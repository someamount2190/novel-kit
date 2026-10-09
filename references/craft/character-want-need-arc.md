# Craft: want vs need, and the arc that connects them

**Principle.** A character who works has two engines pulling against each other: a
**want** (the external, conscious goal that drives the plot — catch the killer, win
the case) and a **need** (the internal, often unconscious lack the story is really
about — to forgive herself, to trust again). The **arc** is the line between a
start-belief and an end-belief; the plot forces the character to choose between the
want and the need, and the climax is usually where the need wins (or tragically
doesn't). Traits and backstory are the *evidence* for all three — the wound that
created the need, the habits that pursue the want. (Sources: Truby, *The Anatomy of
Story*; Weiland, *Creating Character Arcs*; Egri, *The Art of Dramatic Writing*.)

**Why the model needs it.** The model writes capable, agreeable, traitless people
who do whatever the scene requires, and it confuses "want" with "need" so the arc
never lands. `character.baseline_gate` forces traits + backstory + voice + want +
need + arc to exist before any scene; the fidelity audit (SOP-08) checks the prose
honours them and that change is *earned*; `plot.py` checks the arc is realised as
`@scene`-tagged beats and actually resolves.

**Thin (interchangeable).**
> Mara was a determined detective who wanted to solve the case. She was good at her
> job and cared about justice.

No flaw, no wound, no internal contradiction — nothing to violate, so nothing to track.

**Baselined (want ≠ need, arc visible).**
> traits: stubborn, guilt-ridden, distrustful of authority
> backstory: her sister drowned in the flood she was meant to prevent
> wants: name who opened the gates  (external — drives the plot)
> needs: forgive herself for surviving  (internal — what the book is about)
> arc: "the truth is mine to carry alone" -> "the truth must be shared to mean anything"

Now every scene can ask: does she pursue the want, and is she nudged toward the need?

**Discriminating check.** Name the want and the need in one line each; they must be
different and ideally in tension. Then trace the arc through the SUBPLOTS: at least a
turn and a resolution beat, each on a real scene that MOVES her (`plot.py`). If want
== need, or the arc has no beats, the character is decoration, not a character.
