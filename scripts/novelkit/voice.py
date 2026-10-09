"""voice.py — the VOICE DISTINCTIVENESS field. PURE PYTHON (+ cold-read harness).

character.py already guards two things about a single voice: the BASELINE (a voice
signature must be declared) and FIDELITY (does X speak like X / never break X's
rules). It does NOT guard the thing the model gets most wrong across a cast: every
character ends up speaking in the SAME default register — the author's. Dialogue is
interchangeable; strip the tags and you can't tell who's talking. A distinct voice
falls out of a distinct PERSONALITY (a clipped, guarded ex-soldier and a hedging,
over-formal bureaucrat cannot share a sentence rhythm). Two guards here:

  • distinctiveness_gate(bible) — DESIGN time. Refuses a cast whose DECLARED `voice`
    fields are generic ("speaks normally") or near-duplicates of each other. If two
    characters' voice signatures are interchangeable on paper, their dialogue will be
    too. Deterministic; reliable; contributes to the report's pass/fail.
  • voiceprints(scene, bible) — PROSE time. Attributes dialogue to speakers (by name
    tags), fingerprints each speaker's lines on measurable axes (sentence length,
    contractions, hedges, questions, formality, profanity), and flags speakers whose
    fingerprints are metrically INDISTINGUISHABLE. Attribution is heuristic, so this
    is a REVIEW diagnostic — a floor that catches everyone-sounds-the-same, not a
    judge of whether the voices are GOOD. That verdict is the cold read (SOP-13).

prose_scan punishes too-much and texture punishes too-little; voice punishes
too-SAME. The eye still decides quality — distinct-on-metrics is necessary, not
sufficient.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from . import bible as B
from . import character as C
from . import manuscript as M

# ---- DESIGN: declared-voice distinctiveness --------------------------------

# words that carry no distinguishing information in a voice line
_VOICE_STOP = {
    "a", "an", "the", "and", "or", "but", "of", "to", "in", "on", "with", "his",
    "her", "their", "its", "they", "she", "he", "it", "is", "are", "be", "very",
    "quite", "rather", "always", "never", "often", "sometimes", "when", "that",
    "this", "what", "who", "you", "i", "me", "my", "speak", "speaks", "speaking",
    "talk", "talks", "talking", "say", "says", "saying", "said", "voice", "tone",
    "use", "uses", "using", "word", "words", "way", "style", "manner", "tends",
    "tend", "like", "as", "for", "into", "behind", "under", "language", "lot",
}
# descriptors that don't actually distinguish anyone (a "generic" voice)
_GENERIC = {
    "normal", "normally", "casual", "casually", "friendly", "average", "ordinary",
    "plain", "standard", "neutral", "regular", "natural", "naturally", "polite",
    "nice", "calm", "clear", "simple", "conversational", "everyday", "fine",
}
_TOKEN = re.compile(r"[a-z][a-z'\-]+")


def voice_tokens(voice: str) -> set:
    """Content tokens of a declared voice line — what actually distinguishes it."""
    toks = {t for t in _TOKEN.findall((voice or "").lower())
            if t not in _VOICE_STOP and len(t) > 2}
    return toks


def _jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def distinctiveness_gate(bib: B.Bible, dup_threshold: float = 0.6) -> dict:
    """Are the major characters' DECLARED voices non-generic and mutually distinct?"""
    majors = [c for c in bib.characters.values() if C.is_major(c)]
    profiles = []
    generic = []
    for c in majors:
        voice = (c.attrs.get("voice") or "").strip()
        toks = voice_tokens(voice)
        distinguishing = toks - _GENERIC
        if not voice:
            generic.append({"name": c.name, "why": "no voice declared"})
        elif len(distinguishing) < 2:
            generic.append({"name": c.name,
                            "why": f"too generic — only {sorted(toks) or 'no'} content marker(s)"})
        profiles.append((c.name, toks))

    collisions = []
    for i in range(len(profiles)):
        for j in range(i + 1, len(profiles)):
            n1, t1 = profiles[i]
            n2, t2 = profiles[j]
            sim = _jaccard(t1, t2)
            if sim >= dup_threshold:
                collisions.append({"pair": (n1, n2), "similarity": round(sim, 2),
                                   "shared": sorted(t1 & t2)})

    passed = not generic and not collisions
    return {"passed": passed, "majors": len(majors),
            "generic": generic, "collisions": collisions}


