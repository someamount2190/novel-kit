"""character.py — the CHARACTER field. PURE PYTHON (+ subagent harness for fidelity).

A character is not a name with an eye colour; it is a baseline of BACKSTORY + TRAITS
+ VOICE + a WANT/NEED + an ARC (the belief they start with -> the belief they end
with). The model invents flat, interchangeable people and then has them act however
the plot needs. Two guards:

  • baseline_gate(bible) — refuses a thin character: every MAJOR character must
    declare traits, backstory, voice, want, need, arc. (The arc is the spine of that
    character's subplot in plot.py.)
  • fidelity — does the character ACT IN ACCORDANCE with their traits/backstory in a
    given scene? A little is deterministic (voice rules like "never swears"); the
    rest is judgement, so this module preps a dossier + the scene + a rubric/schema
    for an in-character audit subagent (spawned per SOP-08), and aggregates verdicts.

Character fields are read from the story bible (see bible.py) — enrich each
`### Name` block with: traits, backstory, voice, wants, needs, arc, pronouns.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from . import bible as B

# fields a MAJOR character must have to be a "baseline character"
REQUIRED = ["traits", "backstory", "physicality", "voice", "wants", "needs", "arc"]
MAJOR_ROLES = ("protagonist", "antagonist", "deuteragonist", "major", "pov",
               "lead", "main")

PROFANITY = {"damn", "hell", "shit", "fuck", "fucking", "bastard", "bitch", "ass",
             "arse", "bloody", "crap", "goddamn", "piss"}


def is_major(c: B.Character) -> bool:
    role = (c.attrs.get("role") or "").lower()
    if not role:
        return True  # no role declared -> treat as major (be strict)
    return any(r in role for r in MAJOR_ROLES)


def baseline_gate(bib: B.Bible) -> dict:
    rows = []
    ok = True
    for c in bib.characters.values():
        if not is_major(c):
            rows.append({"name": c.name, "major": False, "missing": [], "passed": True})
            continue
        missing = [f for f in REQUIRED
                   if not (c.attrs.get(f) or "").strip()
                   or (c.attrs.get(f) or "").strip().lower() in ("tbd", "todo", "-")]
        passed = not missing
        ok = ok and passed
        rows.append({"name": c.name, "major": True, "missing": missing, "passed": passed})
    return {"passed": ok, "characters": rows}


def voice_rules(c: B.Character) -> list:
    """Extract checkable rules from the voice line. Today: 'never swears' and
    'never says "<x>"' / 'never uses "<x>"'. Returns list of ('no-profanity'|literal)."""
    voice = (c.attrs.get("voice") or "").lower()
    rules = []
    if re.search(r"never\s+(swear|curse|cuss)", voice):
        rules.append(("no-profanity", None))
    for m in re.finditer(r'never\s+(?:says?|uses?|utters?)\s+["“\']([^"”\']+)["”\']', voice):
        rules.append(("forbid", m.group(1).lower()))
    return rules


def scan_scene_voice(scene_text: str, c: B.Character) -> list:
    """Deterministic voice-rule violations attributable to dialogue in the scene.
    Heuristic: checks dialogue spans (text in quotes). Flags for REVIEW — confirm the
    speaker by eye (we can't perfectly attribute every quote)."""
    rules = voice_rules(c)
    if not rules:
        return []
    dialogue = " ".join(re.findall(r'["“]([^"”]+)["”]', scene_text)).lower()
    if not dialogue:
        return []
    hits = []
    for kind, val in rules:
        if kind == "no-profanity":
            found = sorted({w for w in re.findall(r"[a-z']+", dialogue) if w in PROFANITY})
            if found:
                hits.append({"rule": f"{c.name} never swears", "violation": found})
        elif kind == "forbid":
            if re.search(rf"\b{re.escape(val)}\b", dialogue):
                hits.append({"rule": f'{c.name} never says "{val}"', "violation": [val]})
    return hits


# ---- fidelity audit (in-character) subagent harness -----------------------
RUBRIC = """You are a CHARACTER-CONSISTENCY auditor. Below is a character dossier
(their backstory, traits, voice, want/need, arc) and a scene. Judge ONLY whether
this character behaves, speaks, and reacts in a way consistent with that dossier —
not whether the scene is good. A character may grow, but growth must be EARNED on
the page, not abrupt.

Answer with evidence, quoting lines:
1. IN-CHARACTER? Does each action/line fit their traits + backstory? Quote any
   beat that feels out of character (someone "stubborn and guarded" suddenly
   confiding for no reason).
2. VOICE: do their lines match their voice signature (diction, rhythm, what they
   never say)? Quote any line that sounds like a different person (or like the
   author).
3. MOTIVATION: is what they do here driven by their want/need, or by plot
   convenience? Quote forced moves.
4. ARC: does this scene move them along their arc (closer to/further from the
   end-belief), hold steady, or contradict it? If it contradicts, quote it.
5. Does the scene EARN any change of belief/decision they make, or is it abrupt?
Be specific. Do not summarise the plot."""

SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["in_character", "out_of_character_beats", "voice_problems",
                 "motivation_problems", "arc_movement", "earned", "verdict"],
    "properties": {
        "in_character": {"type": "boolean"},
        "out_of_character_beats": {"type": "array", "items": {"type": "string"}},
        "voice_problems": {"type": "array", "items": {"type": "string"}},
        "motivation_problems": {"type": "array", "items": {"type": "string"}},
        "arc_movement": {"type": "string",
                         "enum": ["toward", "away", "steady", "contradicts"]},
        "earned": {"type": "boolean",
                   "description": "if they change a belief/make a big decision, is it earned?"},
        "verdict": {"type": "string", "enum": ["consistent", "minor-slips", "out-of-character"]},
    },
}


