# SOP-10 — GENRE pre-process (runs FIRST, before design)

The moment a user gives a premise, before any planning: categorise the genre and
research what that genre PROMISES, REQUIRES, and how successful examples deliver it.
Designing genre-blind is how you write a mystery that cheats, a romance with no
payoff, a thriller that sags. The genre brief constrains everything downstream.

## Gate 1 — classify (deterministic hint, then YOUR judgement)
```
cd scripts && python -m novelkit.genre "<premise>"
```
It returns ranked genres from premise signals. This is a HINT, not the verdict — you
understand genre better than keywords. Confirm or override by reading the premise;
many premises are cross-genre (a literary mystery, a romantasy). If the signal is
weak/absent, decide the genre yourself or ask the user. Pin it with `--genre <name>`.
(`plan_novel.py` runs this automatically and writes `_work/<slug>_genre.md`.)

## Gate 2 — load the knowledge base
The brief pulls `references/genres/<slug>.md` if it exists (reader promise,
obligatory scenes, exemplar patterns, tropes, clichés-to-avoid). If the entry is
MISSING or thin (the brief says so), you research from scratch in Gate 3.

## Gate 3 — LIVE research (this is the "research" step — don't skip it)
Use **WebSearch / WebFetch** to learn three things, citing sources:
1. **Conventions / obligatory scenes (the genre "SOP")** — what the genre MUST
   deliver. Confirm across **≥2 independent sources** (craft sites, genre guides);
   don't trust a single blog. Adversarially sanity-check claims that sound like one
   author's hobbyhorse.
2. **What readers actually like (the promise)** — search reviews, "best <genre>
   novels", reader communities, "why readers love <genre>". Capture the EMOTIONAL
   payoff people return for, in their words.
3. **What successful stories do** — pick 2-4 current/landmark comps in the precise
   sub-genre and note the concrete moves they share (structure, obligatory beats,
   how they open, how they pay off).
For an unusual or blended genre with no KB entry, this gate is the whole job.

## Gate 4 — write the GENRE BRIEF
Fill `_work/<slug>_genre.md`: READER PROMISE · CONVENTIONS / OBLIGATORY SCENES ·
WHAT SUCCESSFUL STORIES DO (comps + shared moves) · TROPES TO HONOUR · CLICHÉS TO
AVOID · RESEARCH LOG (with source citations + anything that surprised you vs the KB
baseline).

## Gate 5 — feed it forward (the brief is a constraint, not a note)
- The plan's **AUDIENCE & COMPS** and **RESEARCH & FAILURE MODES** must be consistent
  with the brief; cite the comps you found.
- Let the genre pick the **STRUCTURE** (see `references/structure/` + the brief's
  structure note).
- The **obligatory scenes** must appear in the **SCENE LEDGER** — a mystery needs the
  fair reveal, a romance the black moment + reunion. A missing obligatory scene is a
  broken promise.
- Add the genre's specific clichés to `references/cliches/<genre>.txt` so `prose_scan`
  flags them automatically; add genre failure modes to your SOP-02 watch.

## Gate 6 — record (only what a source confirmed)
If you researched a genre with no/partial KB entry, write or extend
`references/genres/<slug>.md` (+ the INDEX line) with the verified conventions/
promise/exemplars — and ONLY what a source actually confirmed (anti-poison rule).
A future premise in this genre then starts from your research, not from scratch.

→ Then SOP-06 (design-first): the plan + bible, now genre-aware.
