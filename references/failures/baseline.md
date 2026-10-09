# Failure modes — the model's recurring fiction mistakes + the guard

Consult before drafting (SOP-02) and before shipping a chapter. Each entry: the
smell, why the model falls into it, and the GUARD (tool or procedure that catches it).

## Sagging middle
Act II loses tension; scenes become episodic. *Cause:* the model has no felt sense of
escalation and writes pleasant connective tissue. *Guard:* `structure.py` flags a
middle-third mean tension below the opening third, and flat tension runs. Every Act
II scene needs a turn that ratchets up.

## Told-not-shown emotion
Naming feelings ("she was devastated") + body clichés ("heart pounded"). *Cause:*
most-probable continuation of an emotional beat. *Guard:* `prose_scan` told-emotion
+ cliché categories; `references/craft/show-dont-tell.md`.

## Clichéd / most-probable phrasing
"Shiver down her spine", "let out a breath she didn't know she was holding."
*Guard:* `prose_scan` cliché list (extend via `references/cliches/`); the cold read's
FAMILIARITY question.

## Said-bookisms & adverb tags
"he ejaculated", "she said angrily", and impossible tags ("'No,' she smiled").
*Guard:* `prose_scan` said_bookisms (impossible tags are a HARD flag). Default to
*said/asked*; let the line carry the tone.

## Uniform character voice
Every character speaks in the same register (the model's). *Cause:* no committed
voice signature. *Guard:* the plan's VOICE SIGNATURE per character; the cold read's
VOICE question; read each character's lines in isolation (SOP-05 Pass 4).

## Continuity drift over length
Eye colour changes, a name's spelling drifts, a date contradicts. *Cause:* the model
can't hold canon across tens of thousands of words. *Guard:* the story bible +
`continuity.py` (gender-aware attribute/name/forbidden/ledger checks). Maintain the
bible as canon evolves.

## Chekhov violations (dangling setup / unplanted payoff)
A gun is planted and never fired, or a payoff arrives with no setup. *Guard:* the
bible SETUP/PAYOFF ledger + `continuity.py` ledger coverage.

## Info-dump / "as you know, Bob"
Backstory or world mechanics delivered in a block, or via characters telling each
other what they both already know. *Guard:* reveal through action/conflict; the cold
read's confusion + skim questions; SOP-05 Pass 4 (cut dialogue that only informs).

## White-room / talking-heads
Scenes with no setting or physical grounding; disembodied dialogue. *Guard:* the
cold read's CONFUSION ("where are we?"); ground each scene in place + the POV body.

## Head-hopping
POV slips between characters within a scene. *Guard:* the plan's POV & TENSE
discipline; one viewpoint per scene; the cold read's VOICE question.

## Mary Sue / no real obstacle
The protagonist wins too easily; conflict is cosmetic. *Guard:* `structure.py`
valence check (not all wins); each ledger row needs real CONFLICT and a costly turn.
