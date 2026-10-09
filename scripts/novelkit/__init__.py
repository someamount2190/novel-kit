"""novelkit — deterministic harness for novel writing/editing.

PURE PYTHON, stdlib only (runs on 3.10 and 3.14). No third-party deps.

Modules:
  manuscript  parse prose into chapters/scenes + word/sentence stats
  prose_scan  deterministic prose-smell scanner (filter words, cliches, adverbs,
              said-bookisms, intensifiers, repetition, sentence-rhythm, passive)
  bible       story-bible canon model (characters / world facts / timeline / ledger)
  continuity  validate prose against the bible canon -> contradiction & drift flags
  structure   scene ledger (goal/conflict/turn) + beat coverage + tension curve
  plan        scaffold the BUILD PLAN + design_gate()
  critique    prep a BLIND cold-read payload + aggregate adversarial verdicts
  report      aggregate inspect results into one verdict
  debug       error classifier consulting LEARNINGS.md

Run a module as:  python -m novelkit.<mod> <args>
(from the scripts/ directory, so the package import resolves)
"""

import sys as _sys

# Windows consoles default to cp1252 and choke on the report glyphs (⚠ … • ✓ ✗).
# Reconfigure stdio to UTF-8 once, here, so every `python -m novelkit.*` is safe.
for _stream in (_sys.stdout, _sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except Exception:
        pass

__all__ = [
    "manuscript",
    "prose_scan",
    "bible",
    "continuity",
    "structure",
    "plan",
    "critique",
    "report",
    "debug",
]
