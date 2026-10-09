"""flags.py — narrative FLAGS: typed, character-attached signals with a lifecycle.
PURE PYTHON.

Researched 2026-06-22 (TV Tropes "Event Flag"; CBR shonen death-flags; VN/gal-game
flag systems; JeremyVarner/ResetEra on death-flag cliché). A "flag" comes from game/
visual-novel programming: a condition that, once RAISED, triggers a later payoff. In
fiction it's a planted signal with a lifecycle:  raised → paid (triggered) | broken
(deliberately subverted).  Types this audits specially:

  • introduction — how a character ENTERS signals their role/importance and plants
    what they're for; should pay off later (the intro that returns).
  • romance — an event that "sparks the relationship"; should escalate and PAY (the
    union/HFN). A raised romance flag that evaporates cheats the reader.
  • death — foreshadows a death (the after-the-war speech, the family photo, the last
    mission). Must be RAISED BEFORE the death. CLICHÉ-AWARE: a death flag paid
    straight telegraphs — advise subtlety or subversion (but note over-subversion is
    itself a cliché now, so it's an advisory, not a failure).

Declared in the plan under `## FLAGS`, one per line:
    - <type> | <character> | raised @<scene> | (paid|broken) @<scene> — <note>
e.g.
    - introduction | Toma | raised @1 | paid @8 — the overlooked boy is the one who matters
    - death | Sera | raised @6 | broken @8 — heavily flagged, SURVIVES (deliberate)

AUDIT: a raised flag with neither paid nor broken is DANGLING (a promise the reader
clocked and you didn't honour). A payoff at/before the raise is mis-ordered
(foreshadow must precede). Death flags get the telegraph advisory.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from . import structure as S
from . import bible as B

KNOWN_TYPES = {"introduction", "romance", "death", "betrayal", "power-up", "powerup",
               "redemption", "foreshadow", "reveal", "rivalry"}
_AT = re.compile(r"@\s*(?:scene\s*|s)?(\d+)", re.IGNORECASE)
_STATUS = re.compile(r"\b(paid|broken|triggered|resolved|subverted)\b", re.IGNORECASE)


def parse_flags(plan_text: str) -> list:
    m = re.search(r"^##\s+flags?.*$", plan_text, re.IGNORECASE | re.MULTILINE)
    if not m:
        return []
    body = plan_text[m.end():]
    nxt = re.search(r"^##\s+\S", body, re.MULTILINE)
    if nxt:
        body = body[:nxt.start()]

    flags = []
    for ln in body.splitlines():
        s = ln.strip()
        if not s.startswith(("-", "*")):
            continue
        s = s.lstrip("-* ").strip()
        if not s or s.startswith("<"):   # skip scaffold placeholder
            continue
        note = ""
        if "—" in s:
            s, note = s.split("—", 1)
        elif " - " in s:
            s, note = s.split(" - ", 1)
        parts = [p.strip() for p in s.split("|")]
        ftype = parts[0].lower() if parts else ""
        character = parts[1] if len(parts) > 1 else ""
        raised = paid = None
        status = None  # 'paid' | 'broken'
        for seg in parts[2:]:
            seg_l = seg.lower()
            at = _AT.search(seg)
            n = int(at.group(1)) if at else None
            if "rais" in seg_l:
                raised = n
            else:
                st = _STATUS.search(seg_l)
                if st:
                    word = st.group(1).lower()
                    status = "broken" if word in ("broken", "subverted") else "paid"
                    paid = n
        flags.append({"type": ftype, "character": character, "raised": raised,
                      "status": status, "paid": paid, "note": note.strip(), "raw": ln.strip()})
    return flags


def audit(plan_text: str, bib: B.Bible) -> dict:
    rows = S.parse_ledger(plan_text)
    n_scenes = len(rows)
    flags = parse_flags(plan_text)
    known = {n.lower() for c in bib.characters.values() for n in c.all_names}

    issues = {"dangling": [], "ordering": [], "unknown_char": [], "unplaced": [],
              "unknown_type": []}
    advisories = []

    for f in flags:
        label = f"{f['type']} flag ({f['character']})"
        # character known? (allow "A & B" / "A and B")
        chars = re.split(r"\s*(?:&|and|,|/)\s*", f["character"])
        if f["character"] and not any(
                any(c.strip().lower() in kn or kn in c.strip().lower() or c.strip().lower() == kn
                    for kn in known) for c in chars if c.strip()):
            issues["unknown_char"].append({"flag": label, "raw": f["raw"]})
        if f["type"] not in KNOWN_TYPES:
            issues["unknown_type"].append({"flag": label, "type": f["type"]})
        if f["raised"] is None:
            issues["unplaced"].append({"flag": label, "problem": "no 'raised @scene'"})
            continue
        if not (1 <= f["raised"] <= n_scenes) and n_scenes:
            issues["unplaced"].append({"flag": label,
                                       "problem": f"raised @{f['raised']} out of range (1..{n_scenes})"})
        if f["status"] is None:
            issues["dangling"].append(
                {"flag": label, "raised": f["raised"],
                 "problem": "raised but never PAID or marked BROKEN — a promise left "
                            "hanging (the reader clocked this flag)"})
        else:
            if f["paid"] is not None and f["raised"] is not None and f["paid"] <= f["raised"]:
                issues["ordering"].append(
                    {"flag": label,
                     "problem": f"{f['status']} @{f['paid']} is not AFTER raised "
                                f"@{f['raised']} — foreshadow must precede the payoff"})
            # death-flag telegraph advisory
            if f["type"] == "death" and f["status"] == "paid":
                advisories.append(
                    f"{label}: paid straight — death flags TELEGRAPH. Make the tell "
                    f"subtle, or subvert (but don't over-subvert; that's now a cliché too).")
            if f["type"] == "romance" and f["status"] == "broken":
                advisories.append(
                    f"{label}: a broken romance flag denies the genre's payoff — "
                    f"intentional? (fine in tragedy; fatal in romance).")

    total = sum(len(v) for v in issues.values())
    return {"flags": flags, "n_flags": len(flags), "issues": issues,
            "advisories": advisories, "total": total,
            "passed": len(issues["dangling"]) == 0 and len(issues["ordering"]) == 0
                      and len(issues["unknown_char"]) == 0 and len(issues["unplaced"]) == 0}


def format_report(rep: dict) -> str:
    L = [f"FLAGS — {rep['n_flags']} declared"]
    if rep["n_flags"] == 0:
        L.append("  (no flags declared — optional. Introduction/romance/death flags are "
                 "a strong way to plant & pay character beats; see references/flags.md.)")
        return "\n".join(L)
    for f in rep["flags"]:
        state = (f["status"] or "DANGLING").upper()
        when = (f"raised @{f['raised']}" if f["raised"] else "unplaced")
        pay = (f" → {f['status']} @{f['paid']}" if f["status"] else "")
        L.append(f"  • [{f['type']}] {f['character']}: {when}{pay}  [{state}]")
    iss = rep["issues"]
    if rep["passed"] and not rep["advisories"]:
        L.append("  ✓ every flag is placed, owned, ordered, and paid-or-broken")
        return "\n".join(L)
    for key, items in iss.items():
        for it in items:
            L.append(f"  ✗ {it.get('flag','')}: {it.get('problem', it.get('type',''))}  ({key})")
    for a in rep["advisories"]:
        L.append(f"  ⚠ {a}")
    return "\n".join(L)


def _cli(argv):
    if len(argv) < 2:
        print("usage: python -m novelkit.flags <plan.md> <bible.md> [--json]")
        return 2
    plan_text = Path(argv[0]).read_text(encoding="utf-8", errors="replace")
    bib = B.load(argv[1])
    rep = audit(plan_text, bib)
    if "--json" in argv:
        import json
        print(json.dumps(rep, ensure_ascii=False, indent=2))
    else:
        print(format_report(rep))
    return 0 if rep["passed"] else 1


if __name__ == "__main__":
    sys.exit(_cli(sys.argv[1:]))
