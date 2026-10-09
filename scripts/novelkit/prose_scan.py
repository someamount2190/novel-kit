"""prose_scan.py — deterministic prose-smell detector. PURE PYTHON, stdlib only.

This is the writing analogue of blender-kit's failure_scan / godot-kit's preflight:
a check the model CANNOT talk its way past. The model defaults to the most-probable
phrasing — clichés, filter words, adverb-laden tags, telling-not-showing, monotone
sentence rhythm — and then praises the result. This scanner finds those mechanically
and reports line-anchored hits + densities, so revision targets evidence, not vibes.

It does NOT judge story, character, or meaning — that's the cold-read subagent's job
(SOP-07). Treat every flag as a PROMPT TO LOOK, not an automatic delete: an
intentional cliché in dialogue, a deliberate fragment for rhythm, are fine. The
scanner narrows where to look; the eye decides.

Categories (each -> hits with line numbers + a per-1000-word density):
  filter_words     perception verbs that distance the reader from POV
  telling_emotion  emotions named outright instead of dramatised
  said_bookisms    dialogue tags fancier than said/asked, and adverb-tagged tags
  adverbs_ly       -ly adverbs (esp. propping up weak verbs)
  intensifiers     very/really/quite/just/suddenly... empty amplifiers
  cliches          curated overused phrases (extendable via references/cliches/)
  repetition       a distinctive word echoed within a short window
  sentence_openers many consecutive sentences with the same opening word
  rhythm           sentence-length monotony (low variance / long same-length runs)
  passive          be-verb + past participle (heuristic)
  filler           crutch words (that/then/began to/started to/in order to)

Thresholds are tuned to flag the worst ~genre-fiction smells without drowning
literary prose. Tune in THRESHOLDS; they are intentionally explicit.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from . import manuscript as M

# --------------------------------------------------------------------------- data
FILTER_WORDS = {
    # perception/cognition verbs that narrate experience through the POV character
    # ("she saw the man enter" vs the stronger "the man entered"). NOTE: look/looked
    # and watch/watched are deliberately EXCLUDED — they're far more often physical
    # actions ("he looked at the water") than perception filters, so including them
    # buries the real signal. Add them back only for a tight POV-discipline pass.
    "saw", "see", "sees", "seeing", "heard", "hear", "hearing", "listened",
    "felt", "feel", "feeling", "noticed", "notice", "realized", "realised",
    "realize", "wondered", "wonder", "thought", "knew", "know", "seemed",
    "seem", "seems", "decided", "decide", "observed", "observe", "sensed",
    "sense", "smelled", "tasted", "spotted", "noted", "remembered",
}

# emotions stated outright (telling). Paired with a be/feel verb upstream they are
# nearly always tell-not-show.
TELLING_EMOTIONS = {
    "angry", "anger", "sad", "sadness", "happy", "happiness", "afraid", "fear",
    "scared", "nervous", "anxious", "anxiety", "excited", "excitement", "furious",
    "terrified", "terror", "joy", "joyful", "miserable", "depressed", "embarrassed",
    "ashamed", "shame", "jealous", "jealousy", "frustrated", "frustration",
    "confused", "confusion", "worried", "worry", "lonely", "guilty", "guilt",
    "surprised", "shocked", "devastated", "heartbroken", "relieved", "annoyed",
}

# dialogue tags that aren't "said/asked" — said-bookisms. Many are fine occasionally;
# density is what we flag.
SAID_BOOKISMS = {
    "exclaimed", "retorted", "opined", "ejaculated", "interjected", "queried",
    "expostulated", "remarked", "stated", "uttered", "voiced", "articulated",
    "pronounced", "declared", "proclaimed", "announced", "snarled", "growled",
    "hissed", "spat", "barked", "snapped", "purred", "cooed", "chirped",
    "quipped", "mused", "ventured", "offered", "countered", "chuckled",
    "laughed", "smiled", "grinned", "smirked", "sighed", "breathed", "gasped",
    "screamed", "shouted", "yelled", "whispered", "muttered", "murmured",
    "stammered", "stuttered", "demanded", "pleaded", "begged", "wailed",
    "sobbed", "scoffed", "sneered", "groaned", "moaned", "grunted", "huffed",
}
# the ones that are physically impossible to "say" (you can't laugh/smile words)
IMPOSSIBLE_TAGS = {"laughed", "smiled", "grinned", "smirked", "chuckled", "sighed", "breathed"}

INTENSIFIERS = {
    "very", "really", "quite", "rather", "somewhat", "just", "actually",
    "basically", "literally", "simply", "totally", "completely", "absolutely",
    "extremely", "incredibly", "truly", "definitely", "certainly", "suddenly",
    "somehow", "a bit", "a little", "kind of", "sort of", "pretty much",
}

FILLER = {
    "began to", "started to", "in order to", "the fact that", "due to the fact",
    "for all intents", "at this point in time", "each and every", "first and foremost",
    "needless to say", "it goes without saying",
}

# curated cliché phrases — the live list also pulls references/cliches/*.txt if present.
CLICHES = [
    "heart pounded", "heart raced", "heart hammered", "heart skipped a beat",
    "blood ran cold", "blood boiled", "time stood still", "time seemed to slow",
    "breath caught", "caught her breath", "caught his breath", "breath hitched",
    "shiver down her spine", "shiver down his spine", "chill down", "shiver ran",
    "deafening silence", "eerie silence", "pregnant pause", "calm before the storm",
    "little did", "to no avail", "in the nick of time", "against all odds",
    "eyes widened", "eyes narrowed", "eyes went wide", "rolled her eyes",
    "rolled his eyes", "let out a breath", "breath she didn't know",
    "breath he didn't know", "released a breath", "white as a sheet",
    "pale as a ghost", "weak in the knees", "butterflies in her stomach",
    "butterflies in his stomach", "knot in her stomach", "knot in his stomach",
    "lump in her throat", "lump in his throat", "tears welled", "tears streamed",
    "a single tear", "fell to his knees", "fell to her knees", "world came crashing",
    "nodded in agreement", "nodded knowingly", "smiled knowingly", "could feel the",
    "without a second thought", "before she knew it", "before he knew it",
    "as if on cue", "needless to say", "the silence was deafening", "wave of",
    "sent shivers", "ice in her veins", "ice in his veins", "heart in her throat",
    "heart in his throat", "bile rose", "all eyes turned", "you could hear a pin drop",
]

THRESHOLDS = {
    # density = hits per 1000 words. Above target = REVIEW; above 2x = HARD fail.
    "filter_words": 8.0,
    "telling_emotion": 3.0,
    "intensifiers": 8.0,
    "adverbs_ly": 12.0,
    "filler": 2.5,
    # absolute counts / structural
    "repetition_window": 60,     # words; same lemma within this window = echo
    "opener_run": 3,             # >= this many consecutive same-opener sentences
    "rhythm_run": 5,             # >= this many consecutive sentences within +/-2 words
    "rhythm_stdev_min": 4.0,     # whole-scene sentence-length stdev below this = monotone
}

_WORD = re.compile(r"[A-Za-z][A-Za-z'’-]*")
_LY = re.compile(r"\b([A-Za-z]{3,}ly)\b")
_BE = r"(?:is|are|was|were|been|being|be|am)"
_PASSIVE = re.compile(rf"\b{_BE}\b\s+(?:\w+\s+){{0,1}}(\w+ed)\b", re.IGNORECASE)
# legitimate -ly words that aren't adverbs of manner / aren't worth flagging
_LY_OK = {"only", "family", "reply", "supply", "apply", "rely", "july", "italy",
          "ally", "fly", "early", "ugly", "holy", "lonely", "lovely", "likely",
          "daily", "weekly", "monthly", "yearly", "friendly", "lively", "elderly",
          "curly", "silly", "jelly", "belly", "rally", "really"}  # 'really' counted as intensifier


def _line_index(text: str) -> list:
    """char offset -> 1-based line number lookup."""
    offsets = [0]
    for ln in text.split("\n"):
        offsets.append(offsets[-1] + len(ln) + 1)
    return offsets


def _lineno(offsets: list, pos: int) -> int:
    lo, hi = 0, len(offsets) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if offsets[mid + 1] <= pos:
            lo = mid + 1
        else:
            hi = mid
    return lo + 1


def _load_extra_cliches() -> list:
    base = Path(__file__).resolve().parents[2] / "references" / "cliches"
    extra = []
    if base.is_dir():
        for f in base.glob("*.txt"):
            for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
                line = line.strip().lower()
                if line and not line.startswith("#"):
                    extra.append(line)
    return extra


def scan(text: str) -> dict:
    offsets = _line_index(text)
    lower = text.lower()
    words = _WORD.findall(text)
    nwords = len(words) or 1
    k = nwords / 1000.0

    findings: dict = {}

    def add(cat, pos, snippet):
        findings.setdefault(cat, []).append({"line": _lineno(offsets, pos),
                                             "text": snippet.strip()})

    # token-based categories
    for m in _WORD.finditer(text):
        w = m.group(0).lower()
        if w in FILTER_WORDS:
            add("filter_words", m.start(), _ctx(text, m.start()))
        if w in INTENSIFIERS:
            add("intensifiers", m.start(), _ctx(text, m.start()))
        if w in TELLING_EMOTIONS:
            add("telling_emotion", m.start(), _ctx(text, m.start()))

    # multiword intensifiers / filler
    for phrase in INTENSIFIERS | FILLER:
        if " " in phrase:
            for m in re.finditer(re.escape(phrase), lower):
                cat = "intensifiers" if phrase in INTENSIFIERS else "filler"
                add(cat, m.start(), _ctx(text, m.start()))
    for phrase in FILLER:
        if " " in phrase:
            continue
        for m in re.finditer(rf"\b{re.escape(phrase)}\b", lower):
            add("filler", m.start(), _ctx(text, m.start()))

    # -ly adverbs
    for m in _LY.finditer(text):
        w = m.group(1).lower()
        if w in _LY_OK or w in INTENSIFIERS:
            continue
        add("adverbs_ly", m.start(), _ctx(text, m.start()))

    # said-bookisms: a fancy tag adjacent to a quote, OR "said <adverb>ly"
    for m in re.finditer(r'["”]\s*[,.]?\s*(?:\w+\s+){0,2}(\w+)', text):
        tag = m.group(1).lower()
        if tag in SAID_BOOKISMS:
            sev = "impossible-tag" if tag in IMPOSSIBLE_TAGS else "bookism"
            findings.setdefault("said_bookisms", []).append(
                {"line": _lineno(offsets, m.start(1)), "text": _ctx(text, m.start(1)),
                 "kind": sev, "tag": tag})
    for m in re.finditer(r'\b(said|asked|replied)\s+(\w+ly)\b', text, re.IGNORECASE):
        if m.group(2).lower() not in _LY_OK:
            findings.setdefault("said_bookisms", []).append(
                {"line": _lineno(offsets, m.start()), "text": _ctx(text, m.start()),
                 "kind": "adverb-tag", "tag": m.group(2).lower()})

    # clichés
    for phrase in CLICHES + _load_extra_cliches():
        for m in re.finditer(re.escape(phrase), lower):
            add("cliches", m.start(), _ctx(text, m.start()))

    # passive (heuristic)
    for m in _PASSIVE.finditer(text):
        add("passive", m.start(), _ctx(text, m.start()))

    # repetition: distinctive word echoed within window
    findings["repetition"] = _repetition(text, offsets)

    # sentence-level: openers + rhythm
    findings["sentence_openers"] = _openers(text, offsets)
    rhythm = _rhythm(text)

    # ---- assemble report
    counts = {c: len(findings.get(c, [])) for c in
              ["filter_words", "telling_emotion", "said_bookisms", "adverbs_ly",
               "intensifiers", "cliches", "filler", "passive", "repetition",
               "sentence_openers"]}
    densities = {c: round(counts[c] / k, 1) for c in
                 ["filter_words", "telling_emotion", "adverbs_ly", "intensifiers",
                  "filler"]}

    # Two tiers: HARD flags fail the gate; REVIEW flags are "go look" hints that a
    # human/eye should judge (a couple of filter words in good prose is normal).
    hard, review = [], []
    for c in ("filter_words", "telling_emotion", "intensifiers", "adverbs_ly", "filler"):
        target = THRESHOLDS[c]
        d = densities[c]
        if d > 2 * target:
            hard.append(f"{c}: {d}/1k words (>2x target {target}) — crutch-level")
        elif d > target:
            review.append(f"{c}: {d}/1k words (target <= {target})")

    if counts["cliches"]:
        hard.append(f"cliches: {counts['cliches']} hit(s) — see list")
    impossible = [f for f in findings.get("said_bookisms", []) if f.get("kind") == "impossible-tag"]
    if impossible:
        hard.append(f"impossible dialogue tags (you can't laugh/smile words): {len(impossible)}")
    bookisms = counts["said_bookisms"] - len(impossible)
    if bookisms > 0:
        (review if bookisms <= 2 else hard).append(
            f"said-bookisms / adverb tags: {bookisms}")
    if findings["sentence_openers"]:
        hard.append(f"repeated sentence openers: {len(findings['sentence_openers'])} run(s)")
    if rhythm["monotone"]:
        hard.append(f"sentence rhythm monotone (stdev {rhythm['stdev']} < "
                    f"{THRESHOLDS['rhythm_stdev_min']})")
    if rhythm["runs"]:
        review.append(f"same-length sentence runs: {len(rhythm['runs'])}")

    return {
        "words": nwords,
        "counts": counts,
        "densities": densities,
        "rhythm": rhythm,
        "flags": hard,            # back-compat: hard flags are "the flags"
        "hard_flags": hard,
        "review_flags": review,
        "findings": findings,
        "passed": not hard,
    }


def _ctx(text: str, pos: int, width: int = 38) -> str:
    a = max(0, pos - width)
    b = min(len(text), pos + width)
    return ("…" if a else "") + text[a:b].replace("\n", " ") + ("…" if b < len(text) else "")


def _repetition(text: str, offsets: list) -> list:
    STOP = set("""the a an and or but of to in on at for with as is was were be been
        being it its it's he she they them his her their you your i me my we our that
        this these those there here not no so do did had has have will would could
        should can may might must from by into out up down over under then than too
        very just only also even still back about after before when while where which
        who whom what why how all any some more most other into onto off""".split())
    toks = [(m.group(0).lower(), m.start()) for m in _WORD.finditer(text)]
    out = []
    win = THRESHOLDS["repetition_window"]
    last = {}
    seq = [w for w, _ in toks]
    for i, (w, pos) in enumerate(toks):
        if len(w) < 5 or w in STOP:
            continue
        if w in last and (i - last[w][0]) <= win:
            out.append({"line": _lineno(offsets, pos), "word": w,
                        "gap_words": i - last[w][0],
                        "text": _ctx(text, pos)})
        last[w] = (i, pos)
    return out


def _openers(text: str, offsets: list) -> list:
    sents = M.sentences(text)
    out = []
    run_word = None
    run = []
    pos_cursor = 0
    for s in sents:
        mw = _WORD.search(s)
        first = mw.group(0).lower() if mw else ""
        pos = text.find(s[:20], pos_cursor) if s else pos_cursor
        if pos < 0:
            pos = pos_cursor
        pos_cursor = pos + 1
        if first == run_word and first:
            run.append((s, pos))
        else:
            if len(run) >= THRESHOLDS["opener_run"]:
                out.append({"opener": run_word, "count": len(run),
                            "line": _lineno(offsets, run[0][1])})
            run_word = first
            run = [(s, pos)]
    if len(run) >= THRESHOLDS["opener_run"]:
        out.append({"opener": run_word, "count": len(run),
                    "line": _lineno(offsets, run[0][1])})
    return out


def _rhythm(text: str) -> dict:
    sents = M.sentences(text)
    lens = [len(_WORD.findall(s)) for s in sents]
    if len(lens) < 4:
        return {"stdev": None, "monotone": False, "runs": [], "n": len(lens)}
    mean = sum(lens) / len(lens)
    stdev = (sum((x - mean) ** 2 for x in lens) / len(lens)) ** 0.5
    runs = []
    i = 0
    while i < len(lens):
        j = i
        while j + 1 < len(lens) and abs(lens[j + 1] - lens[i]) <= 2:
            j += 1
        if j - i + 1 >= THRESHOLDS["rhythm_run"]:
            runs.append({"start_sentence": i + 1, "length": j - i + 1,
                         "approx_words": lens[i]})
        i = j + 1
    return {"stdev": round(stdev, 1), "monotone": stdev < THRESHOLDS["rhythm_stdev_min"],
            "runs": runs, "n": len(lens), "mean": round(mean, 1)}


def format_report(rep: dict, show_hits: int = 6) -> str:
    L = []
    L.append(f"PROSE SCAN — {rep['words']:,} words")
    L.append("  densities (per 1k words):")
    for c, d in rep["densities"].items():
        tgt = THRESHOLDS.get(c)
        mark = "  ⚠" if (tgt and d > tgt) else ""
        L.append(f"      {c:<16} {d:>5}{mark}")
    r = rep["rhythm"]
    if r.get("stdev") is not None:
        L.append(f"  rhythm: mean {r['mean']}w  stdev {r['stdev']}"
                 f"{'  ⚠ monotone' if r['monotone'] else ''}")
    L.append("")
    if rep["hard_flags"]:
        L.append("  HARD FLAGS (fix before shipping):")
        for f in rep["hard_flags"]:
            L.append(f"    ✗ {f}")
    else:
        L.append("  ✓ no hard prose-smell flags (still: cold-read it — SOP-07)")
    if rep["review_flags"]:
        L.append("  REVIEW (go look — may be fine in context):")
        for f in rep["review_flags"]:
            L.append(f"    • {f}")
    # sample hits for the worst categories
    L.append("")
    L.append("  sample hits:")
    for cat in ["cliches", "said_bookisms", "filter_words", "telling_emotion",
                "repetition", "sentence_openers", "passive"]:
        hits = rep["findings"].get(cat) or []
        if not hits:
            continue
        L.append(f"    [{cat}] ({len(hits)})")
        for h in hits[:show_hits]:
            loc = f"L{h.get('line')}"
            extra = h.get("tag") or h.get("word") or h.get("opener") or ""
            extra = f" «{extra}»" if extra else ""
            L.append(f"        {loc}{extra}: {h.get('text','')}")
        if len(hits) > show_hits:
            L.append(f"        … +{len(hits) - show_hits} more")
    return "\n".join(L)


def _cli(argv: list) -> int:
    if not argv:
        print("usage: python -m novelkit.prose_scan <file> [--json] [--scene N]")
        return 2
    path = argv[0]
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    if "--scene" in argv:
        n = int(argv[argv.index("--scene") + 1])
        ms = M.parse(text, path)
        sc = next((s for s in ms.scenes if s.index + 1 == n), None)
        if not sc:
            print(f"no scene {n} (have {len(ms.scenes)})")
            return 2
        text = sc.text
    rep = scan(text)
    if "--json" in argv:
        import json
        print(json.dumps(rep, ensure_ascii=False, indent=2))
    else:
        print(format_report(rep))
    return 0 if rep["passed"] else 1


if __name__ == "__main__":
    sys.exit(_cli(sys.argv[1:]))
