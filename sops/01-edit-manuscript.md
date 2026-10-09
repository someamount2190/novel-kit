# SOP-01 — Edit / critique a manuscript the user brings

The user hands you existing prose (a scene, chapter, or whole novel). Do NOT start
line-editing — diagnose first, top-down: structure → continuity → scene → prose.
Fixing commas in a scene that should be cut wastes everyone's time.

## Gate 1 — ingest + map
```
cd scripts && python -m novelkit.manuscript <path>
```
Confirm the chapter/scene split and word balance look right. If the file uses
unusual breaks, note it. Read the whole thing once before judging.

## Gate 2 — reconstruct the BIBLE from the text
Build `_work/<slug>_bible.md` (scaffold: `python -m novelkit.bible --scaffold "<title>"`)
by reading off the canon the manuscript ALREADY asserts: character attributes as
first stated, names/aliases, world rules, dates, the setups it plants. This is the
baseline continuity is measured against — capture the *first* assertion of each
fact, then `continuity.py` finds where the text later breaks its own canon.

## Gate 3 — DEVELOPMENTAL pass (highest altitude first)
- Reconstruct the SCENE LEDGER from the actual text into a plan file; run
  `python -m novelkit.structure`. Where does tension sag? Is the climax late? Do
  scenes have goals/turns, or do things just happen?
- COLD READ (SOP-07) representative scenes (opening, a middle scene, the climax) to
  locate where it loses a reader.
- Report the developmental findings (structure, pacing, character, stakes) BEFORE
  touching prose. Get the user's priorities.

## Gate 4 — CONTINUITY pass
```
python -m novelkit.continuity <path> _work/<slug>_bible.md
```
Surface contradictions, name drift, forbidden terms, dangling/unplanted setups.
Confirm each suspect by eye (false positives expected) and list real ones with line
numbers.

## Gate 5 — LINE pass (SOP-05)
Only once structure/continuity are agreed. Run `prose_scan`, then the revision-pass
order in SOP-05.

## Gate 6 — report
Separate developmental notes from line notes. Cite line numbers and the cold reads.
Never rewrite wholesale without flagging it — the prose is the user's voice, not yours.
