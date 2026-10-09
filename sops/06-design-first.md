# SOP-06 — Design first (the no-prose-yet gate)

You may not write scene prose until the PLAN passes `design_gate()`. Researching
the premise is not enough; the anime-head failure (blender-kit) was *researching
only the "what" and skipping the craft and the failure modes*. Same trap here.

## Gate 1 — scaffold
```
cd scripts
python plan_novel.py "<premise>" --title "<title>" --protagonist "<name>"
```
Creates `_work/<slug>_plan.md` and `_work/<slug>_bible.md`.

## Gate 2 — fill the PLAN with substance (not placeholders)
Every section, real content:
- **LOGLINE** — one sentence: *[protagonist] must [goal] or [stakes], but [obstacle].*
- **PREMISE & THEME** — the dramatic question + what the book is *about* under the
  plot. A novel without a theme drifts; name it now.
- **AUDIENCE & COMPS** — genre, reader, two comps ("X meets Y"). Sets tone + length.
- **CHARACTERS** — for each major one: WANT (external goal) vs NEED (internal lack),
  and a **VOICE SIGNATURE**: 2-3 concrete speech markers (diction, sentence rhythm,
  a verbal tic, what they NEVER say). This is what stops every character sounding
  like you. Cross-link the bible.
- **STRUCTURE** — pick a template (see `references/structure/`) and write the key
  beats *with their turns* (what flips at each).
- **SCENE LEDGER** (the PLOT, planned first) — the pipe table. Each scene: **ch** ·
  pov · goal · conflict · turn · **moves** · tension(1-10). `moves` = which character
  this scene resolves an action for or changes a belief in (`Mara: belief "X" -> "Y"`;
  several separated by `;`). A scene that moves nobody is purposeless. `ch` = its chapter.
- **SUBPLOTS** — one thread per character arc: `### Name: from-belief -> to-belief`
  with `- beat: <change> @scene N` lines (mark the resolution). `plot.py` audits coverage.
- **CHAPTERS** (plan the chapters BEFOREHAND) — the `## CHAPTERS` table: ch · title ·
  purpose · subplots advanced · scenes · ~words. Chapters are LONG (multi-scene); a
  subplot SPANS a couple of chapters. `chapters.py` audits.
- **FLAGS** (optional, recommended) — typed character flags: `<type> | <character> |
  raised @scene | (paid|broken) @scene — note` (introduction/romance/death/…). SOP-12 /
  references/flags.md; `flags.py` audits the raised→paid lifecycle.
- **SETUP/PAYOFF** — promises and their payoffs (Chekhov's guns). Mirror in the bible.
- **POV & TENSE** — and the POV discipline (whose head, when).
- **RESEARCH & FAILURE MODES** — genre conventions you must honour + the failure
  modes you'll guard against (`references/failures/`). Research the CRAFT here.

## Gate 3 — fill the BIBLE (canon + CHARACTER + WORLD)
`_work/<slug>_bible.md`. For each MAJOR character commit the baseline: **traits,
backstory, PHYSICALITY (a rendered body + mannerism), voice, wants, needs, arc** (+
`pronouns:` to sharpen continuity, + eyes/hair). Add a **`## WORLDBUILDING`** section —
look & feel, daily life, social order, concrete texture details — so the world can go
ON THE PAGE, not just be named (SOP-11). Then world rules, timeline, setup/payoff,
FORBIDDEN terms. Every fact you commit is one `continuity.py`/`character.py` guards forever.

## Gate 4 — pass EVERY design gate (plot-first, then the rest)
```
python -m novelkit.plan      _work/<slug>_plan.md                       # plan complete (incl. CHAPTERS): PASS
python -m novelkit.character _work/<slug>_bible.md                      # baseline incl. physicality: PASS
python -m novelkit.structure _work/<slug>_plan.md _work/<slug>_bible.md # SCENE: each moves someone; tension rises
python -m novelkit.plot      _work/<slug>_plan.md _work/<slug>_bible.md  # PLOT: scenes do jobs; arcs pay off
python -m novelkit.chapters  _work/<slug>_plan.md _work/<slug>_bible.md  # long chapters; subplots span chapters
python -m novelkit.flags     _work/<slug>_plan.md _work/<slug>_bible.md  # flag lifecycle (if any declared)
```
If any FAILS, fix the flagged field. **No scene prose until they pass.**

→ Then SOP-00 (full novel) or SOP-02 (a single scene).