# ---- PROSE: dialogue attribution + voiceprints -----------------------------

_QUOTE = re.compile(r'["“]([^"”]{2,})["”]')
_SPEECH_VERB = (r"said|says|asked|asks|replied|replies|answered|answers|whispered|"
                r"shouted|muttered|murmured|called|growled|snapped|added|continued|"
                r"began|cried|breathed|demanded|offered|admitted|told|hissed|urged|"
                r"warned|repeated|insisted|countered|sighed|laughed")
CONTRACTIONS = re.compile(
    r"\b\w+(?:'|’)(?:t|s|re|ve|ll|d|m)\b", re.IGNORECASE)
HEDGES = {"well", "maybe", "perhaps", "sort", "kind", "just", "actually", "guess",
          "suppose", "probably", "really", "mean", "like", "um", "uh", "anyway",
          "honestly", "basically"}


def _name_in(window: str, bib: B.Bible):
    """First character whose name/alias word appears in `window`."""
    low = window.lower()
    best = None
    best_pos = len(low) + 1
    for c in bib.characters.values():
        for n in c.all_names:
            for w in n.lower().split():
                if len(w) < 3:
                    continue
                m = re.search(rf"\b{re.escape(w)}\b", low)
                if m and m.start() < best_pos:
                    best, best_pos = c, m.start()
    return best


def _speaker_of_paragraph(tag_text: str, bib: B.Bible):
    """Who speaks a paragraph, given its narrative (non-quoted) text. Prefer a name
    adjacent to a speech verb ('Mara said'); fall back to any known name in the tag."""
    low = tag_text.lower()
    for m in re.finditer(rf"\b(?:{_SPEECH_VERB})\b", low):
        win = tag_text[max(0, m.start() - 30):m.end() + 30]
        who = _name_in(win, bib)
        if who:
            return who
    return _name_in(tag_text, bib)


def attribute(text: str, bib: B.Bible) -> dict:
    """Map character.name -> list of their dialogue spans, by the fiction convention
    that a paragraph belongs to ONE speaker: find the speaker from the paragraph's
    speech tag (or a known name in it) and attribute ALL its quotes to them. A
    paragraph whose speaker can't be identified contributes to 'unknown'. Heuristic —
    confirm speakers by eye. Returns {name: [spans], '_unknown': int}."""
    out, unknown = {}, 0
    for para in re.split(r"\n\s*\n", text):
        spans = [m.group(1).strip() for m in _QUOTE.finditer(para)]
        if not spans:
            continue
        tag_text = _QUOTE.sub(" ", para)   # narrative outside the quotes
        who = _speaker_of_paragraph(tag_text, bib)
        if who:
            out.setdefault(who.name, []).extend(spans)
        else:
            unknown += len(spans)
    out["_unknown"] = unknown
    return out


def fingerprint(spans: list) -> dict:
    """Measurable voiceprint over a speaker's concatenated dialogue."""
    text = " ".join(spans)
    words = M.word_list(text)
    n = len(words) or 1
    # each span is its own utterance — split each into sentences so a span boundary
    # never fuses two lines into one giant "sentence".
    sents = [s for span in spans for s in (M.sentences(span) or [span])] or spans
    slens = [len(M.word_list(s)) for s in sents] or [0]
    mean_len = sum(slens) / len(slens)
    contractions = len(CONTRACTIONS.findall(text))
    hedges = sum(1 for w in words if w.lower() in HEDGES)
    questions = sum(1 for s in sents if s.rstrip().endswith("?"))
    exclaims = sum(1 for s in sents if s.rstrip().endswith("!"))
    profanity = sorted({w.lower() for w in words if w.lower() in C.PROFANITY})
    mean_word_len = sum(len(w) for w in words) / n
    return {
        "lines": len(spans), "words": len(words),
        "mean_len": round(mean_len, 1),
        "contraction_rate": round(100 * contractions / n, 1),
        "hedge_rate": round(100 * hedges / n, 1),
        "question_rate": round(100 * questions / max(1, len(sents)), 0),
        "exclaim_rate": round(100 * exclaims / max(1, len(sents)), 0),
        "formality": round(mean_word_len, 2),
        "profanity": profanity,
    }


