# Craft: a chapter = opens → turns → lands + hook

**Principle.** A chapter is not just a bag of scenes. It has its own internal arc:
it OPENS with orientation (who/where/why it matters), TURNS through escalating
complications, and LANDS on a resolution that HOOKS the reader into the next.
A chapter without direction feels like random scenes stapled together; a chapter
without a hook gives the reader a natural stopping point they'll actually take.
(Sources: King, *On Writing*; Brooks, *Story Engineering*; Coyne, *The Story Grid*
— chapter-level command units.)

**Why the model needs it.** Left to autopilot, the model treats chapters as arbitrary
scene collections. Each scene has individual tension but the chapter as a whole
wanders, never builds to anything, and ends without pulling the reader forward.
`chapters.py` enforces a `direction` per chapter and an internal tension curve, so
chapters earn their place in the larger work.

**Before (scenes stapled together — no chapter arc).**
> Chapter 3 has three scenes: Mara argues with her mentor (tension 4→6), then
> researches in the library (tension 3→3), then eats dinner (tension 2→2). The
> chapter opens mid-argument with no orientation, and ends on a mundane meal.
> Why should the reader keep reading?

No chapter-level direction. Tension yo-yos. Lands dead.

**After (opens→turns→lands+hook).**
> Chapter 3 OPENS with Mara storming out of the argument, her goal clear: find
> proof before sunset. Scene 2: the library, she discovers the archive was purged
> (tension up). Scene 3: dinner, her sister casually mentions the purging date —
> the night their father died. LANDS + HOOK: Mara realizes the purge wasn't routine.
> She needs to know who ordered it. Chapter 4 opens.

Chapter has direction. Tension builds. Lands on a revelation that demands the next
chapter.

**Discriminating check.** Fill the chapter's `direction` field: what does this chapter
DO? Then map the tension curve: does each scene turn the knob higher? Does the
landing settle nothing and plant a question only the next chapter can answer? A
chapter that opens cold, wanders, and ends on a resolved note is a demotion to
"scene collection" — restructure it or merge it.
