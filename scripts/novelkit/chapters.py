"""chapters.py — the CHAPTER layer. PURE PYTHON.

Plot is planned before anything; chapters are planned beforehand too. A novel is
organised in CHAPTERS that are LONG (several scenes each), and SUBPLOTS span a couple
of chapters rather than resolving inside one scene. This module audits that layer,
sitting between structure.py (scenes) and plot.py (subplots).

Declared in the plan under `## CHAPTERS` (a pipe table), and each SCENE LEDGER row
carries a `ch` column tying the scene to its chapter:

    ## CHAPTERS
    | ch | title          | purpose                         | subplots advanced | scenes | ~words |
    |----|----------------|---------------------------------|-------------------|--------|--------|
    | 1  | Summoned & Spent | Toma arrives, appraised blank, cast out | Toma; Aldric | 1-3 | 6000 |
    | 2  | The Lower City | Toma hits bottom; Sera takes him in     | Toma; Sera   | 4-5 | 5500 |

AUDIT:
  • every scene's `ch` is a declared chapter; chapters cover all scenes contiguously;
  • chapters are LONG — a one-scene chapter is flagged (novels run multi-scene);
  • every chapter ADVANCES something — a subplot beat or plot turn lands in it;
  • SUBPLOTS SPAN chapters — a subplot whose beats sit in a single chapter is flagged
    (the user's point: arcs should thread across a couple of chapters);
  • word targets that are tiny get a "novels have long chapters" advisory.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from . import structure as S
from . import plot as P
from . import bible as B

MIN_SCENES_PER_CHAPTER = 2          # a "long" chapter is multi-scene
SHORT_WORDS = 2500                   # advisory floor; novel chapters typically run longer


def _parse_chapter_table(plan_text: str) -> list:
    m = re.search(r"^##\s+chapters?.*$", plan_text, re.IGNORECASE | re.MULTILINE)
    body = plan_text[m.end():] if m else ""
    if m:
        nxt = re.search(r"^##\s+\S", body, re.MULTILINE)
        if nxt:
            body = body[:nxt.start()]
    rows, headers = [], None
    for ln in body.splitlines():
        if not ln.strip().startswith("|"):
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if all(re.match(r"^:?-{2,}:?$", c) for c in cells if c):
            continue
        if headers is None:
            headers = [c.lower() for c in cells]
            continue
        row = {headers[i]: c for i, c in enumerate(cells) if i < len(headers)}
        if any(row.values()):
            rows.append(row)
    return rows


def _chap_of_scene(ledger_rows: list) -> dict:
    """scene index (1-based) -> chapter number (int) from the ledger `ch` column."""
    out = {}
    for i, r in enumerate(ledger_rows, 1):
        raw = (r.get("chapter") or "").strip()
        mm = re.search(r"\d+", raw)
        out[i] = int(mm.group(0)) if mm else None
    return out


def audit(plan_text: str, bib: B.Bible = None) -> dict:
    ledger = S.parse_ledger(plan_text)
    chap_table = _parse_chapter_table(plan_text)
    scene_chap = _chap_of_scene(ledger)
    subplots = P.parse_subplots(plan_text)

    declared = {}
    for r in chap_table:
        mm = re.search(r"\d+", r.get("ch", "") or r.get("chapter", "") or "")
        if mm:
            declared[int(mm.group(0))] = r

    issues = {"scene_unassigned": [], "undeclared_chapter": [], "short_chapter": [],
              "no_advance": [], "subplot_in_one_chapter": [], "no_chapter_plan": [],
              "no_direction": []}
    advisories = []

    if not chap_table:
        issues["no_chapter_plan"].append({"problem": "no ## CHAPTERS table — plan the "
                                          "chapters beforehand (plot-first)"})

    # per-scene tension (for each chapter's internal trajectory)
    scene_tension = {}
    for i, r in enumerate(ledger, 1):
        tm = re.search(r"-?\d+(?:\.\d+)?", r.get("tension", "") or "")
        scene_tension[i] = float(tm.group(0)) if tm else None

    # scenes -> chapters (scenes live INSIDE chapters; the chapter is the container)
    scenes_in_chapter = {}
    for sc, ch in scene_chap.items():
        if ch is None:
            issues["scene_unassigned"].append({"scene": sc})
            continue
        scenes_in_chapter.setdefault(ch, []).append(sc)
        if declared and ch not in declared:
            issues["undeclared_chapter"].append({"scene": sc, "chapter": ch})

    chapter_arc = {}   # ch -> [tensions] for the report
    for ch, scs in sorted(scenes_in_chapter.items()):
        if len(scs) < MIN_SCENES_PER_CHAPTER:
            issues["short_chapter"].append({"chapter": ch, "scenes": scs,
                                            "problem": f"only {len(scs)} scene(s) — novels "
                                            f"run multi-scene chapters; merge or develop"})
        row = declared.get(ch, {})
        # DIRECTION — a chapter must have a planned arc, not just a label: where it
        # opens, its turn, where it lands, and the hook out. Header may carry a
        # parenthetical hint ("direction (opens → …)"), so match by CONTAINS.
        direction = ""
        for hk, val in row.items():
            if any(key in hk for key in ("direction", "arc", "trajectory", "where it goes")) \
                    and (val or "").strip():
                direction = val.strip()
                break
        if declared and not direction:
            issues["no_direction"].append(
                {"chapter": ch, "problem": "no planned DIRECTION — give the chapter an "
                 "arc: opens X → turns on Y → lands Z, with a hook into the next"})
        # internal tension trajectory (does the chapter BUILD, or plateau / trail off?)
        tens = [scene_tension[s] for s in scs if scene_tension.get(s) is not None]
        chapter_arc[ch] = tens
        if len(tens) >= 2 and len(set(tens)) == 1:
            advisories.append(f"ch {ch}: tension flat ({'/'.join(str(int(t)) for t in tens)})"
                              f" — does the chapter BUILD? direction needs movement, not a plateau")
        elif len(tens) >= 2 and tens[-1] == min(tens) and tens[-1] < tens[0]:
            advisories.append(f"ch {ch}: ends on its lowest beat — chapters usually land "
                              f"on a turn/hook, not trail off")
        words = None
        wmm = re.search(r"\d[\d,]{2,}", row.get("~words", "") or row.get("words", "") or "")
        if wmm:
            words = int(wmm.group(0).replace(",", ""))
        if words is not None and words < SHORT_WORDS:
            advisories.append(f"ch {ch}: ~{words}w target is short — novel chapters "
                              f"usually run longer (subplots span them).")

    # which chapters each subplot touches (beats -> scene -> chapter)
    subplot_chapters = {}
    for t in subplots:
        chs = set()
        for b in t["beats"]:
            if b["scene"] and b["scene"] in scene_chap and scene_chap[b["scene"]]:
                chs.add(scene_chap[b["scene"]])
        subplot_chapters[t["title"]] = chs
        # only meaningful once the book has enough chapters to span; a 2-chapter
        # micro-outline can't have every subplot cross "a couple of chapters".
        n_chapters = len(declared) or len(scenes_in_chapter)
        if len(chs) == 1 and n_chapters >= 3:
            issues["subplot_in_one_chapter"].append(
                {"subplot": t["title"], "chapter": next(iter(chs)),
                 "problem": "all beats in one chapter — a subplot should SPAN a couple "
                            "of chapters, not resolve inside one"})

    # every chapter advances >=1 subplot
    chapters_touched_by_subplots = {c for chs in subplot_chapters.values() for c in chs}
    for ch in sorted(scenes_in_chapter):
        if ch not in chapters_touched_by_subplots:
            issues["no_advance"].append(
                {"chapter": ch, "problem": "no subplot beat lands here — what does this "
                 "chapter advance? (every chapter should move an arc or the plot)"})

    total = sum(len(v) for v in issues.values())
    hard = (len(issues["scene_unassigned"]) + len(issues["undeclared_chapter"])
            + len(issues["no_chapter_plan"]) + len(issues["no_direction"]))
    return {"chapters": len(declared) or len(scenes_in_chapter),
            "scenes_in_chapter": scenes_in_chapter, "subplot_chapters": subplot_chapters,
            "chapter_arc": chapter_arc, "issues": issues, "advisories": advisories,
            "total": total, "passed": hard == 0}


def format_report(rep: dict) -> str:
    L = [f"CHAPTERS — {rep['chapters']} chapter(s)"]
    arc = rep.get("chapter_arc", {})
    for c, s in sorted(rep["scenes_in_chapter"].items()):
        tens = arc.get(c) or []
        trail = ("  tension " + "→".join(str(int(t)) for t in tens)) if tens else ""
        L.append(f"  ch{c}: scenes [{','.join(map(str, s))}]{trail}")
    iss = rep["issues"]
    clean = rep["total"] == 0
    if clean:
        L.append("  ✓ scenes mapped to long chapters; every chapter advances a subplot; "
                 "subplots span chapters")
    labels = {
        "no_chapter_plan": "NO CHAPTER PLAN",
        "no_direction": "CHAPTER HAS NO PLANNED DIRECTION",
        "scene_unassigned": "SCENE NOT IN A CHAPTER (add a `ch` column value)",
        "undeclared_chapter": "SCENE IN AN UNDECLARED CHAPTER",
        "short_chapter": "CHAPTER TOO SHORT",
        "no_advance": "CHAPTER ADVANCES NOTHING",
        "subplot_in_one_chapter": "SUBPLOT DOESN'T SPAN CHAPTERS",
    }
    for key, label in labels.items():
        for it in iss.get(key, []):
            detail = it.get("problem", "")
            who = (f"ch {it['chapter']}" if "chapter" in it and "scene" not in it
                   else f"scene {it.get('scene','')}" if "scene" in it
                   else it.get("subplot", ""))
            L.append(f"  ✗ [{label}] {who}: {detail}")
    for a in rep["advisories"]:
        L.append(f"  ⚠ {a}")
    return "\n".join(L)


def _cli(argv):
    if not argv:
        print("usage: python -m novelkit.chapters <plan.md> [bible.md] [--json]")
        return 2
    plan_text = Path(argv[0]).read_text(encoding="utf-8", errors="replace")
    bib = B.load(argv[1]) if len(argv) > 1 and not argv[1].startswith("--") \
        and Path(argv[1]).is_file() else None
    rep = audit(plan_text, bib)
    if "--json" in argv:
        import json
        rep.pop("subplot_chapters", None)
        print(json.dumps(rep, ensure_ascii=False, indent=2))
    else:
        print(format_report(rep))
    return 0 if rep["passed"] else 1


if __name__ == "__main__":
    sys.exit(_cli(sys.argv[1:]))
