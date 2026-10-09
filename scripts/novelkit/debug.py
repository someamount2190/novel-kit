"""debug.py — classify a failing run against LEARNINGS.md. PURE PYTHON.

Same role as blender-kit/godot-kit debug: when a novelkit script errors, match the
traceback's signature against recorded fixes in ../LEARNINGS.md before flailing.
Bounded retries with the mapped fix, then a minimal repro + STOP. Record a NEW fix
only after a clean run verifies it (anti-poison rule).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

LEARNINGS = Path(__file__).resolve().parents[2] / "LEARNINGS.md"

# baseline signatures even before LEARNINGS is populated
BASELINE = [
    (r"UnicodeEncodeError.*charmap",
     "Windows cp1252 console can't print report glyphs. novelkit.__init__ already "
     "reconfigures stdout to UTF-8 — run via `python -m novelkit.<mod>`, not by "
     "importing a module file directly without the package init."),
    (r"no SCENE LEDGER table found",
     "structure.py needs a markdown pipe table under '## SCENE LEDGER' with a header "
     "row. Scaffold one with `python -m novelkit.plan --scaffold`."),
    (r"FileNotFoundError|No such file",
     "Path wrong. Run module commands from the skill's scripts/ dir; manuscript/bible "
     "paths are relative to your CWD, not to scripts/."),
    (r"design_gate.*FAIL|RESULT: FAIL",
     "The plan still has unfilled gates. preflight/SOP-06 forbid prose until "
     "plan.design_gate() passes — fill the flagged sections with substance."),
    (r"ModuleNotFoundError: No module named 'novelkit'",
     "Run from scripts/ so the package resolves: cd scripts && python -m novelkit.<mod>."),
]


def _load_learnings():
    if not LEARNINGS.is_file():
        return []
    text = LEARNINGS.read_text(encoding="utf-8", errors="replace")
    entries = []
    for block in re.split(r"^##\s+", text, flags=re.MULTILINE)[1:]:
        sig = re.search(r"error_signature:\s*`?(.+?)`?\s*$", block, re.MULTILINE)
        fix = re.search(r"fix:\s*(.+)", block, re.MULTILINE)
        if sig:
            entries.append((sig.group(1).strip(),
                            (fix.group(1).strip() if fix else block.strip()[:300])))
    return entries


def classify(error_text: str) -> dict:
    matches = []
    for sig, fix in _load_learnings():
        try:
            if re.search(sig, error_text, re.IGNORECASE):
                matches.append({"source": "LEARNINGS.md", "signature": sig, "fix": fix})
        except re.error:
            if sig.lower() in error_text.lower():
                matches.append({"source": "LEARNINGS.md", "signature": sig, "fix": fix})
    for sig, fix in BASELINE:
        if re.search(sig, error_text, re.IGNORECASE):
            matches.append({"source": "baseline", "signature": sig, "fix": fix})
    return {"matched": bool(matches), "matches": matches}


def report(error_text: str) -> str:
    rep = classify(error_text)
    if not rep["matched"]:
        return ("debug: no known signature matched. Read references/bpy_gotchas-style "
                "notes? (none yet). Make a MINIMAL repro, fix, then record in "
                "LEARNINGS.md (only after a clean run verifies the fix).")
    L = ["debug: matched known issue(s):"]
    for m in rep["matches"]:
        L.append(f"  [{m['source']}] /{m['signature']}/")
        L.append(f"      → {m['fix']}")
    return "\n".join(L)


def _cli(argv):
    if argv and argv[0] not in ("-", "--stdin"):
        err = Path(argv[0]).read_text(encoding="utf-8", errors="replace") \
            if Path(argv[0]).is_file() else " ".join(argv)
    else:
        err = sys.stdin.read()
    print(report(err))
    return 0


if __name__ == "__main__":
    sys.exit(_cli(sys.argv[1:]))
