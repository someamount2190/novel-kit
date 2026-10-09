# LEARNINGS — novelkit bug/error fixes

Keyed by `error_signature` (a regex/substring `novelkit.debug` can match). Append a
new entry ONLY after a clean run verifies the fix (anti-poison rule). Format:

```
## <short title>
error_signature: `<regex or substring>`
fix: <one line>
verified_by: <command/run that confirmed it>
```

---

## Windows console crashes printing report glyphs
error_signature: `UnicodeEncodeError.*charmap`
fix: Run modules as `python -m novelkit.<mod>` so `novelkit/__init__.py` reconfigures stdout to UTF-8. Don't execute a module file by path without the package init.
verified_by: prose_scan on _tmp/sample_bad.md printed ✓/✗/⚠ glyphs cleanly after the __init__ reconfigure (2026-06-21).

## Continuity missed pronoun-referenced attribute (eyes/hair)
error_signature: `continuity.*pronoun|missed.*eye colour`
fix: Attribute checks use gender-aware focal tracking — eye/hair colour is usually given via "Her/His ...", not the character's name. continuity._infer_genders + the recent[F/M/X] buckets resolve the pronoun; add `pronouns: she/her` to a bible character to make it exact. A fixed sentence-distance window does NOT work (the name may be 10+ sentences back).
verified_by: scene2 (`Her green eyes` vs canon grey) flagged at L9 after gender-aware resolution; clean prose did not false-positive (2026-06-21).

## Continuity attribute false positive on "gaze" + generic colours
error_signature: `attribute.*false positive|dark basin|gaze.*colour`
fix: Dropped "gaze" from CHECKABLE_ATTRS eye nouns (bible.py). "dark/pale gaze" near a named character — and generic colours describing nearby objects ("dark basin") — produced false eye-colour contradictions. Eye COLOUR is given via "eye(s)"; "gaze" carries expression. True positives ("green eyes" vs canon grey) still caught.
verified_by: scene 2 "looked into the dark basin ... his gaze caught" stopped flagging Toma.eyes; canon-break sample still flags green-vs-grey (2026-06-21).

## Continuity name-drift false positives on common capitalised words
error_signature: `name.*drift.*false|Some.*~|Could.*~|See.*~`
fix: Expanded continuity._STOP_CAPS with common sentence-initial capitalised words (Some/Could/Should/See/When/Then/Maybe/etc.). Short canonical names (Toma, Sera, Court) matched common words at edit-distance 2, spamming drift suspects every scene. Real misspellings (Marra~Mara, dist 1) still caught.
verified_by: scene 2 "Some/Could/See" drift suspects cleared; "Marra"~Mara still flagged on the sample (2026-06-21).

## Texture/density scan rates sparse-but-named prose as "rich" (can't judge real richness)
error_signature: `texture.*rich.*sparse|density.*not richness|named not rendered`
fix: A density metric CANNOT detect the "no worldbuilding / no character building" failure — a scene that name-drops systems (Weave/Rite/Class) and uses action-body words (hand/palm/wrist) scores high while a reader correctly finds it sparse. So texture.py is a COARSE white-room FLOOR only; the real richness guard is (1) bible WORLDBUILDING + required character `physicality` (design-time forcing) and (2) the cold-read IMMERSION + EMBODIMENT lens (judgment). Don't over-tune texture floors to flag good spare prose.
verified_by: sparse hero scene 2 scored RICH on every axis yet a reader flagged it; the design-forcing + embodiment-lens revision fixed it while texture stayed coarse (2026-06-22).

## Texture false-positive on short / good-spare passages
error_signature: `texture.*THIN.*good|under-embodied.*short|naming without rendering.*short`
fix: Density is noise below ~300 words. texture.scan only applies the physical-embodiment and naming-without-rendering checks when words >= 300, and naming-without-rendering needs world density >= max(floor,12). Stops false THIN verdicts on good spare literary passages (the interior profile must tolerate sparse).
verified_by: references/samples/good.md (152w, literary) passes after the gate; hero scenes still RICH (2026-06-22).

## chapters: "subplot doesn't span chapters" false-positive on tiny outlines
error_signature: `subplot.*one chapter.*false|span chapters.*2-chapter`
fix: chapters.audit only flags subplot_in_one_chapter when there are >= 3 chapters — a 2-chapter micro-outline can't have every subplot cross a couple of chapters.
verified_by: 2-chapter sample passes clean; 3-chapter hero plan still audits spanning correctly (2026-06-22).

## Plan footer leaked into the last design-gate section
error_signature: `research & failure modes.*passed.*empty|footer leaked`
fix: plan._split_sections ends the current section on a `---` horizontal rule, so trailing footer text doesn't count as the last section's content.
verified_by: empty scaffold now FAILS all required sections incl. the last; filled plan PASSES (2026-06-21).
