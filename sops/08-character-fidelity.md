# SOP-08 — CHARACTER field: baseline + in-character fidelity

A character is a baseline (backstory + traits + voice + want/need + arc) that the
prose must HONOUR. The model invents flat people and then has them do whatever the
plot needs. Two gates: the baseline (do they exist as real people?) and fidelity
(do they ACT like themselves in this scene?).

## Gate 1 — BASELINE (project-level, run once + whenever a character is added)
```
cd scripts && python -m novelkit.character _work/<slug>_bible.md
```
Every MAJOR character (protagonist/antagonist/etc., or any with no role declared)
must have: **traits, backstory, voice, wants, needs, arc**. FAIL = fill the bible
sheet. The `arc` is the spine of that character's subplot (SOP-09) — write it as
`from "<start belief>" to "<end belief>"`. Minor walk-ons are exempt.

## Gate 2 — VOICE RULES (deterministic, per scene)
```
python -m novelkit.character _work/<slug>_bible.md --voice _work/<scene>.md "Mara Vance"
```
Checks the dialogue against rules parsed from the voice line — e.g. *never swears*
(flags profanity), *never says "X"*. These are REVIEW hints (confirm the speaker by
eye). To make a rule checkable, phrase it in the voice field as `never swears` or
`never says "okay"`.

> This gate is about a SINGLE voice (does X sound like X / keep X's rules). Whether
> the CAST sounds like different *people* — voice distinctiveness, the blind-tag test
> — is **SOP-13** (`novelkit.voice`). Run both: a character can be perfectly in voice
> yet indistinguishable from everyone else.

## Gate 3 — FIDELITY AUDIT (the in-character cold read, per scene)
The real test is judgement, so spawn an auditor subagent — like SOP-07's cold read
but focused on consistency. Get the payload + schema:
```
python -m novelkit.character _work/<slug>_bible.md --payload _work/<scene>.md "Mara Vance"
python -m novelkit.character --schema
```
Spawn one **Agent** (general-purpose) per acting character with the payload (dossier
+ scene) and the verdict schema. It returns: in_character, out_of_character_beats,
voice_problems, motivation_problems, arc_movement (toward/away/steady/contradicts),
earned, verdict (consistent/minor-slips/out-of-character). Aggregate with
`character.aggregate([...])` (out-of-character from ANY auditor stands).

## Gate 4 — the EARNED test
The most common failure isn't a wrong eye colour, it's an unearned change: a guarded
character suddenly confides, a coward suddenly brave, with nothing on the page to
turn them. If `earned` is false or `arc_movement` is "contradicts", the scene must
either dramatise the cause or not make the change here. Revise, then re-audit with a
fresh auditor.

## Gate 5 — feed it back
A character's realised change in a scene IS a subplot beat — record it in the plan's
SUBPLOTS with `@scene N` so SOP-09's plot audit sees the arc advancing. Fidelity
(does the scene honour the character) and plot (does the arc pay off across scenes)
are two ends of the same thread.
