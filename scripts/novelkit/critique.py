"""critique.py — BLIND cold-read harness. PURE PYTHON (prep + aggregation only).

There is no objective render of a novel, so the model praises its own draft. The
defence is a COLD READER: a fresh subagent that never saw the plan, the intent, or
the author's notes — it reads the prose blind, as a stranger in a bookshop would,
and reports where it got bored, confused, or felt the words before. That is the
writing analogue of viewing the render.

This module does NOT call the model. It (1) prepares a clean blind payload from a
scene (stripping author notes / plan leakage so the reader can't be primed), (2)
ships the RUBRIC + the verdict SCHEMA the SOP tells Claude to spawn readers with,
and (3) aggregates several readers' verdicts into one honest verdict. Spawning the
reader subagents is SOP-07's job (via the Agent tool); keep them independent.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# lines that would PRIME the reader (author intent, plan refs, meta) — stripped.
_NOTE = re.compile(r"^\s*(\[.*\]|<!--.*-->|note:|todo:|tk:|\(author:.*\))\s*$",
                   re.IGNORECASE)

RUBRIC = """You are a COLD READER. You have NOT seen any plan, outline, or author
intent — only the prose below. Read it once, the way a stranger flips through a
book in a shop, then answer honestly. Be specific and quote lines. Your job is to
find where this LOSES a reader, not to be kind.

1. ENGAGEMENT (1-5): would you turn the page? Where exactly did your attention
   slacken? Quote the first sentence you skimmed.
2. CONFUSION: anything you had to re-read? Who's speaking/where are we/what just
   happened? Quote it.
3. FAMILIARITY: any phrase, image, or beat you've read a hundred times before
   (cliché / predictable turn)? Quote each.
4. CHARACTER & VOICE: do the speakers sound like distinct people, or one voice?
   Any line that no real person would say?
5. SHOW vs TELL: where are we TOLD an emotion/fact we should have been shown?
6. STAKES & FORWARD PULL: what does the POV character want in this scene, and what
   makes you need to know what happens next? If nothing — say so.
7. IMMERSION / WORLD: could you SEE, hear, smell this place? Is the world rendered on
   the page, or just NAMED (terms and systems referenced but never made physical)?
   Quote where it goes thin / white-room.
8. CHARACTER EMBODIMENT: do the people have bodies, faces, mannerisms — do they feel
   like specific physical humans, or are they names with dialogue? Name anyone who's
   a label rather than a person.
9. ONE CUT, ONE FIX: the single line/paragraph you'd cut, and the single change
   that would most improve the scene.
