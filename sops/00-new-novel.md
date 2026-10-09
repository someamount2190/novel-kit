# SOP-00 — Draft a new novel (the full loop)

## Gate 1 — DESIGN (SOP-06)
Do SOP-06 in full. `plan.design_gate()` and `structure.py` must PASS. No prose yet.

## Gate 2 — draft chapter by chapter, scene by scene
Work the SCENE LEDGER in order. For each scene, run SOP-02 (draft → scan → revise).
Keep each draft scene in `_work/` as `<slug>_chNN_sM.md` (or one growing manuscript
file with `# Chapter N` / `***` separators — `manuscript.py` parses both).

After each scene:
- update the BIBLE if the scene established new canon (a new name, a date, a
  promise). Stale bible → false continuity passes.
- log new setups in the bible's SETUP/PAYOFF ledger so the dangling-gun check can
  track them.

## Gate 3 — INSPECT per scene (the gate)
```
python -m novelkit.report _work/<scene>.md _work/<slug>_bible.md _work/<slug>_plan.md
```
Fix every HARD prose flag and every continuity contradiction. Structure issues are
plan-level — fix them in the ledger, not by patching prose.

## Gate 4 — COLD READ per scene (SOP-07)
Spawn 1-3 independent reader subagents on the blind payload; aggregate. Revise to
their verdict. A scene is done when the deterministic gate PASSES **and** the cold
read says "works".

## Gate 5 — chapter & act seams
At each chapter end, run `manuscript.py` on the accumulated text to confirm
scene/word balance, and re-run `continuity.py` over the WHOLE manuscript so far
(contradictions usually appear *between* scenes, not inside one). At each act
boundary, re-check `structure.py`: did the tension actually escalate, or did the
middle sag?

## Gate 6 — report honestly
Cite the cold read(s) you addressed and the last clean `report`. Note anything you
could not verify. Never claim "compelling" from your own read.
