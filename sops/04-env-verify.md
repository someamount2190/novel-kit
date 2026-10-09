# SOP-04 — Verify the toolkit / first run

## Gate 1 — Python
```
python --version        # expect 3.10.x on this machine (stdlib-only; 3.14 also fine)
```
No third-party packages are needed. If `python` is missing, `py -3` or `python3`
work too — the toolkit is pure stdlib.

## Gate 2 — package imports + UTF-8
```
cd scripts
python -c "import novelkit, novelkit.genre, novelkit.prose_scan, novelkit.texture, novelkit.continuity, novelkit.structure, novelkit.plot, novelkit.chapters, novelkit.flags, novelkit.character, novelkit.voice, novelkit.plan, novelkit.bible, novelkit.critique, novelkit.report, novelkit.debug; print('novelkit OK')"
```
Importing the package reconfigures stdout to UTF-8 (Windows cp1252 otherwise crashes
on report glyphs). Always run modules as `python -m novelkit.<mod>`.

## Gate 3 — self-test on the bundled samples (the three fields)
```
python -m novelkit.genre "a detective hunts a killer" # detects mystery + shows KB promise
python -m novelkit.prose_scan ../references/samples/bad.md     # exit 1, many HARD flags
python -m novelkit.prose_scan ../references/samples/good.md    # exit 0, passes
python -m novelkit.plan      ../references/samples/plan_filled.md                              # RESULT: PASS
python -m novelkit.character ../references/samples/bible.md                                    # baseline incl. physicality: PASS
python -m novelkit.voice     ../references/samples/bible.md                                    # voices specific + mutually distinct: PASS
python -m novelkit.structure ../references/samples/plan_filled.md ../references/samples/bible.md  # SCENE moves + tension rises
python -m novelkit.plot      ../references/samples/plan_filled.md ../references/samples/bible.md  # PLOT audit: PASS
python -m novelkit.chapters  ../references/samples/plan_filled.md ../references/samples/bible.md  # CHAPTER layer: PASS
python -m novelkit.flags     ../references/samples/plan_filled.md ../references/samples/bible.md  # FLAGS lifecycle: PASS
python -m novelkit.texture   ../references/samples/good.md --genre literary-fiction            # furnished (not thin): PASS
python -m novelkit.continuity ../references/samples/scene_canon_break.md ../references/samples/bible.md   # catches eye-colour + forbidden + drift
```
If all behave as annotated, the harness is healthy.

## Gate 4 — directories
- `_work/` — your plans, bibles, drafts (persist).
- `_tmp/` — throwaway test inputs.
Both are created on demand; nothing else to install.
