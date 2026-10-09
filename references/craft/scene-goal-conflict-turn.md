# Craft: a scene = goal → conflict → turn

**Principle.** A scene is not "stuff that happens in one place." It is a unit of
change: a POV character pursues a concrete GOAL, meets CONFLICT (opposition that
matters), and the scene TURNS — the character's situation is measurably better or
worse at the end than the start. If you can cut a scene and the story is unchanged,
it had no turn. (Sources: Swain, *Techniques of the Selling Writer*; Bell, *Scene &
Structure*; Coyne, *The Story Grid* — the value-shift test.)

**Why the model needs it.** Left to autopilot, the model writes *connective tissue*:
characters travel, recap, and chat pleasantly. Each reads fine line-by-line and the
whole sags. `structure.py` enforces goal/conflict/turn columns + a tension change so
this can't hide.

**Before (no turn — flat).**
> Mara walked to the records office. She thought about her sister. The clerk was
> there. They talked about the weather. She decided to come back tomorrow.

Goal vague, conflict none, nothing turned. Tension flat.

**After (goal/conflict/turn).**
> Mara needed the gate log before the clerk's shift ended *(goal)*. He slid the
> ledger out of reach: "Records are closed." *(conflict)* She reached past him
> anyway — and saw the flood-night entry had been scraped out and rewritten.
> *(turn: she now knows it was deliberate; tension up)*

**Discriminating check.** Fill the ledger row. If goal/conflict/turn can't all be
named, the scene is connective tissue — cut it or give it a job. A scene whose turn
is the same valence as the last three (all wins or all losses) flattens the line;
`structure.py` flags that too.
