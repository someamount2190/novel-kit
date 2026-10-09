# Craft: distinct character voice (the blind-tag test)

**Principle.** In good dialogue you can delete every "X said" tag and still know who
is speaking, because each character's lines carry a personality. Voice is not an
accent or a catchphrase; it is the surface of a worldview — what a person notices,
what they refuse to say, how long their sentences run, whether they hedge or
command, joke or instruct, abstract or concrete. A clipped, guilt-ridden ex-warden
and an over-formal bureaucrat *cannot* share a sentence rhythm, because they don't
share a way of moving through the world. The levers that make voice measurable and
controllable: **diction** (plain vs latinate, slang vs formal), **rhythm** (short
and blunt vs long and subordinated), **hedging vs assertion** (maybe/sort of/I guess
vs flat declaratives), **question vs statement**, **what they won't say** (the
ex-soldier who never names a feeling; the diplomat who never says no), and
**register under pressure** (who gets terser, who gets more elaborate). (Sources:
Robert McKee, *Dialogue*; Sol Stein, *Stein on Writing*; James Scott Bell, *How to
Write Dazzling Dialogue*.)

**Why the model needs it.** Left to its defaults, the model writes every character
in one register — its own competent, mid-length, lightly-hedged narrator voice — so
the cast is interchangeable and the dialogue is really the author talking to
themselves in different mouths. It will also *assert* that the voices are distinct
without ever running the blind-tag test on its own prose. Two guards: `voice.py`'s
`distinctiveness_gate` refuses a cast whose DECLARED voices are generic or duplicated
at design time; `voice.py`'s voiceprints fingerprint each speaker's attributed
dialogue (sentence length, contractions, hedges, questions, formality, profanity)
and flag speakers who are metrically indistinguishable. Neither can judge whether the
voices are *good* — only the cold-read blind-tag test (SOP-13) decides that.

**Thin (one voice, three names).**
> "I think we should probably go soon," Mara said. "It's getting late."
> "Yeah, I think you're right, we should get going pretty soon," Elias said.
> "I guess we don't really have a lot of time," Mara said.

Swap the tags and nothing changes. Everyone hedges ("I think", "probably",
"pretty"), everyone runs the same medium sentence, no one has a way of speaking.

**Distinct (voice = personality on the surface).**
> "Tide's turning. Hour, maybe. Then the lower road's gone." Mara didn't look up.
> "I must consult the relevant ordinance before any determination can be made,"
> Elias said, squaring the papers. "Procedure exists precisely so responsibility is
> properly apportioned."
> "Talk plain," Mara said. "Who opened the gates?"

Cover the tags: the blunt fragments are the guilt-ridden warden; the latinate,
agency-dodging clauses are the bureaucrat hiding behind regulation. Diction, rhythm,
and what each will/won't say do all the work.

**Discriminating check.** Run the blind-tag test: remove every dialogue tag and read
the lines cold — can you still assign each one? Any line you could move to another
character's mouth with no loss is a failure; rewrite it from that character's
worldview (change what they notice and how they'd phrase it, not just add a verbal
tic). At design time, each major character's `voice` field must name ≥2 *specific*
markers that differ from every other character's — "friendly and casual" describes
no one. See SOP-13 for the full procedure.
