---
name: novel-kit
description: >-
  Reliable long-form fiction work — drafting and editing novels. Use whenever a
  task involves writing a novel/chapter/scene, building a story/characters/plot,
  prose style or line-editing, continuity across a long manuscript, or critiquing
  fiction. Wraps the model's weak spots (praising its own prose without reading it
  cold, clichéd default phrasing, contradicting established canon over tens of
  thousands of words, structureless episodic scenes) in deterministic scanners +
  a design->draft->inspect->cold-read loop + a craft/failure learning system.
---

# novel-kit

You cannot feel your own prose the way a stranger does. You default to the
most-probable phrasing — clichés, filter words, adverb-laden dialogue tags,
told-not-shown emotion, monotone sentence rhythm — and then you call the result
"gripping" without ever reading it as a cold reader would. Across a long
manuscript you contradict your own canon (an eye colour changes, a name's
spelling drifts, a planted gun never fires). You write episodic scenes where
things merely happen, with no escalation. This skill removes those failure modes
with code and procedure. **Follow the loop. Do not trust your sense that it
"reads well" — scan it, check it against canon, and have it read COLD.**

There is no objective render of a novel. The two things that come closest, and
that this skill is built around:
- **Canon is machine-checkable.** Commit a fact to the story bible once; the
  continuity checker flags every later contradiction. (≈ blender-kit's render: the
  fact you can't argue with.)
- **A cold reader is the proxy for looking.** A fresh subagent that never saw your
  plan or intent reads the prose blind and reports where it got bored, confused,
  or felt the words before. That is how you "look at" fiction. You praising your
  own draft is not.

## Environment (this machine)
- Host Python: `python` → 3.10.6 (toolkit is stdlib-only; also runs on 3.14).
- Run a module from the `scripts/` dir so the package resolves:
  `cd scripts && python -m novelkit.<mod> <args>`.
- `novelkit/__init__.py` reconfigures stdout to UTF-8 — required, or the Windows
  cp1252 console crashes on the report glyphs (✓ ✗ • ⚠ …). Always invoke via
  `python -m novelkit.<mod>`, never by running a module file by path.
- Working files live in `_work/` (plans, bibles, drafts). Throwaway in `_tmp/`.

## THREE FIELDS
The work has three coupled fields; the loop builds and audits each, and they feed
each other:
- **CHARACTER** — a baseline person: traits + backstory + voice + want/need + an ARC
  (start-belief → end-belief). `character.baseline_gate` refuses thin characters;
  the fidelity audit checks they ACT in accordance with that baseline (SOP-08).
- **SCENE** — a scene has a purpose and **MOVES ≥1 character**: it resolves an action
  or changes a belief (the `moves` field). A scene that moves nobody is purposeless.
- **PLOT** — a malleable TIMELINE (the scene ledger) with **subplots** (each
  character's ARC realised as `@scene`-tagged beats) woven in. Re-audit it any time
  to confirm scenes still do their jobs and every arc still pays off (SOP-09).

## THE MANDATORY LOOP (never report a scene/chapter "done" until all of it has run)
```
GENRE PRE-PROCESS FIRST (SOP-10) — the instant you get a premise:
  python -m novelkit.genre "<premise>"      classify the genre (a hint — confirm by reading it)
  -> research the genre LIVE (WebSearch): its READER PROMISE, its CONVENTIONS /
     OBLIGATORY SCENES, and WHAT SUCCESSFUL COMPS DO. Write _work/<slug>_genre.md.
     This brief constrains comps, structure, the obligatory scenes in the ledger, and
     the genre clichés to avoid. (plan_novel.py runs the classify + scaffold for you.)

then DESIGN — PLOT FIRST (SOP-06); no prose until the gates pass:
  scaffold:   python scripts/plan_novel.py "<premise>" --title "..." --protagonist "..."
  PLOT comes first: logline · theme · comps · STRUCTURE beats · SCENE LEDGER (w/ a
                  `moves` + `ch` per scene + tension) · SUBPLOTS (arc beats @scene) ·
                  FLAGS (typed character flags) · setup/payoff · POV · research.
  CHAPTERS planned beforehand: scenes group into LONG (multi-scene) chapters; subplots
                  SPAN a couple of chapters (the `## CHAPTERS` table + the ledger `ch`).
  fill the BIBLE: each major character's traits, backstory, PHYSICALITY (a rendered
                  body + mannerism), voice, want/need, ARC; WORLDBUILDING (sensory/
                  cultural texture so the world goes ON THE PAGE); canon; forbidden.
  -> python -m novelkit.plan      _work/<slug>_plan.md        MUST PASS (plan complete, incl. CHAPTERS)
  -> python -m novelkit.character _work/<slug>_bible.md       MUST PASS (baseline incl. physicality)
  -> python -m novelkit.structure _work/<slug>_plan.md _work/<slug>_bible.md   (moves + escalation)
  -> python -m novelkit.plot      _work/<slug>_plan.md _work/<slug>_bible.md   (arcs pay off)
  -> python -m novelkit.chapters  _work/<slug>_plan.md _work/<slug>_bible.md   (long chapters; subplots span)
  -> python -m novelkit.flags     _work/<slug>_plan.md _work/<slug>_bible.md   (flag lifecycle)
  No scenes until these pass.

then DRAFT a scene against the plan + bible (prose craft = SOP-02). Render the
  WORLD and EMBODY the people on the page — don't leave them in the bible:
  write -> python -m novelkit.prose_scan <scene.md>           (excess: fix HARD flags)
        -> python -m novelkit.texture   <scene.md> --genre <g> (RICHNESS floor: not thin/white-room)

then INSPECT (never trust your own read):
  python -m novelkit.report <scene.md> _work/<slug>_bible.md _work/<slug>_plan.md --genre <g>
     = prose + TEXTURE + continuity + CHARACTER baseline + VOICE distinctiveness + SCENE
       moves + PLOT + CHAPTERS + FLAGS
  -> COLD READ (SOP-07): blind reader subagents — now incl. an IMMERSION + EMBODIMENT
     lens (is the world rendered, not just named? are the people bodies, not labels?).
  -> CHARACTER FIDELITY (SOP-08): each acting character audited against their dossier.
  -> VOICE DISTINCTIVENESS (SOP-13): blind-tag test — could a reader tell who's
     speaking with the dialogue tags removed? Revise interchangeable lines.
  -> REVISE against the scanners, the cold read, and the fidelity audit. Update the
     bible if canon changed; re-run plot audit if you moved/cut a scene.
  -> repeat until the deterministic gate PASSES, the cold read says "works", and the
     characters stay in character.
  -> THEN report, citing the reads you addressed (not your own opinion of it).
```
Passing the scanners is **necessary, not sufficient** — a scene can be clean of
smells and still be boring. The cold read decides whether it works. You may not
call a scene finished from code alone, and you may not call it finished on your
own say-so. "It works" requires a cold reader who said so.

## Hard rules
0. **DESIGN BEFORE PROSE.** Run SOP-06: scaffold + fill the PLAN and the BIBLE.
   `plan.design_gate()` must PASS. The anime-head lesson from blender-kit ports
   exactly: researching the *premise* is not enough — research the CRAFT
   (structure, genre conventions, failure modes) and commit a plan FIRST. Skip
   ONLY for a one-off paragraph exercise the user explicitly scopes as throwaway.
0b. **Plan the PLOT first, in CHAPTERS, before scenes.** PLOT is the first artifact:
   the SCENE LEDGER (timeline) + SUBPLOTS + FLAGS + setup/payoff. Group scenes into
   LONG (multi-scene) chapters planned beforehand; subplots SPAN a couple of chapters
   (`chapters.py` checks this). SCENE: every ledger row declares a `moves` — a scene
   that moves nobody is purposeless. PLOT audit: every arc beat dramatised, every arc
   resolved.
0c. **Build the CHARACTERS and the WORLD as renderable material.** Every major
   character needs a baseline INCLUDING `physicality` (a rendered body + mannerism, not
   just a name) — `character.baseline_gate` must PASS. The bible needs a `WORLDBUILDING`
   section (sensory/cultural texture). This exists so the world and people can go ON
   THE PAGE; thin, interchangeable people and a named-not-rendered world are the failure.
0d. **prose_scan punishes too-much; `texture` punishes too-little.** The kit's smell
   scanners all push toward terseness, so prose can pass every check and still be
   sparse (no worldbuilding, no character building). Run `texture` (genre profile) as
   the richness FLOOR, and lean on the cold read's IMMERSION + EMBODIMENT lens — density
   can't tell "named" from "rendered", so the eye decides. Render the world; embody the
   people. (Found by a reader, 2026-06-22; see references/failures/sparse-underbuilt-prose.md.)
1. **Commit canon to the bible, then never contradict it.** Every physical/biographical
   fact, world rule, timeline beat, character baseline, and planted setup goes in
   `_work/<slug>_bible.md`. Update it the instant canon legitimately changes.
   `continuity.py` and `character.py` are only as good as the bible you maintain.
2. **Run `prose_scan` on every scene; fix HARD flags.** Clichés, impossible dialogue
   tags, crutch-level densities, monotone rhythm. REVIEW flags are "go look" — judge
   by eye (an intentional cliché in dialogue is fine).
3. **Run `report` before calling a scene/chapter done** (prose + continuity +
   CHARACTER baseline + SCENE moves + PLOT audit). Re-run the PLOT audit whenever you
   move, cut, or add a scene — the timeline is malleable, so coverage can break.
4. **Do the COLD READ (SOP-07) AND the CHARACTER FIDELITY audit (SOP-08) — always.**
   Cold read: blind reader subagents, never shown the plan/intent; aggregate
   pessimistically (one reader's confusion is real). Fidelity: for each character
   acting in the scene, confirm they behave per their dossier — any change of belief
   must be EARNED on the page, not abrupt. Revise to both verdicts, not your impression.
5. **One voice per POV; no head-hopping.** Honour the POV & tense declared in the plan.
5b. **Every character sounds like a different person (SOP-13).** Declared voices must be
   specific + mutually distinct (`voice.distinctiveness_gate`, in `report`); in dialogue
   scenes run the VOICEPRINTS diagnostic and the BLIND-TAG cold read — could a reader tell
   who's speaking with tags removed? The model's default is one voice (its own) for the
   whole cast. Rewrite interchangeable lines from each character's worldview.
6. **On any failure: consult `LEARNINGS.md` + the relevant `references/` entry FIRST,**
   then `python -m novelkit.debug <error>`. Bounded retries (max 2) with the mapped
   fix, then a minimal repro + STOP. Never fake a passing scan or invent a cold read.
7. **Record a new craft learning only after a cold read VERIFIED it** (cite which
   read). An unverified "rule" poisons the catalog — same anti-poison rule as the
   other kits.

## Routing — pick the SOP, follow its numbered gates (no gate may be skipped)
| Task | SOP |
|------|-----|
| **FIRST when a premise arrives — categorise + research the GENRE** | `sops/10-genre-preprocess.md` |
| Then design + gate the plan (the no-prose-yet gate) | `sops/06-design-first.md` |
| Draft a new novel (full loop) | `sops/00-new-novel.md` |
| Edit / critique a manuscript the user brings | `sops/01-edit-manuscript.md` |
| Draft or revise a single scene | `sops/02-scene.md` |
| Build / audit CHARACTERS — baseline + in-character fidelity | `sops/08-character-fidelity.md` |
| Make character VOICES distinct — research, design gate, blind-tag cold read | `sops/13-character-voice.md` |
| Audit the PLOT — timeline, subplots, scene jobs (re-run after edits) | `sops/09-plot-audit.md` |
| Build the WORLD + check richness (worldbuilding, texture, embodiment) | `sops/11-worldbuilding-texture.md` |
| Plant / audit narrative FLAGS (introduction · romance · death) | `sops/12-flags.md` |
| Line-edit / prose-polish pass | `sops/05-revision-passes.md` |
| Run the adversarial COLD READ | `sops/07-critique-coldread.md` |
| A script/check failed | `sops/03-debug-failure.md` |
| Verify the toolkit / first run | `sops/04-env-verify.md` |

## The toolkit (`scripts/novelkit/`, run `python -m novelkit.<mod>` from `scripts/`)
- `plan_novel.py`  (entry) classify GENRE + scaffold a GENRE BRIEF + PLAN + BIBLE for a premise.
- `genre`       GENRE pre-process — classify a premise + assemble the genre brief
                (reader promise, obligatory scenes, exemplar moves, clichés) from the
                `references/genres/` knowledge base; flags what to research live (SOP-10).
- `plan`        scaffold the build plan + `design_gate()` (the no-prose-yet gate).
- `bible`       parse/scaffold the story bible (canon: characters, world, timeline,
                setup/payoff ledger, forbidden terms).
- `character`   CHARACTER field — `baseline_gate` (traits/backstory/PHYSICALITY/voice/
                want/need/arc), deterministic voice-rule scan, + in-character FIDELITY harness.
- `voice`       VOICE DISTINCTIVENESS — `distinctiveness_gate` (declared voices specific +
                mutually distinct; counts toward report pass/fail) + per-scene VOICEPRINTS
                (attribute dialogue, fingerprint each speaker, flag near-identical voices)
                + the BLIND-TAG cold-read harness. Catches everyone-sounds-the-same;
                can't judge GOOD (that's the cold read). See SOP-13.
- `manuscript`  split prose into chapters/scenes + word/sentence/rhythm stats.
- `prose_scan`  the deterministic prose-smell scanner — punishes EXCESS (filter words,
                clichés, said-bookisms, adverbs, intensifiers, repetition, rhythm). HARD/REVIEW.
- `texture`     the RICHNESS floor — COUNTERWEIGHT to prose_scan. Sensory density,
                world-term density, character EMBODIMENT, interiority ratio; genre-
                calibrated thin/ok/rich. Catches white-room/sparse; can't judge GOOD
                (that's the cold read's immersion lens). prose_scan punishes too-much;
                texture punishes too-little.
- `continuity`  validate prose against the bible: attribute contradictions
                (gender-aware pronoun resolution), name drift, forbidden terms,
                dangling setups / unfired Chekhov's guns.
- `structure`   SCENE field — ledger completeness (goal/conflict/turn + `moves` a
                character) + tension-curve diagnostics (flat run, sagging middle, late-climax).
- `plot`        PLOT field — timeline + subplot AUDIT: every scene moves someone,
                every arc beat is `@scene`-placed and dramatised, every arc resolves.
- `chapters`    CHAPTER layer — scenes live INSIDE chapters; each chapter needs a planned
                DIRECTION (opens→turns→lands+hook) and an internal tension arc that builds;
                every chapter advances a subplot; subplots SPAN a couple of chapters
                (`## CHAPTERS` table w/ `direction` + ledger `ch`).
- `flags`       narrative FLAGS — typed character signals (introduction/romance/death…)
                with a raised→paid|broken lifecycle; flags dangling/mis-ordered + death-
                flag telegraph. See references/flags.md.
- `critique`    BLIND cold-read payload + verdict SCHEMA (incl. immersion/embodiment); aggregate.
- `report`      one INSPECT gate: prose + texture + continuity + character + VOICE +
                structure + plot + chapters + flags  (pass `--genre <g>` so texture uses the
                right profile).
- `debug`       classify a failing run against LEARNINGS.md.

## References & per-key learning loop
- `references/genres/` — per-genre knowledge base (reader promise, obligatory scenes,
  exemplar moves, tropes, clichés). `genre.py` reads it; SOP-10 augments it with live
  research and records verified findings back (anti-poison).
- `references/craft/` — craft principles (scene = goal/conflict/turn; show-don't-tell;
  character want/need/arc; distinct character voice / the blind-tag test; enter late/
  leave early), each cited + before/after pair.
- `references/cliches/` — banned-phrase lists; `prose_scan` auto-loads any `*.txt`
  here, so growing the list strengthens the scanner.
- `references/structure/` — structure templates (three-act, Save the Cat, story
  circle) with when-to-use.
- `references/failures/` — known failure modes (sagging middle, info-dump, white-room,
  talking-heads, head-hopping, Mary Sue, deus ex machina) + the guard for each.
- `LEARNINGS.md` — bug/error fixes keyed by `error_signature`.
- Consult the relevant entry BEFORE drafting/editing; after a cold read VERIFIES a
  craft learning, append it (cite the read). Record only verified learnings.
