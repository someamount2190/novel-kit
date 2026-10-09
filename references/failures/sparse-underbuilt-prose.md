# Failure mode: sparse / under-built prose (no worldbuilding, no character building)

**The smell.** The prose is clean — passes prose_scan, no clichés, good rhythm — and
still feels thin. The world is NAMED but never rendered (terms and systems referenced,
never made physical); the cast are names with dialogue, not bodies with mannerisms.
Atmospheric and interior, but you can't SEE the place or the people.

**Why the model does it.** Two compounding causes:
1. *Register default.* The model reaches for a literary-minimalist voice — short,
   withholding, heavy on interiority and implication. Valid for literary fiction;
   it BETRAYS immersive genres (isekai/fantasy/sf), whose promise is a rendered world.
2. *Tooling bias.* Every smell-scanner (prose_scan) punishes EXCESS — clichés, filter
   words, adverbs, purple prose. So every deterministic force pushes toward terseness,
   and nothing rewards furnishing. The model optimises to the scanners and goes spare.

**The guard (three layers — no single one suffices):**
- DESIGN forces the material to exist: the bible's `WORLDBUILDING` section (sensory/
  cultural texture) + a REQUIRED per-character `physicality` (rendered body + mannerism).
  You can't put on the page what the design never built. (SOP-06.)
- `texture.py` is a coarse FLOOR (sensory/world/embodiment density, genre-calibrated).
  It catches a true white-room — but it CANNOT tell "named" from "rendered" (it rated a
  deliberately-sparse draft "rich" because it name-dropped systems and used action-body
  words). Necessary, not sufficient.
- The COLD READ's IMMERSION + EMBODIMENT lens is the real detector — judgment, the way a
  human catches it: "can you see/smell this place? do these people have bodies?" (SOP-07.)

**Before (named, not built):**
> The Rite read no Class. The king dismissed him. Toma went down to the lower city.

**After (rendered + embodied):**
> The basin's milk-pale glow drew back from his hand the way light leaves a room. The
> king — iron-grey, undyed wool, not a jewel on him — folded his hands once. "You are
> not a hero, son. You are the cost of one." On the way out a steward pressed a flat
> iron token into his palm, blank where a sigil should be, still warm from another
> discarded boy.

**Discriminating check.** Run `texture --genre <g>`; then ask the cold read whether the
world is rendered and the people embodied. If a named character has no body/face/
mannerism on the page, or the setting is a name with no sensory life, it's under-built —
even if every other gate is green.

*Recorded after a reader caught it on a clean-but-sparse isekai draft (2026-06-22).*
