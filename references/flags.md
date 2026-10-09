# Narrative FLAGS — taxonomy + craft (researched 2026-06-22)

A "flag" comes from game / visual-novel programming: an EVENT FLAG is a condition
that, once RAISED, triggers a later event (a cutscene, a route, a boss, an ending).
Fiction borrowed the metaphor (esp. anime / light-novel / isekai culture). A flag is
a planted signal with a lifecycle:

    raised  →  paid (triggered)   |   broken (deliberately subverted)

`flags.py` audits declared flags (plan `## FLAGS`): every raised flag must be paid or
marked broken (else DANGLING — a promise the reader clocked), the payoff must come
AFTER the raise (foreshadow precedes), and the owner must be a real character.

Sources: TV Tropes *Event Flag*; CBR (shonen death-flags, "how to notice"); GameRant/
ComicBook (underpowered-hero lists); JeremyVarner.com & ResetEra (death-flag cliché);
VN flag-system docs (TyranoBuilder, Ren'Py/LemmaSoft, QooApp "Flags").

## introduction flag
How a character ENTERS signals their role/importance and plants what they're FOR. In
VNs the new character portrait literally marks the flag. Craft: a character introduced
with weight (a loaded first action/line) promises a payoff; pay it. A vivid intro that
never returns is a dangling promise; a major payoff from someone never properly
introduced feels unearned.

## romance flag
An event that "sparks the relationship" (the meet, the charged moment, the choice). In
gal-games you RAISE love flags to unlock a route. Craft: a raised romance flag should
ESCALATE and PAY OFF (the union / HFN — see the romance genre entry). A raised romance
flag that evaporates cheats the reader; a `broken` romance flag denies the genre's core
promise (fine in tragedy, fatal in romance). Don't raise one you won't honour.

## death flag
Foreshadows a character's death. Classic tells (so well-known they TELEGRAPH):
- talking about plans AFTER the war / "when this is over, I'll…"
- showing a photo of loved ones; naming the partner waiting at home
- "this is my last job"; a sudden uncharacteristic act of kindness or peace
- a backstory/name handed to a minor character right before a battle
Purpose: raise stakes, prime grief. **Cliché risk:** death flags are the genre's
worst-kept secret — played straight they kill the surprise (a "cheap pull at the heart-
strings"). `flags.py` emits a TELEGRAPH advisory for a death flag paid straight.
**Subversion:** flag a character heavily and let them LIVE; kill an unflagged one. But
note (ResetEra/JeremyVarner): over-subversion is now itself a cliché — readers who
know the trope also know the subversion. So: make the tell SUBTLE, or subvert with
intent, and don't lean on the flag to do the emotional work the scene should.

## other types flags.py recognises
betrayal · power-up · redemption · foreshadow · reveal · rivalry — same lifecycle.

## how to declare (plan `## FLAGS`)
    - <type> | <character> | raised @<scene> | (paid|broken) @<scene> — <note>
e.g.
    - introduction | Toma | raised @1 | paid @8 — the overlooked boy is the one who matters
    - death | Sera | raised @6 | broken @8 — heavily flagged, SURVIVES (deliberate subversion)

Declare only the flags the story actually has. Forcing a romance flag onto a story with
no romance (or onto an inappropriate pairing) invites the very harem/fanservice clichés
the isekai genre entry warns against — judgment over checklist.
