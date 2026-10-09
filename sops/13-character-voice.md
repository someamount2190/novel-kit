# SOP-13 — VOICE DISTINCTIVENESS: make every character sound like a different person

A reader should be able to tell who's speaking with the dialogue tags removed. The
model's default failure is the opposite: every character speaks in its own
competent, mid-length, lightly-hedged register, so the cast is interchangeable and
the dialogue is really the author talking to themselves. This SOP makes voice a
designed, researched, checkable property — not something you assert after the fact.
It complements SOP-08: SOP-08 asks "does X sound like X / never break X's rules?";
this asks "do X and Y sound like DIFFERENT people?" See
`references/craft/distinct-character-voice.md`.

## Gate 1 — RESEARCH the character's voice (don't default it)
Voice is the surface of a worldview, so derive it from the dossier, then research how
real and fictional people in that situation actually talk:
1. **From the bible** — read each major character's `traits`, `backstory`, `wants`,
   `needs`. A voice must be CAUSED by these (the guilt-ridden ex-warden clips her
   sentences and never names a feeling; the cowardly engineer hides in latinate
   regulation-speak). If you can't trace the voice to the personality, it's a costume.
2. **Live research (WebSearch / WebFetch)** when a character belongs to a specific
   register you don't command — a 1890s harbour master, a trauma surgeon, a teenager
   in a given subculture, a non-native English speaker's syntax. Search idiolect /
   register / "how X talk", real transcripts/interviews, and dialect notes; cite ≥2
   sources, and avoid caricature (research the rhythm and diction, not a stereotype).
3. **Pin the levers** for each character, concretely: diction (plain/latinate, slang),
   sentence rhythm (short-blunt vs long-subordinated), hedging vs assertion,
   question vs command, **what they will NOT say**, and how they shift under pressure.

## Gate 2 — DESIGN GATE: declared voices specific + mutually distinct (deterministic)
Write each character's `voice:` field in the bible as ≥2 *specific* markers from
Gate 1 (e.g. `clipped; nautical metaphors; never swears`), then:
```
cd scripts && python -m novelkit.voice _work/<slug>_bible.md
```
FAIL if any voice is generic ("friendly and casual" describes no one) or if two
characters' voice markers overlap too far (interchangeable on paper → interchangeable
on the page). Fix by re-rooting the weaker voice in that character's distinct
personality. This gate also runs inside `report.py` and counts toward its pass/fail.

## Gate 3 — PROSE VOICEPRINTS: are the speakers different on the page? (per scene)
After drafting a dialogue scene:
```
python -m novelkit.voice _work/<slug>_bible.md --scene _work/<scene>.md
```
Attributes dialogue to speakers (by name tag; one speaker per paragraph) and prints a
fingerprint per speaker — sentence length, contraction rate, hedge rate, question %,
formality, profanity. A `⚠` marks two speakers who are *metrically* near-identical
(likely one voice). Attribution is heuristic — **confirm the speakers by eye**. This
is a REVIEW diagnostic (a floor that catches everyone-sounds-the-same); it does NOT
fail the report. Metrics can't tell "different" from "good".

## Gate 4 — the BLIND-TAG TEST (the real verdict — cold read, always)
Distinct-on-metrics is necessary, not sufficient. Spawn blind cold-read auditor(s)
like SOP-07, focused on voice. Get the payload + schema:
```
python -m novelkit.voice _work/<slug>_bible.md --payload _work/<scene>.md
python -m novelkit.voice --schema
```
Spawn one (or more) **Agent** (general-purpose) with the payload (voice signatures +
scene) and the verdict schema. It runs the blind-tag test and returns:
`distinguishable`, `interchangeable_lines`, `author_voice_lines`, `per_character`
(on_signature + note), `verdict` (distinct / some-blur / interchangeable). Aggregate
with `voice.aggregate([...])` — `interchangeable` from ANY reader stands.

## Gate 5 — REVISE the offending lines
For every `interchangeable_line` or `author_voice_line`: rewrite it from that
character's worldview — change WHAT they notice and HOW they'd phrase it, not just
bolt on a verbal tic. A catchphrase is not a voice. Then re-run Gate 3 and a FRESH
Gate 4 reader; repeat until the verdict is `distinct`.

## Gate 6 — feed it back (anti-poison)
- If a character's voice legitimately evolves (trauma clips a once-florid speaker),
  update the bible `voice:` field so SOP-08 fidelity and this gate stay in sync.
- Record a voice-craft learning in `LEARNINGS.md` ONLY after a cold read verified it
  (cite the read) — e.g. a register technique that a blind reader confirmed made two
  characters separable. An unverified "rule" poisons the catalog.
