# Craft: scenes serve the chapter's arc, not just their own

**Principle.** A scene within a chapter has two jobs: its own turn (goal→conflict→
turn) AND contributing to the chapter's internal arc. Scenes must stack, not
stutter — each scene hands off tension to the next, raising the chapter's overall
curve. A scene that resolves its own mini-arc but resets tension for the next
scene is episodic; the chapter feels like a TV episode, not a unified movement.
(Sources: Ingermanson, *Physics of Fiction*; Brooks, *Story Engineering*; Coyne,
*The Story Grid* — scene-level command units within chapter arcs.)

**Why the model needs it.** Left to autopilot, the model writes standalone scenes
that happen in sequence. Each scene has goal/conflict/turn, but the chapter's
tension bounces: 4→6, then 3→3, then 5→7. The chapter never builds. `chapters.py`
plots the chapter's internal tension curve; `structure.py` flags when scenes don't
escalate within the chapter. Scenes must hand off — the turn of scene N raises
the stakes for scene N+1.

**Before (episodic scenes — no handoff).**
> Chapter 4, Scene 1: Mara confronts the archive keeper. He refuses to help.
> She leaves, frustrated. (tension 4→6)
> Scene 2: Mara returns to her room. Nothing connects to the archive. She
> examines a locket and cries about her father. (tension 3→3)
> Scene 3: Mara visits the market. Unrelated to scenes 1 or 2. She buys
> apples and hears a rumor. (tension 5→7)

Each scene has its own arc. The chapter bounces. No build.

**After (stacking scenes — handoffs raise tension).**
> Chapter 4, Scene 1: Mara confronts the archive keeper. He refuses to help
> but slips her a name: "The night watchman might talk." (tension 4→6,
> HOOK: she has a lead)
> Scene 2: Mara finds the night watchman — he's her father's old partner.
> He reveals the archive purge was ordered by the Council. (tension 6→8,
> HOOK: now she knows WHO)
> Scene 3: Mara confronts a Council member. They deny everything — but
> she notices they're wearing her father's signet ring. (tension 8→9,
> HOOK: they're lying, and they have his things)

Each scene hands off a hook that raises the next scene's stakes. The chapter's
tension climbs: 4→6→8→9. The chapter earns its arc.

**Discriminating check.** Read the chapter's scenes in sequence. Does each scene's
turn CREATE the next scene's goal? If you can shuffle scenes without breaking the
chapter, they're episodic — restructure until the order is locked by causality.
A chapter where scenes don't hand off is a list, not a story.