Do NOT summarise the plot back. Do NOT praise without a reason."""

# JSON Schema for a structured verdict (use with the Agent `schema` option).
SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["engagement", "would_turn_page", "confusions", "cliches",
                 "voice_problems", "told_not_shown", "world_vivid", "immersion_problems",
                 "embodiment_problems", "scene_want", "one_cut", "one_fix", "verdict"],
    "properties": {
        "engagement": {"type": "integer", "minimum": 1, "maximum": 5},
        "would_turn_page": {"type": "boolean"},
        "first_skimmed_line": {"type": "string"},
        "confusions": {"type": "array", "items": {"type": "string"}},
        "cliches": {"type": "array", "items": {"type": "string"}},
        "voice_problems": {"type": "array", "items": {"type": "string"}},
        "told_not_shown": {"type": "array", "items": {"type": "string"}},
        "world_vivid": {"type": "boolean",
                        "description": "is the world rendered/perceivable, not just named?"},
        "immersion_problems": {"type": "array", "items": {"type": "string"},
                               "description": "where the world is thin / white-room / named-not-shown"},
        "embodiment_problems": {"type": "array", "items": {"type": "string"},
                                "description": "characters who are names/labels, not physical people"},
        "scene_want": {"type": "string",
                       "description": "what the POV character wants here, or 'unclear'"},
        "one_cut": {"type": "string"},
        "one_fix": {"type": "string"},
        "verdict": {"type": "string", "enum": ["works", "needs-work", "broken"]},
    },
}


def blind_payload(scene_text: str) -> str:
    """Strip priming notes; return clean prose for a cold read."""
    kept = [ln for ln in scene_text.splitlines() if not _NOTE.match(ln)]
    # also strip markdown scene/chapter headings so the reader isn't told structure
    kept = [ln for ln in kept if not re.match(r"^\s*#{1,3}\s", ln)]
    return "\n".join(kept).strip()


def prompt_for(scene_text: str) -> str:
    """The full prompt to hand a cold-read subagent."""
    return RUBRIC + "\n\n--- PROSE (read cold) ---\n\n" + blind_payload(scene_text)


def aggregate(verdicts: list) -> dict:
    """Combine independent cold readers into one verdict. Pessimistic by design:
    one reader's confusion is real even if others missed it; engagement is the
    median (resists a single generous reader)."""
    verdicts = [v for v in verdicts if v]
    if not verdicts:
        return {"readers": 0, "passed": False, "note": "no verdicts"}
    eng = sorted(v.get("engagement", 0) for v in verdicts)
    median = eng[len(eng) // 2]
    turn = sum(1 for v in verdicts if v.get("would_turn_page")) / len(verdicts)
    vivid = sum(1 for v in verdicts if v.get("world_vivid")) / len(verdicts)
    union = lambda key: sorted({x for v in verdicts for x in (v.get(key) or [])})
    verdict_words = [v.get("verdict") for v in verdicts]
    broken = verdict_words.count("broken")
    needs = verdict_words.count("needs-work")
    # world not vivid to a majority, or embodiment problems raised, push to needs-work
    embod = union("embodiment_problems")
    overall = ("broken" if broken else
               "needs-work" if (needs or median < 4 or turn < 0.5 or vivid < 0.5 or embod)
               else "works")
    return {
        "readers": len(verdicts),
        "engagement_median": median,
        "would_turn_page_frac": round(turn, 2),
        "world_vivid_frac": round(vivid, 2),
        "confusions": union("confusions"),
        "cliches": union("cliches"),
        "voice_problems": union("voice_problems"),
        "told_not_shown": union("told_not_shown"),
        "immersion_problems": union("immersion_problems"),
        "embodiment_problems": embod,
        "cuts": [v.get("one_cut") for v in verdicts if v.get("one_cut")],
        "fixes": [v.get("one_fix") for v in verdicts if v.get("one_fix")],
        "overall": overall,
        "passed": overall == "works",
    }


def format_aggregate(agg: dict) -> str:
    if not agg.get("readers"):
        return "COLD READ — no verdicts collected."
    L = [f"COLD READ — {agg['readers']} reader(s)  → {agg['overall'].upper()}"]
    L.append(f"  engagement (median): {agg['engagement_median']}/5   "
             f"would-turn-page: {int(agg['would_turn_page_frac']*100)}%")
    for key, label in [("confusions", "confusions"), ("cliches", "felt-before"),
                       ("voice_problems", "voice"), ("told_not_shown", "told-not-shown")]:
        items = agg.get(key) or []
        if items:
            L.append(f"  {label}:")
            for it in items[:6]:
                L.append(f"    • {it}")
    if agg.get("fixes"):
        L.append("  suggested fixes:")
        for f in agg["fixes"][:4]:
            L.append(f"    → {f}")
    return "\n".join(L)


def _cli(argv):
    if not argv:
        print("usage: python -m novelkit.critique <scene.md> [--scene N]   (emit blind prompt)\n"
              "       python -m novelkit.critique --schema                 (print verdict schema)")
        return 2
    if argv[0] == "--schema":
        import json
        print(json.dumps(SCHEMA, indent=2))
        return 0
    text = Path(argv[0]).read_text(encoding="utf-8", errors="replace")
    if "--scene" in argv:
        from . import manuscript as M
        n = int(argv[argv.index("--scene") + 1])
        ms = M.parse(text, argv[0])
        sc = next((s for s in ms.scenes if s.index + 1 == n), None)
        text = sc.text if sc else text
    print(prompt_for(text))
    return 0


if __name__ == "__main__":
    sys.exit(_cli(sys.argv[1:]))
