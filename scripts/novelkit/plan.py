"""plan.py — scaffold the NOVEL BUILD PLAN + design_gate(). PURE PYTHON.

The writing analogue of blender-kit's plan/design_gate: you may NOT draft prose
until the plan passes. The anime-head lesson ports directly — researching only
"what a novel is" is not enough; you must commit the PREMISE, the CHARACTERS (with
concrete voice signatures), the STRUCTURE (a beat sheet with real escalation), the
THEME, and the SCENE LEDGER before writing scene one. preflight refuses to bless a
draft whose plan still has unfilled gates.

design_gate() passes only when every REQUIRED section exists AND is filled (not a
placeholder, not empty, meets a minimum substance bar).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# section heading (lowercased, ##-level) -> (required?, min_chars, hint)
SECTIONS = [
    ("logline", True, 40,
     "One sentence: [protagonist] must [goal] or [stakes], but [obstacle]."),
    ("premise & theme", True, 80,
     "The dramatic question + what the book is ABOUT under the plot (the theme)."),
    ("audience & comps", True, 40,
     "Genre, target reader, 2 comparable titles ('X meets Y'). Sets tone/length."),
    ("characters", True, 150,
     "Each major character: want (external) vs need (internal) + a VOICE SIGNATURE "
     "(2-3 concrete speech markers). Cross-link the story bible."),
    ("structure", True, 120,
     "Chosen template (3-act / Save the Cat / story circle) + the key beats with "
     "their turns. See references/structure/."),
    ("scene ledger", True, 120,
     "A pipe table: # | scene | pov | goal | conflict | turn | moves | tension(1-10). "
     "'moves' = which character this scene moves (Name: belief X -> Y, or Name: "
     "action resolved); a scene moving nobody is purposeless. structure.py validates."),
    ("subplots", True, 80,
     "Per-character development threads (the PLOT field). One '### Name: from-belief "
     "-> to-belief' per arc, with '- beat: <change> @scene N' lines (mark the "
     "resolution). plot.py audits beat<->scene coverage."),
    ("chapters", True, 100,
     "Plan the chapters BEFOREHAND (plot-first). Scenes live INSIDE chapters. A pipe "
     "table: ch | title | direction | subplots advanced | scenes | ~words. Each chapter "
     "needs a planned DIRECTION (opens X → turns on Y → lands Z + a hook into the next), "
     "not just a label. Chapters are LONG (multi-scene); subplots span a couple of "
     "chapters; each SCENE LEDGER row carries its `ch`. chapters.py audits."),
    ("flags", False, 0,
     "Optional, recommended: typed character FLAGS — `<type> | <character> | raised "
     "@scene | (paid|broken) @scene — note` (introduction / romance / death / …). "
     "flags.py audits the raised->paid lifecycle. See references/flags.md."),
    ("setup/payoff", True, 30,
     "Promises and their payoffs (Chekhov's guns). Mirrored in the bible ledger."),
    ("pov & tense", True, 20,
     "POV (1st / 3rd-limited / omniscient), tense, and the POV discipline (whose "
     "head, when)."),
    ("research & failure modes", True, 60,
     "Genre conventions you must honour + the failure modes you'll guard against "
     "(see references/failures/). Researching craft, not just premise."),
]

PLACEHOLDER = re.compile(r"^\s*(tbd|todo|tk|\.\.\.|xxx|\[.*\]|<.*>)\s*$", re.IGNORECASE)


def scaffold(premise: str = "") -> str:
    out = [f"# Novel Build Plan", ""]
    out.append("> DESIGN GATE: fill every section with substance. `plan.design_gate()`"
               " must PASS before any prose (SOP-06). Researching the premise is not"
               " enough — research the CRAFT (structure, genre, failure modes) too.")
    out.append("")
    if premise:
        out.append(f"*Seed premise:* {premise}")
        out.append("")
    titles = {
        "logline": "## LOGLINE",
        "premise & theme": "## PREMISE & THEME",
        "audience & comps": "## AUDIENCE & COMPS",
        "characters": "## CHARACTERS",
        "structure": "## STRUCTURE",
        "scene ledger": "## SCENE LEDGER",
        "subplots": "## SUBPLOTS",
        "chapters": "## CHAPTERS",
        "flags": "## FLAGS",
        "setup/payoff": "## SETUP/PAYOFF",
        "pov & tense": "## POV & TENSE",
        "research & failure modes": "## RESEARCH & FAILURE MODES",
    }
    for key, _req, _min, hint in SECTIONS:
        out.append(titles[key])
        out.append(f"<!-- {hint} -->")
        if key == "characters":
            out.append("<!-- Names + one-line role here; the FULL sheet (traits, "
                       "backstory, voice, want/need, ARC) lives in the story bible. -->")
        if key == "scene ledger":
            out.append("")
            out.append("| # | ch | scene | pov | goal | conflict | turn | moves | tension |")
            out.append("|---|----|-------|-----|------|----------|------|-------|---------|")
            out.append("| 1 | 1 |  |  |  |  |  |  |  |")
        if key == "subplots":
            out.append("### <Character>: <from-belief> -> <to-belief>")
            out.append("- beat:  @scene 1")
            out.append("- beat:  @scene N (resolution)")
        if key == "chapters":
            out.append("")
            out.append("| ch | title | direction (opens → turns → lands + hook) | subplots advanced | scenes | ~words |")
            out.append("|----|-------|-------------------------------------------|-------------------|--------|--------|")
            out.append("| 1 | <title> | opens <X> → turns on <Y> → lands <Z>; hook: <…> | <Character> | 1-3 | 6000 |")
        if key == "flags":
            out.append("- introduction | <Character> | raised @1 | paid @N — <note>")
            out.append("- death | <Character> | raised @N | broken @M — <subversion note>")
        out.append("")
    out.append("---")
    out.append("Story bible (canon): see `*_bible.md` — scaffold with "
               "`python -m novelkit.bible --scaffold \"<title>\"`.")
    return "\n".join(out)


def _split_sections(text: str) -> dict:
    secs = {}
    cur = None
    buf = []
    for ln in text.splitlines():
        m = re.match(r"^##\s+(.+?)\s*$", ln)
        if m:
            if cur is not None:
                secs[cur] = "\n".join(buf)
            cur = m.group(1).strip().lower()
            buf = []
        elif re.match(r"^-{3,}\s*$", ln):   # a horizontal rule ends the plan body
            if cur is not None:
                secs[cur] = "\n".join(buf)
            cur = None
        elif cur is not None:
            buf.append(ln)
    if cur is not None:
        secs[cur] = "\n".join(buf)
    return secs


def _substance(body: str) -> str:
    """strip comments/placeholders/blank -> the real filled content."""
    lines = []
    for ln in body.splitlines():
        s = ln.strip()
        if not s:
            continue
        if s.startswith("<!--") or s.startswith("-->"):
            continue
        if PLACEHOLDER.match(s):
            continue
        # a line still carrying an angle-bracket template token (<Character>, <from-belief>)
        # is an unfilled scaffold example, not real content
        if re.search(r"<[^>\n]{1,40}>", s):
            continue
        # a ledger header/separator alone isn't substance
        if re.match(r"^\|[\s#|-]*\|?$", s):
            continue
        lines.append(s)
    return "\n".join(lines)


def design_gate(text: str) -> dict:
    secs = _split_sections(text)
    results = []
    ok = True
    for key, required, min_chars, hint in SECTIONS:
        body = ""
        for k, v in secs.items():
            if k == key or k.replace(" ", "") == key.replace(" ", ""):
                body = v
                break
        filled = _substance(body)
        passed = (not required) or (len(filled) >= min_chars)
        # scene ledger also needs at least one real data row
        if key == "scene ledger" and passed:
            from . import structure as S
            rows = S.parse_ledger(text)
            real = [r for r in rows if _substance(" ".join(r.values()))]
            if len(real) < 1:
                passed = False
        if required and not passed:
            ok = False
        results.append({"section": key, "required": required, "chars": len(filled),
                        "min": min_chars, "passed": passed, "hint": hint})
    return {"passed": ok, "sections": results}


def format_gate(rep: dict) -> str:
    L = ["DESIGN GATE"]
    for r in rep["sections"]:
        mark = "✓" if r["passed"] else "✗"
        need = "" if r["passed"] else f"  (have {r['chars']}/{r['min']} chars)"
        L.append(f"  {mark} {r['section']}{need}")
        if not r["passed"]:
            L.append(f"        → {r['hint']}")
    L.append("")
    L.append("  RESULT: " + ("PASS — you may draft (SOP-00 / SOP-02)."
                             if rep["passed"]
                             else "FAIL — fill the gates above. No prose yet."))
    return "\n".join(L)


def _cli(argv):
    if not argv:
        print("usage: python -m novelkit.plan --scaffold [\"premise\"]\n"
              "       python -m novelkit.plan <plan.md>            (run design gate)")
        return 2
    if argv[0] == "--scaffold":
        print(scaffold(argv[1] if len(argv) > 1 else ""))
        return 0
    text = Path(argv[0]).read_text(encoding="utf-8", errors="replace")
    rep = design_gate(text)
    print(format_gate(rep))
    return 0 if rep["passed"] else 1


if __name__ == "__main__":
    sys.exit(_cli(sys.argv[1:]))