def dossier(c: B.Character) -> str:
    L = [f"CHARACTER: {c.name}"]
    if c.aliases:
        L.append(f"  aliases: {', '.join(c.aliases)}")
    for f in ("pronouns", "role", "traits", "backstory", "physicality", "voice",
              "wants", "needs", "arc"):
        v = c.attrs.get(f)
        if v:
            L.append(f"  {f}: {v}")
    return "\n".join(L)


def fidelity_payload(c: B.Character, scene_text: str) -> str:
    return (RUBRIC + "\n\n--- DOSSIER ---\n" + dossier(c)
            + "\n\n--- SCENE ---\n\n" + scene_text.strip())


def aggregate(verdicts: list) -> dict:
    verdicts = [v for v in verdicts if v]
    if not verdicts:
        return {"readers": 0, "passed": False, "note": "no verdicts"}
    union = lambda k: sorted({x for v in verdicts for x in (v.get(k) or [])})
    words = [v.get("verdict") for v in verdicts]
    ooc = words.count("out-of-character")
    overall = ("out-of-character" if ooc else
               "minor-slips" if "minor-slips" in words else "consistent")
    moves = [v.get("arc_movement") for v in verdicts]
    return {
        "readers": len(verdicts),
        "out_of_character_beats": union("out_of_character_beats"),
        "voice_problems": union("voice_problems"),
        "motivation_problems": union("motivation_problems"),
        "arc_movement": max(set(moves), key=moves.count) if moves else "steady",
        "earned": all(v.get("earned", True) for v in verdicts),
        "overall": overall,
        "passed": overall == "consistent",
    }


def _cli(argv):
    if not argv:
        print("usage: python -m novelkit.character <bible.md>                 (baseline gate)\n"
              "       python -m novelkit.character <bible.md> --voice <scene.md> <Name>\n"
              "       python -m novelkit.character <bible.md> --payload <scene.md> <Name>\n"
              "       python -m novelkit.character --schema")
        return 2
    if argv[0] == "--schema":
        import json
        print(json.dumps(SCHEMA, indent=2))
        return 0
    bib = B.load(argv[0])
    if "--voice" in argv:
        scene = Path(argv[argv.index("--voice") + 1]).read_text(encoding="utf-8", errors="replace")
        name = argv[argv.index("--voice") + 2]
        c = bib.character_by_any_name(name) or bib.characters.get(name)
        if not c:
            print(f"no character '{name}'")
            return 2
        hits = scan_scene_voice(scene, c)
        if not hits:
            print(f"✓ no deterministic voice-rule violations for {c.name}")
            return 0
        for h in hits:
            print(f"  • REVIEW: {h['rule']} — found {h['violation']} in dialogue")
        return 1
    if "--payload" in argv:
        scene = Path(argv[argv.index("--payload") + 1]).read_text(encoding="utf-8", errors="replace")
        name = argv[argv.index("--payload") + 2]
        c = bib.character_by_any_name(name) or bib.characters.get(name)
        print(fidelity_payload(c, scene))
        return 0
    # default: baseline gate
    rep = baseline_gate(bib)
    print("CHARACTER BASELINE GATE")
    for r in rep["characters"]:
        if not r["major"]:
            print(f"  · {r['name']} (minor — exempt)")
            continue
        mark = "✓" if r["passed"] else "✗"
        miss = "" if r["passed"] else f"  missing: {', '.join(r['missing'])}"
        print(f"  {mark} {r['name']}{miss}")
    print("\n  RESULT: " + ("PASS" if rep["passed"]
                            else "FAIL — every major character needs "
                                 + ", ".join(REQUIRED)))
    return 0 if rep["passed"] else 1


if __name__ == "__main__":
    sys.exit(_cli(sys.argv[1:]))
