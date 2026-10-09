# SOP-11 — Worldbuilding & texture (render the world, embody the people)

The kit's smell-scanners all punish EXCESS, so prose can pass every check and still be
sparse — no worldbuilding, no character building. This SOP is the counterweight. See
`references/craft/worldbuilding-and-embodiment.md` and
`references/failures/sparse-underbuilt-prose.md`.

## Gate 1 — build the material at DESIGN time (so it can reach the page)
In the bible:
- `## WORLDBUILDING` — look & feel (sensory signature), daily life (what the central
  rule MEANS in practice), social order, and 3-5 concrete texture details (a food, a
  street sound, a ritual, an object). Naming "the Weave" is not worldbuilding; this is.
- each major character's `physicality` — a RENDERED body + a signature mannerism (this
  is now required by `character.baseline_gate`).
For immersive genres (isekai/fantasy/sf/horror) the genre brief (SOP-10) names the
reader's appetite for immersion — honour it.

## Gate 2 — put it on the page (drafting, SOP-02)
- Reveal the world through USE and the POV's perception, never an info-dump: tie each
  rule to a daily, sensory consequence; let one concrete object carry the world.
- Embody every character who acts — including the POV (easy to forget from inside them).
  Reuse each mannerism so it becomes characterisation. Let secondary characters speak.

## Gate 3 — the texture FLOOR (deterministic, coarse)
```
cd scripts && python -m novelkit.texture <scene.md> --genre <genre>
```
Reports sensory density, world-term density, character EMBODIMENT, interiority ratio,
genre-calibrated thin/ok/rich. It catches a white-room — but it CANNOT tell "named"
from "rendered" (it will rate a name-dropping scene "rich"). Treat a pass as "furnished
enough to look at", never as "vivid". A `thin` verdict is a real problem; a `rich`
verdict is necessary, not sufficient.

## Gate 4 — the real judge: the cold read's IMMERSION + EMBODIMENT lens (SOP-07)
The blind reader now answers: *can you see/hear/smell this place, or is it just named?*
and *do the people have bodies/faces/mannerisms, or are they labels?* This is how a
human catches sparseness (it's how this whole failure was caught). If the aggregate has
`world_vivid=false` or any `embodiment_problems`, REVISE — render the thin spots, give
the unembodied characters a body and a beat — and re-read with a fresh reader.
