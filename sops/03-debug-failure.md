# SOP-03 — A script / check failed

## Gate 1 — classify against memory FIRST
```
cd scripts && python -m novelkit.debug "<paste the error / traceback>"
```
It matches known signatures in `../LEARNINGS.md` + a baseline catalog and prints the
mapped fix. Also skim `LEARNINGS.md` directly for near-misses.

## Gate 2 — the usual suspects (this toolkit)
- **UnicodeEncodeError / charmap** — you ran a module by file path instead of
  `python -m novelkit.<mod>`, so `__init__`'s UTF-8 reconfigure didn't run. Use `-m`.
- **ModuleNotFoundError: novelkit** — run from the `scripts/` dir.
- **no SCENE LEDGER table found** — the plan needs a markdown pipe table under a
  `## SCENE LEDGER` heading with a header row. Re-scaffold if unsure.
- **design gate FAIL** — expected when the plan has gaps; it's the gate doing its
  job, not a bug. Fill the flagged sections.
- **continuity false positives** — a second character legitimately shares an
  attribute, or an intentional rename. Confirm by eye; add `pronouns:`/`gender:` to
  the bible character to sharpen pronoun resolution, or accept the suspect and move on.
- **FileNotFoundError** — manuscript/bible/plan paths are relative to your CWD, not
  to `scripts/`.

## Gate 3 — bounded retries, then STOP
Apply the mapped fix and retry at most twice. If still failing, build a MINIMAL
repro (smallest input that triggers it), state what you tried, and STOP — do not
fake a passing scan or fabricate a cold read.

## Gate 4 — record (only after a clean run verifies the fix)
Append to `LEARNINGS.md` with an `error_signature:` (a regex/substring `debug` can
match) and a one-line `fix:`. Anti-poison rule: record only fixes a real run confirmed.
