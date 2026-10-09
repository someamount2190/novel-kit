# SOP-09 — PLOT field: audit the timeline + subplots

The plot is a malleable timeline (the SCENE LEDGER) with character SUBPLOTS woven
in. Because it's malleable, every edit (move/cut/add a scene, re-tag a beat) can
silently break coverage — so the audit is something you RE-RUN, not a one-time gate.

## Gate 1 — declare the subplots (in the plan)
Under `## SUBPLOTS`, one thread per character arc:
```
### Mara: carrying the truth alone -> sharing it
- beat: insists on investigating alone @scene 2
- beat: lies to her deputy @scene 5
- beat: testifies publicly @scene 12 (resolution)
```
Each beat is a belief/decision change tagged with the scene that dramatises it. Mark
the landing beat `(resolution)`. The thread title's `Name:` must match a bible
character (first name is enough).

## Gate 2 — every scene declares its `moves`
In the SCENE LEDGER, each row's `moves` cell names the character(s) it moves and the
delta: `Mara: belief "X" -> "Y"` or `Elias: confesses (action)`. A climactic scene
may move several — separate with `;`. A scene with no `moves` is purposeless.

## Gate 3 — run the audit
```
cd scripts && python -m novelkit.plot _work/<slug>_plan.md _work/<slug>_bible.md
```
It cross-references three layers and FAILS on any of:
- **purposeless scene** — moves no character (cut it or give it a job);
- **subplot not dramatised** — a beat with no `@scene`, an out-of-range scene, or a
  beat whose scene moves a *different* character (the development isn't on the page);
- **timeline order** — a beat that precedes an earlier beat in the same thread;
- **arc incomplete** — a major character's arc with <2 realised beats, or no
  resolution beat;
- **arc never realised** — an `arc` declared in the bible with no subplot at all.

## Gate 4 — revise the PLOT, not the prose
Plot problems are fixed at the ledger/subplot level: add the missing beat, retag a
scene, cut a purposeless scene, reorder. Then re-run the audit. Don't paper over a
structural hole with a nice paragraph.

## Gate 5 — re-audit after every structural edit
Moved scene 7 to scene 4? Cut a chapter? Re-run `plot.py` — beat `@scene` tags and
the tension curve (`structure.py`) may now be wrong. The timeline is malleable on
purpose; the audit is how you keep it honest.
