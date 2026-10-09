# SOP-02 — Draft or revise a single scene

A scene is the unit of work. It must DO something: a POV character pursues a goal,
meets conflict, and the situation TURNS (better or worse) by the end. A scene where
nothing changes is a candidate for cutting.

## Gate 1 — know the scene's job (from the ledger)
Find this scene's row in the plan's SCENE LEDGER: pov · goal · conflict · turn ·
**moves** · tension. The `moves` is the scene's reason to exist — which character it
resolves an action for or changes a belief in. If it has no goal/conflict/turn or
moves nobody, fix the LEDGER first (SOP-06) — don't write a scene with no job. Re-read
the POV (and any acting) character's full dossier — traits, backstory, voice, arc
(bible) — so you write them in character.

## Gate 2 — draft against craft, not autopilot
Before writing, skim `references/craft/` and `references/failures/`. While drafting:
- **Enter late, leave early** — start at the latest possible moment, cut the run-up.
- **Show the turn** — dramatise the change; don't summarise the emotion.
- **One voice** — stay in the POV character's head and diction; no head-hopping.
- **Concrete + specific** — named nouns, active verbs; resist the most-probable phrase.

## Gate 3 — scan BOTH directions (excess AND thinness)
```
cd scripts && python -m novelkit.prose_scan _work/<scene>.md            # too-MUCH
              python -m novelkit.texture    _work/<scene>.md --genre <g> # too-LITTLE
```
`prose_scan`: fix HARD flags (clichés, impossible tags, crutch-level density, monotone
rhythm); REVIEW flags are "go look". `texture` is the RICHNESS floor — render the WORLD
(sensory, lived-in, not just named) and EMBODY the people (bodies, faces, mannerisms —
including the POV). A `thin` verdict means fix it; a `rich` verdict is necessary, not
sufficient (density can't tell named from rendered — that's the cold read, SOP-11).

## Gate 4 — continuity + structure
```
python -m novelkit.report _work/<scene>.md _work/<slug>_bible.md _work/<slug>_plan.md
```
Resolve every attribute contradiction, name-drift suspect, forbidden term. If the
scene created new canon, write it into the bible NOW.

## Gate 5 — COLD READ (SOP-07) + CHARACTER FIDELITY (SOP-08)
Necessary even when the scanners are clean. Cold read: blind readers on the payload,
including the IMMERSION + EMBODIMENT lens — is the world rendered (not just named)? are
the people bodies, not labels? (`world_vivid=false` or any `embodiment_problems` →
revise: render the thin spots, give unembodied characters a body + a beat; SOP-11.)
Fidelity: for each character acting in the scene, audit they behave per their dossier
and that any belief/decision change is EARNED on the page. If the scene moves a
character, that change is a SUBPLOT beat — record it `@scene N` and re-run the plot
audit (SOP-09). Update any FLAGS this scene raises or pays (SOP-12).

## Gate 6 — done
Deterministic gate PASS + cold read "works" + characters stay in character → done.
Report citing the cold read and fidelity audit.
