# SOP-12 — Narrative FLAGS (introduction · romance · death · …)

A flag is a typed, character-attached signal with a lifecycle: **raised → paid
(triggered) | broken (subverted)**. Borrowed from visual-novel event-flags. Full
taxonomy + craft + sources: `references/flags.md`. Optional but a strong way to plant
and pay character beats — declare only the flags the story actually has.

## Gate 1 — declare in the plan (`## FLAGS`), plot-first
One per line:
```
- <type> | <character> | raised @<scene> | (paid|broken) @<scene> — <note>
```
Types audited specially: **introduction** (the entrance that plants what a character is
for → pays later), **romance** (the spark → escalates → pays the union; don't raise one
you won't honour), **death** (foreshadows a death → must be raised BEFORE it). Others:
betrayal/power-up/redemption/foreshadow/reveal/rivalry.

## Gate 2 — audit the lifecycle
```
cd scripts && python -m novelkit.flags <plan.md> <bible.md>
```
FAILS on: a DANGLING flag (raised, never paid or marked broken — a promise the reader
clocked); a payoff at/before the raise (foreshadow must precede); an unknown owner; an
unplaced flag. Advises on: a death flag paid STRAIGHT (telegraphs — make the tell
subtle or subvert), a broken romance flag (denies the genre's payoff).

## Gate 3 — death flags: subtlety or subversion, not reflex
Death flags are the genre's worst-kept secret; played straight ("after the war I'll…",
the family photo, the last job) they telegraph and cheapen the death. Either bury the
tell so only a re-read reveals it, OR subvert (flag heavily, let them live; kill the
unflagged) — but know that over-subversion is itself now a cliché, so subvert with
intent. Mark a deliberate non-death `broken` so the audit reads it as craft, not a
dangling promise.

## Gate 4 — don't force flags (judgment over checklist)
Declaring a romance flag for a pairing the story doesn't have (or shouldn't — e.g. an
age-inappropriate one) invites the harem/fanservice clichés the genre guards warn
against. Plant the flags the story earns; leave the rest.
