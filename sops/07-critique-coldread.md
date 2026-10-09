# SOP-07 — The adversarial COLD READ

This is the writing analogue of *looking at the render*. You cannot judge whether
your own prose works — you know what it was *meant* to do, so you read the intent,
not the words. A cold reader doesn't. Spawn fresh subagents that never saw the
plan, the outline, or your notes, and let them tell you where it fails.

## Gate 1 — build the BLIND payload
```
cd scripts && python -m novelkit.critique _work/<scene>.md            # whole file
python -m novelkit.critique _work/manuscript.md --scene 3             # one scene
```
This strips author notes (`[NOTE: …]`, `<!-- … -->`) and structural headings so the
reader is not primed, then prints the RUBRIC + the blind prose. Never hand a reader
the plan, the theme, or "what I was going for." Priming defeats the whole point.

## Gate 2 — spawn 1-3 INDEPENDENT readers
Use the **Agent tool** (general-purpose), one call per reader, in a single message
so they run concurrently and cannot see each other. Give each the printed prompt
and force the verdict schema:
```
python -m novelkit.critique --schema      # the JSON Schema to pass as the Agent `schema` option
```
For variety, vary the lens per reader: a genre fan, an impatient skimmer, a
line-level stylist. Each returns the structured verdict (engagement 1-5,
would_turn_page, confusions, cliches, voice_problems, told_not_shown, scene_want,
one_cut, one_fix, verdict).

## Gate 3 — aggregate (pessimistically)
Collect the verdicts and aggregate. In a workflow you can call
`novelkit.critique.aggregate([...])`; by hand, apply its rule:
- engagement = MEDIAN (one generous reader can't carry it);
- a confusion ANY reader raised is real;
- "works" only if no reader said broken, median engagement ≥ 4, and ≥ half would
  turn the page. Otherwise needs-work / broken.

## Gate 4 — revise to the verdict, then re-read
Make the cuts and the one-fix changes. If the verdict was needs-work/broken, do
another cold read after revising — with NEW reader instances (a reader who already
read it is no longer cold). Stop when a fresh panel says "works".

## Gate 5 — record (only if verified)
If the read taught a reusable craft lesson, append it to the relevant
`references/craft/` or `references/failures/` entry, citing this read as
`verified_by`. Do not record an unverified hunch.
