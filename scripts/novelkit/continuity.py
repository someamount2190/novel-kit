"""continuity.py — validate a manuscript against the story bible canon. PURE PYTHON.

The deterministic guard against the model's worst long-form failure: contradicting
its own established facts across tens of thousands of words. Checks performed:

  1. ATTRIBUTE CONTRADICTION — for each character with a checkable attribute
     (eyes/hair colour), find sentences naming that character + the attribute noun
     + a colour from the vocab; if the colour disagrees with canon, FLAG with line.
  2. NAME DRIFT — capitalised tokens in the prose that are a near-miss (edit
     distance 1-2) of a canonical character name/alias but aren't themselves canon:
     likely misspellings (Mara -> Marra, Vance -> Vince).
  3. FORBIDDEN — any FORBIDDEN canon string appearing in the prose.
  4. LEDGER COVERAGE — every SETUP must have its keywords appear in the prose; a
     setup with no payoff text, or a payoff whose keywords never appear, is a
     dangling promise (Chekhov's gun that never fires) or an unplanted payoff.

These are HEURISTICS that surface suspects — the eye confirms. False positives are
expected (a second grey-eyed character, an intentional rename). Never auto-edit;
report line-anchored suspects for review.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from . import bible as B
from . import manuscript as M

_WORD = re.compile(r"[A-Za-z][A-Za-z'’-]*")
_CAP = re.compile(r"\b([A-Z][a-z]{2,})\b")
_STOP_CAPS = set("""The A An And But Or So He She They It We You I His Her Their Its
    Then There Here When Where What Why How That This These Those Now Yet As If Of
    To In On At For With From By Into Out Up Down Over Mr Mrs Ms Dr Sir Lady Lord
    Chapter Some Someone Something Could Would Should Will Shall Can May Might Must
    See Saw Look Looked Still Just Even Once Every Each Many Most Both Either Neither
    Nobody Nothing Maybe Perhaps Because Before After While Until Since Though Although
    No Yes Sorry Not Nor All Any Two One First Last Next Another Other Such About
    Said Asked Told Yet Soon Later Always Never Often Well Like Only Almost""".split())


def _levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    if abs(len(a) - len(b)) > 2:
        return 3
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def _line_index(text: str):
    offs = [0]
    for ln in text.split("\n"):
        offs.append(offs[-1] + len(ln) + 1)
    return offs


def _lineno(offs, pos):
    lo, hi = 0, len(offs) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if offs[mid + 1] <= pos:
            lo = mid + 1
        else:
            hi = mid
    return lo + 1


def _infer_genders(sents: list, bib: B.Bible) -> dict:
    """name -> 'F' | 'M' | 'X'. Explicit bible 'pronouns'/'gender' wins; otherwise
    majority of she/her vs he/him in sentences that name the character."""
    out = {}
    fem = {"she", "her", "hers"}
    masc = {"he", "him", "his"}
    for c in bib.characters.values():
        decl = (c.attrs.get("pronouns") or c.attrs.get("gender") or "").lower()
        if any(p in decl for p in ("she", "her", "female", "woman", "f")):
            out[c.name] = "F"
            continue
        if any(p in decl for p in ("he", "him", "male", "man", "m")):
            out[c.name] = "M"
            continue
        f = m = 0
        names = [n.lower() for n in c.all_names]
        for s in sents:
            sl = s.lower()
            if any(re.search(rf"\b{re.escape(n)}\b", sl) for n in names):
                toks = set(_WORD.findall(sl))
                f += len(toks & fem)
                m += len(toks & masc)
        out[c.name] = "F" if f > m else "M" if m > f else "X"
    return out


def check(text: str, bib: B.Bible) -> dict:
    offs = _line_index(text)
    sents = M.sentences(text)
    findings = {"attribute": [], "name_drift": [], "forbidden": [], "ledger": []}

    # locate each sentence's char offset for line numbers
    cursor = 0
    sent_pos = []
    for s in sents:
        p = text.find(s[:24], cursor) if s else cursor
        if p < 0:
            p = cursor
        sent_pos.append(p)
        cursor = p + 1

    # 1. attribute contradictions.
    # Walk sentences once, tracking the last NAMED character (the focal POV). When a
    # sentence describes an attribute (eyes/hair) + colour, attribute it to the
    # character named IN that sentence (high confidence) or, failing that, to the
    # last-named character if this sentence opens with a pronoun (her/his/their) —
    # eye/hair colour is usually given via pronoun ("Her green eyes...").
    norm = lambda S: {("grey" if x == "gray" else x) for x in S}
    char_canon = {}  # name -> {attr -> set(colors)}
    for c in bib.characters.values():
        for attr in B.CHECKABLE_ATTRS:
            canon = c.attrs.get(attr)
            if canon:
                cc = {w for w in _WORD.findall(canon.lower()) if w in B.COLORS}
                if cc:
                    char_canon.setdefault(c.name, {})[attr] = (canon, cc)

    # Infer each character's gender (for pronoun resolution): explicit bible field
    # 'pronouns'/'gender' wins; else count she/her vs he/him in naming sentences.
    genders = _infer_genders(sents, bib)

    # leading pronoun -> gender bucket; F=she/her, M=he/his, X=they/their (any)
    _PRON = re.compile(r"^\s*(her|hers|she|his|he|him|their|theirs|they)\b", re.IGNORECASE)
    PG = {"her": "F", "hers": "F", "she": "F", "his": "M", "he": "M", "him": "M",
          "their": "X", "theirs": "X", "they": "X"}
    # most-recently-named character per gender bucket, valid for the whole scene
    recent = {"F": None, "M": None, "X": None}
    for si, s in enumerate(sents):
        sl = s.lower()
        named_here = None
        for c in bib.characters.values():
            if any(re.search(rf"\b{re.escape(n.lower())}\b", sl) for n in c.all_names):
                named_here = c.name
                g = genders.get(c.name, "X")
                recent[g] = c.name
                recent["X"] = c.name      # any-gender bucket = last named, period
                break
        owner, via_pron = named_here, False
        if owner is None:
            pm = _PRON.match(s)
            if pm:
                bucket = PG[pm.group(1).lower()]
                cand = recent.get(bucket)
                if cand is None:
                    # fall back to the last-named character of ANY gender, unless they
                    # are KNOWN to be the opposite gender of this pronoun.
                    fallback = recent["X"]
                    opp = {"F": "M", "M": "F"}.get(bucket)
                    if fallback and genders.get(fallback) != opp:
                        cand = fallback
                if cand:
                    owner, via_pron = cand, True
        if owner is None or owner not in char_canon:
            continue
        found = {w for w in _WORD.findall(sl) if w in B.COLORS}
        if not found:
            continue
        for attr, (nouns, _) in B.CHECKABLE_ATTRS.items():
            spec = char_canon[owner].get(attr)
            if not spec:
                continue
            canon_str, canon_colors = spec
            if not any(re.search(rf"\b{re.escape(noun)}\b", sl) for noun in nouns):
                continue
            if not (norm(found) & norm(canon_colors)):
                findings["attribute"].append({
                    "line": _lineno(offs, sent_pos[si]),
                    "character": owner, "attr": attr,
                    "canon": canon_str, "found": sorted(found),
                    "via_pronoun": via_pron,
                    "text": s.strip()[:120]})

    # 2. name drift
    canon_names = {}
    for c in bib.characters.values():
        for n in c.all_names:
            for tok in n.split():
                if len(tok) >= 3 and tok[0].isupper():
                    canon_names[tok.lower()] = (c.name, tok)
    seen = {}
    for m in _CAP.finditer(text):
        tok = m.group(1)
        if tok in _STOP_CAPS:
            continue
        low = tok.lower()
        if low in canon_names:
            continue
        for cl, (cname, ctok) in canon_names.items():
            d = _levenshtein(low, cl)
            if 1 <= d <= 2 and abs(len(low) - len(cl)) <= 2:
                key = (tok, ctok)
                if key not in seen:
                    seen[key] = True
                    findings["name_drift"].append({
                        "line": _lineno(offs, m.start()),
                        "token": tok, "near": ctok, "character": cname,
                        "distance": d, "text": _ctx(text, m.start())})
                break

    # 3. forbidden
    low = text.lower()
    for f in bib.forbidden:
        if f.startswith("#"):
            continue
        needle = f.strip().strip('"').lower()
        # support  the word "okay"  phrasing
        m2 = re.search(r'"([^"]+)"', f)
        if m2:
            needle = m2.group(1).lower()
        if not needle:
            continue
        for m in re.finditer(rf"\b{re.escape(needle)}\b", low):
            findings["forbidden"].append({
                "line": _lineno(offs, m.start()), "forbidden": needle,
                "text": _ctx(text, m.start())})

    # 4. ledger coverage
    for sp in bib.ledger:
        skw = _keywords(sp.setup)
        pkw = _keywords(sp.payoff)
        setup_present = _present(skw, low)
        payoff_present = _present(pkw, low) if pkw else False
        status = "ok"
        if skw and not setup_present:
            status = "setup-missing"
        elif not sp.payoff:
            status = "no-payoff-declared"
        elif setup_present and not payoff_present:
            status = "PAYOFF-MISSING (dangling setup / Chekhov's gun unfired)"
        elif payoff_present and not setup_present:
            status = "payoff-unplanted (setup never appears)"
        if status != "ok":
            findings["ledger"].append({"raw": sp.raw, "status": status,
                                       "setup_kw": skw, "payoff_kw": pkw})

    total = sum(len(v) for v in findings.values())
    return {"findings": findings, "total": total,
            "passed": len(findings["attribute"]) == 0
                      and len(findings["forbidden"]) == 0
                      and not [l for l in findings["ledger"]
                               if "MISSING" in l["status"] or "unplanted" in l["status"]]}


def _keywords(phrase: str):
    STOP = set("the a an of to in on at and or but with that this for is are was "
               "were be ch chapter @".split())
    return [w.lower() for w in re.findall(r"[A-Za-z]{3,}", phrase)
            if w.lower() not in STOP][:5]


def _present(kws, low):
    if not kws:
        return False
    hits = sum(1 for k in kws if k in low)
    return hits >= max(1, len(kws) // 2)


def _ctx(text, pos, w=34):
    a, b = max(0, pos - w), min(len(text), pos + w)
    return ("…" if a else "") + text[a:b].replace("\n", " ") + ("…" if b < len(text) else "")


def format_report(rep: dict) -> str:
    f = rep["findings"]
    L = [f"CONTINUITY CHECK — {rep['total']} suspect(s)"]
    if rep["passed"] and rep["total"] == 0:
        L.append("  ✓ no contradictions, name drift, forbidden terms, or dangling setups")
        return "\n".join(L)
    if f["attribute"]:
        L.append("  ATTRIBUTE CONTRADICTIONS (canon vs prose):")
        for h in f["attribute"]:
            L.append(f"    ✗ L{h['line']} {h['character']}.{h['attr']}: canon={h['canon']} "
                     f"but prose says {h['found']}  | {h['text']}")
    if f["forbidden"]:
        L.append("  FORBIDDEN TERMS:")
        for h in f["forbidden"]:
            L.append(f"    ✗ L{h['line']} «{h['forbidden']}»: {h['text']}")
    if f["name_drift"]:
        L.append("  NAME DRIFT (possible misspellings — confirm by eye):")
        for h in f["name_drift"]:
            L.append(f"    • L{h['line']} «{h['token']}» ~ {h['near']} "
                     f"({h['character']}, dist {h['distance']}): {h['text']}")
    if f["ledger"]:
        L.append("  SETUP/PAYOFF LEDGER:")
        for h in f["ledger"]:
            L.append(f"    • [{h['status']}] {h['raw']}")
    return "\n".join(L)


def _cli(argv):
    if len(argv) < 2:
        print("usage: python -m novelkit.continuity <manuscript> <bible.md> [--json]")
        return 2
    text = Path(argv[0]).read_text(encoding="utf-8", errors="replace")
    bib = B.load(argv[1])
    rep = check(text, bib)
    if "--json" in argv:
        import json
        print(json.dumps(rep, ensure_ascii=False, indent=2))
    else:
        print(format_report(rep))
    return 0 if rep["passed"] else 1


if __name__ == "__main__":
    sys.exit(_cli(sys.argv[1:]))