# per-axis "one full step of difference" — used to normalise the fingerprint
# distance so axes on different scales are comparable.
_AXES = {
    "mean_len": 6.0,            # words per sentence
    "contraction_rate": 5.0,    # per 100 words
    "hedge_rate": 4.0,          # per 100 words
    "formality": 0.6,           # mean chars/word
    "question_rate": 30.0,      # %
    "exclaim_rate": 30.0,       # %
}
# two speakers closer than this in normalised fingerprint space read as one voice.
_SIM_THRESHOLD = 2.0


def voice_distance(a: dict, b: dict) -> float:
    """Normalised Euclidean distance between two voiceprints — small = same voice."""
    total = 0.0
    for k, scale in _AXES.items():
        total += ((a[k] - b[k]) / scale) ** 2
    return total ** 0.5


# minimum dialogue before a speaker's fingerprint is trustworthy
_MIN_WORDS = 20
_MIN_LINES = 2


def voiceprints(text: str, bib: B.Bible) -> dict:
    attr = attribute(text, bib)
    unknown = attr.pop("_unknown", 0)
    speakers = {}
    for name, spans in attr.items():
        fp = fingerprint(spans)
        fp["enough"] = fp["words"] >= _MIN_WORDS and fp["lines"] >= _MIN_LINES
        speakers[name] = fp
    # collisions among speakers with enough dialogue + near-identical fingerprints
    gradable = [(n, fp) for n, fp in speakers.items() if fp["enough"]]
    collisions = []
    for i in range(len(gradable)):
        for j in range(i + 1, len(gradable)):
            n1, f1 = gradable[i]
            n2, f2 = gradable[j]
            d = voice_distance(f1, f2)
            if d < _SIM_THRESHOLD:
                collisions.append({"pair": (n1, n2), "distance": round(d, 2)})
    return {"speakers": speakers, "unknown": unknown, "collisions": collisions,
            "gradable": [n for n, _ in gradable]}


# ---- cold-read harness (the GOOD judgement, per SOP-13) --------------------
RUBRIC = """You are a DIALOGUE DISTINCTIVENESS auditor. Below are the voice
signatures of a story's characters and a scene of their dialogue. Judge ONE thing:
could a reader tell WHO IS SPEAKING with the dialogue tags removed? A distinct voice
comes from a distinct personality — diction, rhythm, what a character will and won't
say, how they hedge or don't, formal vs blunt, what they notice.

Do the BLIND-TAG TEST in your head: cover the "X said" tags. For each exchange,
answer with evidence (quote lines):
1. INTERCHANGEABLE LINES: quote any line that could be moved to another character's
   mouth with no loss — these are the failures.
2. AUTHOR VOICE: quote lines where everyone sounds like the same (the author's)
   narrator rather than themselves.
3. PER CHARACTER: does each speaker's dialogue match their declared voice signature?
   Quote a line that betrays it.
4. WHO'S MOST/LEAST distinct, and why.
Do not judge whether the dialogue is good or moves the plot — only whether the
voices are DIFFERENT and TRUE to each signature."""

SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["distinguishable", "interchangeable_lines", "author_voice_lines",
                 "per_character", "verdict"],
    "properties": {
        "distinguishable": {"type": "boolean",
                            "description": "could a reader tell speakers apart with tags removed?"},
        "interchangeable_lines": {"type": "array", "items": {"type": "string"}},
        "author_voice_lines": {"type": "array", "items": {"type": "string"}},
        "per_character": {"type": "array", "items": {
            "type": "object", "additionalProperties": False,
            "required": ["name", "on_signature", "note"],
            "properties": {
                "name": {"type": "string"},
                "on_signature": {"type": "boolean"},
                "note": {"type": "string"}}}},
        "verdict": {"type": "string",
                    "enum": ["distinct", "some-blur", "interchangeable"]},
    },
}


def voice_table(bib: B.Bible) -> str:
    L = ["VOICE SIGNATURES (declared):"]
    for c in bib.characters.values():
        if C.is_major(c) and c.attrs.get("voice"):
            L.append(f"  {c.name}: {c.attrs['voice']}")
    return "\n".join(L)


def coldread_payload(text: str, bib: B.Bible) -> str:
    return (RUBRIC + "\n\n--- " + voice_table(bib)
            + "\n\n--- SCENE ---\n\n" + text.strip())


