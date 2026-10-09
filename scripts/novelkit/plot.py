"""plot.py — the PLOT field: a timeline you can AUDIT. PURE PYTHON.

The plot is the malleable spine: an ordered timeline (the SCENE LEDGER) into which
you weave SUBPLOTS — per-character development threads. Each character's ARC (from
the bible) is realised as a subplot: a sequence of belief/decision BEATS, each
tagged with the scene where it happens. Because the plot is malleable, you re-run
the AUDIT after any change to confirm every scene still does its job and every
subplot still pays off.

SUBPLOTS live in the plan under `## SUBPLOTS`:

    ## SUBPLOTS
    ### Mara: carrying the truth alone -> sharing it
    - beat: refuses Elias's help, insists on going alone @scene 2
    - beat: lies to her deputy to protect him @scene 5
    - beat: breaks, tells the deputy everything @scene 8
    - beat: testifies publicly @scene 12 (resolution)

THE AUDIT cross-references three layers:
  1. SCENE JOBS — every scene MOVES >=1 character (delegated to structure.py). A
     scene that moves nobody is purposeless: cut it or give it a job.
  2. SUBPLOT REALISATION — every beat's @scene exists, is in range, and that scene's
     `moves` actually moves this character. Beats must be in non-decreasing scene
     order (a timeline, not a jumble).
  3. ARC COMPLETION — every MAJOR character with an `arc` has a subplot with >=2
     beats and a resolution; every subplot resolves. An arc with no realised beats
     is character development that exists only in the plan, never on the page.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from . import structure as S
from . import character as C
from . import bible as B

_H3 = re.compile(r"^\s*###\s+(.+?)\s*$")
_BEAT = re.compile(r"^\s*[-*]\s*(?:beat:\s*)?(.+?)\s*$", re.IGNORECASE)
_SCENE_TAG = re.compile(r"@\s*scene\s*(\d+)|@\s*s(\d+)|@(\d+)", re.IGNORECASE)
_RESOLVE = re.compile(r"resolution|resolves?|pays? off|climax|payoff", re.IGNORECASE)


def parse_subplots(plan_text: str) -> list:
    m = re.search(r"^##\s+subplots?.*$", plan_text, re.IGNORECASE | re.MULTILINE)
    if not m:
        return []
    body = plan_text[m.end():]
    nxt = re.search(r"^##\s+\S", body, re.MULTILINE)
    if nxt:
        body = body[:nxt.start()]

    threads = []
    cur = None
    for ln in body.splitlines():
        h = _H3.match(ln)
        if h:
            title = h.group(1).strip()
            owner = title.split(":", 1)[0].strip() if ":" in title else title
            cur = {"title": title, "owner": owner, "beats": []}
            threads.append(cur)
            continue
        if cur is not None and ln.strip().startswith(("-", "*")):
            bm = _BEAT.match(ln)
            if not bm:
                continue
            txt = bm.group(1).strip()
            sc = _SCENE_TAG.search(txt)
            scene = next((int(g) for g in (sc.groups() if sc else []) if g), None)
            threads_beat = {"text": txt, "scene": scene,
                            "resolution": bool(_RESOLVE.search(txt))}
            cur["beats"].append(threads_beat)
    return threads


def audit(plan_text: str, bib: B.Bible) -> dict:
    rows = S.parse_ledger(plan_text)
    known = [n for c in bib.characters.values() for n in c.all_names]
    struct = S.check(rows, known_names=known) if rows else None
    subplots = parse_subplots(plan_text)
    n_scenes = len(rows)

    issues = {"purposeless_scenes": [], "subplot_realisation": [], "arc_completion": [],
              "ordering": [], "orphan_arc": []}

    # 1. SCENE JOBS — scenes that move nobody (from structure's moved map)
    if struct:
        for sc_i, whos in struct.get("moved", {}).items():
            if not whos:
                title = rows[sc_i - 1].get("scene", "")
                issues["purposeless_scenes"].append({"scene": sc_i, "title": title})

    # map: scene -> set of characters it moves (by canonical bible name)
    def canon(name):
        c = bib.character_by_any_name(name) if name else None
        return c.name if c else (name or "")

    moved_by_scene = {i: {canon(w) for w in whos}
                      for i, whos in (struct.get("moved", {}) if struct else {}).items()}

    # 2. SUBPLOT REALISATION
    for t in subplots:
        owner_c = bib.character_by_any_name(t["owner"])
        owner = owner_c.name if owner_c else t["owner"]
        last_scene = 0
        realised = 0
        for b in t["beats"]:
            if b["scene"] is None:
                issues["subplot_realisation"].append(
                    {"subplot": t["title"], "beat": b["text"][:70],
                     "problem": "no @scene tag — beat isn't placed on the timeline"})
                continue
            if not (1 <= b["scene"] <= n_scenes):
                issues["subplot_realisation"].append(
                    {"subplot": t["title"], "beat": b["text"][:70],
                     "problem": f"@scene {b['scene']} out of range (1..{n_scenes})"})
                continue
            realised += 1
            if b["scene"] < last_scene:
                issues["ordering"].append(
                    {"subplot": t["title"], "beat": b["text"][:70],
                     "problem": f"@scene {b['scene']} precedes earlier beat @scene {last_scene}"})
            last_scene = max(last_scene, b["scene"])
            moved = moved_by_scene.get(b["scene"], set())
            if owner and moved and not any(owner.lower() == m.lower() for m in moved):
                issues["subplot_realisation"].append(
                    {"subplot": t["title"], "beat": b["text"][:70],
                     "problem": f"@scene {b['scene']} moves {sorted(moved)}, not {owner} — "
                                f"the beat isn't dramatised in its scene"})
        t["_realised"] = realised

    # 3. ARC COMPLETION
    sub_by_owner = {}
    for t in subplots:
        oc = bib.character_by_any_name(t["owner"])
        sub_by_owner.setdefault((oc.name if oc else t["owner"]).lower(), []).append(t)

    for c in bib.characters.values():
        if not C.is_major(c):
            continue
        arc = (c.attrs.get("arc") or "").strip()
        if not arc:
            continue  # baseline_gate handles a missing arc; here we audit realisation
        threads = sub_by_owner.get(c.name.lower(), [])
        if not threads:
            issues["orphan_arc"].append(
                {"character": c.name, "arc": arc[:80],
                 "problem": "arc declared but NO subplot realises it on the timeline"})
            continue
        beats = [b for t in threads for b in t["beats"]]
        realised = [b for b in beats if b["scene"] and 1 <= b["scene"] <= n_scenes]
        if len(realised) < 2:
            issues["arc_completion"].append(
                {"character": c.name,
                 "problem": f"only {len(realised)} realised beat(s) — an arc needs "
                            f"at least a turn and a resolution (>=2)"})
        if not any(b["resolution"] for b in beats):
            issues["arc_completion"].append(
                {"character": c.name,
                 "problem": "no beat marked as the resolution — where does this arc land?"})

    total = sum(len(v) for v in issues.values())
    return {"scenes": n_scenes, "subplots": len(subplots), "issues": issues,
            "struct": struct, "total": total, "passed": total == 0}


def format_report(rep: dict) -> str:
    iss = rep["issues"]
    L = [f"PLOT AUDIT — {rep['scenes']} scene(s), {rep['subplots']} subplot(s)"]
    if rep["passed"]:
        L.append("  ✓ every scene moves a character; every subplot beat is placed and "
                 "dramatised; every arc has >=2 beats and a resolution")
        return "\n".join(L)
    labels = {
        "purposeless_scenes": "PURPOSELESS SCENES (move no character — cut or give a job)",
        "subplot_realisation": "SUBPLOT NOT DRAMATISED",
        "ordering": "TIMELINE ORDER",
        "arc_completion": "ARC INCOMPLETE",
        "orphan_arc": "ARC NEVER REALISED",
    }
    for key, label in labels.items():
        items = iss.get(key) or []
        if not items:
            continue
        L.append(f"  {label}:")
        for it in items:
            if "scene" in it and "problem" not in it:
                L.append(f"    ✗ scene {it['scene']} — {it.get('title','')}")
            elif "character" in it:
                L.append(f"    ✗ {it['character']}: {it['problem']}")
            else:
                tag = it.get("subplot", "")
                L.append(f"    ✗ [{tag}] {it['problem']}")
                if it.get("beat"):
                    L.append(f"         beat: {it['beat']}")
    return "\n".join(L)


def _cli(argv):
    if len(argv) < 2:
        print("usage: python -m novelkit.plot <plan.md> <bible.md> [--json]")
        return 2
    plan_text = Path(argv[0]).read_text(encoding="utf-8", errors="replace")
    bib = B.load(argv[1])
    rep = audit(plan_text, bib)
    if "--json" in argv:
        import json
        rep.pop("struct", None)
        print(json.dumps(rep, ensure_ascii=False, indent=2))
    else:
        print(format_report(rep))
    return 0 if rep["passed"] else 1


if __name__ == "__main__":
    sys.exit(_cli(sys.argv[1:]))
