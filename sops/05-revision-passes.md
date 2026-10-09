# SOP-05 — Revision passes (macro → micro; line-edit last)

Revise in altitude order. Re-line-editing prose you later cut is wasted work, so
each pass must settle before the next. Never jump straight to comma-level edits.

## Pass 1 — STRUCTURE (does the spine hold?)
`python -m novelkit.structure <plan>`. Every scene earns its place (goal/conflict/
turn). Tension escalates; the climax lands late; no sagging middle; outcomes aren't
all-wins or all-losses. Fix at the LEDGER level — cut/merge/reorder scenes.

## Pass 2 — CONTINUITY (does it contradict itself?)
`python -m novelkit.continuity <manuscript> <bible>` over the whole text. Resolve
contradictions, name drift, forbidden terms, dangling setups. Keep the bible current.

## Pass 3 — SCENE CRAFT (does each scene work?)
Cold-read (SOP-07) the weak scenes flagged in Pass 1. Fix scene-level problems:
late entry/early exit, clarity of the turn, stakes, POV discipline.

## Pass 4 — VOICE & DIALOGUE
Read each major character's lines in isolation: do they sound like distinct people?
Strip said-bookisms and adverb tags (`prose_scan` lists them). Cut dialogue that
only conveys information the reader already has.

## Pass 5 — LINE EDIT (prose smell)
`python -m novelkit.prose_scan <scene>` per scene. Work the categories:
- cut filter words (saw/heard/felt/realised) — go straight to the perception;
- replace clichés with something seen freshly;
- cut empty intensifiers (very/really/just/suddenly);
- prefer strong verbs over verb+adverb;
- vary sentence length (fix monotone-rhythm and same-opener runs);
- prefer active voice unless the passive is deliberate.
Every HARD flag resolved; REVIEW flags judged by eye.

## Pass 6 — PROOF
Read aloud (or have a cold reader read for *flow*, not craft). Fix what trips the
tongue. Final `report` should PASS; final cold read should say "works".