def aggregate(verdicts: list) -> dict:
    verdicts = [v for v in verdicts if v]
    if not verdicts:
        return {"readers": 0, "passed": False, "note": "no verdicts"}
    union = lambda k: sorted({x for v in verdicts for x in (v.get(k) or [])})
    words = [v.get("verdict") for v in verdicts]
    overall = ("interchangeable" if "interchangeable" in words else
               "some-blur" if "some-blur" in words else "distinct")
    return {
        "readers": len(verdicts),
        "interchangeable_lines": union("interchangeable_lines"),
        "author_voice_lines": union("author_voice_lines"),
        "distinguishable": all(v.get("distinguishable", False) for v in verdicts),
        "overall": overall,
        "passed": overall == "distinct",
    }


# ---- reports ---------------------------------------------------------------

def format_gate(rep: dict) -> str:
    L = [f"VOICE DISTINCTIVENESS GATE — {rep['majors']} major character(s)"]
    if rep["passed"]:
        L.append("  ✓ every declared voice is specific and mutually distinct")
        return "\n".join(L)
    for g in rep["generic"]:
        L.append(f"  ✗ {g['name']}: {g['why']}")
    for col in rep["collisions"]:
        a, b = col["pair"]
        L.append(f"  ✗ {a} & {b} share voice markers {col['shared']} "
                 f"(similarity {col['similarity']}) — differentiate them")
    L.append("  RESULT: FAIL — give each character a voice rooted in a different "
             "personality (SOP-13)")
    return "\n".join(L)


def format_prints(rep: dict) -> str:
    L = ["DIALOGUE VOICEPRINTS (heuristic attribution — confirm speakers by eye)"]
    if not rep["speakers"]:
        L.append("  (no attributable dialogue found)")
        return "\n".join(L)
    L.append("  speaker          lines  words  len  contr  hedge  Q%   form  profanity")
    for name, fp in sorted(rep["speakers"].items(),
                           key=lambda kv: -kv[1]["words"]):
        thin = "" if fp["enough"] else "  (too little to judge)"
        prof = ",".join(fp["profanity"]) if fp["profanity"] else "-"
        L.append(f"  {name[:15]:<15}  {fp['lines']:>4}  {fp['words']:>5}  "
                 f"{fp['mean_len']:>4}  {fp['contraction_rate']:>4}  "
                 f"{fp['hedge_rate']:>4}  {int(fp['question_rate']):>3}  "
                 f"{fp['formality']:>4}  {prof}{thin}")
    if rep["unknown"]:
        L.append(f"  · {rep['unknown']} quote(s) unattributed")
    if rep["collisions"]:
        for col in rep["collisions"]:
            a, b = col["pair"]
            L.append(f"  ⚠ {a} & {b} are near-identical on the measured axes "
                     f"(distance {col['distance']} < {_SIM_THRESHOLD}) — likely the "
                     f"same voice (cold-read, SOP-13)")
    elif rep["gradable"]:
        L.append("  ✓ attributed speakers differ on the measured axes "
                 "(now: do they SOUND distinct? — cold read, SOP-13)")
    return "\n".join(L)


def _cli(argv):
    if not argv:
        print("usage: python -m novelkit.voice <bible.md>                    (distinctiveness gate)\n"
              "       python -m novelkit.voice <bible.md> --scene <scene.md>  (voiceprints)\n"
              "       python -m novelkit.voice <bible.md> --payload <scene.md> (cold-read payload)\n"
              "       python -m novelkit.voice --schema")
        return 2
    if argv[0] == "--schema":
        import json
        print(json.dumps(SCHEMA, indent=2))
        return 0
    bib = B.load(argv[0])
    if "--scene" in argv:
        scene = Path(argv[argv.index("--scene") + 1]).read_text(encoding="utf-8", errors="replace")
        rep = voiceprints(scene, bib)
        print(format_prints(rep))
        return 1 if rep["collisions"] else 0
    if "--payload" in argv:
        scene = Path(argv[argv.index("--payload") + 1]).read_text(encoding="utf-8", errors="replace")
        print(coldread_payload(scene, bib))
        return 0
    rep = distinctiveness_gate(bib)
    print(format_gate(rep))
    return 0 if rep["passed"] else 1


if __name__ == "__main__":
    sys.exit(_cli(sys.argv[1:]))
