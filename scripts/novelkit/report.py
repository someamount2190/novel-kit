"""report.py — one INSPECT verdict for a scene/manuscript. PURE PYTHON.

Runs the deterministic checks together so the loop has a single gate to read:
    prose_scan  (smell)  +  continuity vs bible (canon)  +  structure (arc).
The cold read (SOP-07) is NOT deterministic and is reported separately by Claude;
this aggregates only what code can decide. A clean report here still REQUIRES a
cold read before you call a scene done — passing the scanners is necessary, not
sufficient.
"""
from __future__ import annotations

import sys
from pathlib import Path

from . import (prose_scan, continuity, structure, bible, manuscript, character, plot,
               texture, voice, flags as flags_mod, chapters as chapters_mod)


def inspect(ms_path: str, bible_path: str = "", plan_path: str = "", genre: str = "") -> dict:
    text = Path(ms_path).read_text(encoding="utf-8", errors="replace")
    out = {"manuscript": ms_path}
    bib = None
    known = None

    ps = prose_scan.scan(text)
    out["prose"] = {"passed": ps["passed"], "hard": ps["hard_flags"],
                    "review": ps["review_flags"]}

    # TEXTURE — the richness floor (counterweight to prose_scan). Genre sets the profile.
    profile = texture.profile_for_genre(genre) if genre else "general"
    tx = texture.scan(text, profile)
    out["texture"] = {"passed": tx["passed"], "verdict": tx["verdict"],
                      "report": texture.format_report(tx)}

    if bible_path and Path(bible_path).is_file():
        bib = bible.load(bible_path)
        known = [n for c in bib.characters.values() for n in c.all_names]
        cont = continuity.check(text, bib)
        out["continuity"] = {"passed": cont["passed"], "total": cont["total"],
                             "report": continuity.format_report(cont)}
        # project-level CHARACTER field: are all major characters baseline-complete?
        cg = character.baseline_gate(bib)
        out["character"] = {"passed": cg["passed"], "rep": cg}
        # VOICE DISTINCTIVENESS — declared voices must be specific + mutually distinct
        # (deterministic, design-level → counts toward pass/fail).
        vg = voice.distinctiveness_gate(bib)
        out["voice_distinct"] = {"passed": vg["passed"], "report": voice.format_gate(vg)}
        # scene-level voiceprints — heuristic attribution, REVIEW only (does NOT fail).
        vp = voice.voiceprints(text, bib)
        out["voiceprints"] = {"report": voice.format_prints(vp),
                              "collisions": len(vp["collisions"])}
    if plan_path and Path(plan_path).is_file():
        ptext = Path(plan_path).read_text(encoding="utf-8", errors="replace")
        rows = structure.parse_ledger(ptext)
        if rows:
            st = structure.check(rows, known_names=known)
            out["structure"] = {"passed": st["passed"],
                                "report": structure.format_report(st)}
        # project-level PLOT field: timeline + subplot audit (needs both plan + bible)
        if bib is not None:
            pa = plot.audit(ptext, bib)
            out["plot"] = {"passed": pa["passed"], "report": plot.format_report(pa)}
            fa = flags_mod.audit(ptext, bib)
            out["flags"] = {"passed": fa["passed"], "report": flags_mod.format_report(fa)}
            ca = chapters_mod.audit(ptext, bib)
            out["chapters"] = {"passed": ca["passed"], "report": chapters_mod.format_report(ca)}

    out["passed"] = all(sec.get("passed", True) for sec in
                        [out.get("prose", {}), out.get("continuity", {}),
                         out.get("structure", {}), out.get("character", {}),
                         out.get("plot", {}), out.get("texture", {}),
                         out.get("voice_distinct", {}),
                         out.get("flags", {}), out.get("chapters", {})])
    out["_ps"] = ps
    return out


def format_report(rep: dict) -> str:
    L = [f"╞═ INSPECT: {rep['manuscript']} ═╡"]
    L.append(prose_scan.format_report(rep["_ps"]))
    if "texture" in rep:
        L.append("")
        L.append(rep["texture"]["report"])
    if "continuity" in rep:
        L.append("")
        L.append(rep["continuity"]["report"])
    if "character" in rep:
        L.append("")
        cg = rep["character"]["rep"]
        bad = [c for c in cg["characters"] if c["major"] and not c["passed"]]
        if cg["passed"]:
            L.append("CHARACTER BASELINE — ✓ all major characters complete")
        else:
            L.append("CHARACTER BASELINE — ✗")
            for c in bad:
                L.append(f"    ✗ {c['name']} missing {', '.join(c['missing'])}")
    if "voice_distinct" in rep:
        L.append("")
        L.append(rep["voice_distinct"]["report"])
    if "voiceprints" in rep:
        L.append("")
        L.append(rep["voiceprints"]["report"])
    if "structure" in rep:
        L.append("")
        L.append(rep["structure"]["report"])
    if "plot" in rep:
        L.append("")
        L.append(rep["plot"]["report"])
    if "chapters" in rep:
        L.append("")
        L.append(rep["chapters"]["report"])
    if "flags" in rep:
        L.append("")
        L.append(rep["flags"]["report"])
    L.append("")
    L.append("─" * 40)
    L.append("DETERMINISTIC GATE: " + ("PASS" if rep["passed"] else "FAIL"))
    L.append("  (necessary, not sufficient — now do the COLD READ, SOP-07.)")
    return "\n".join(L)


def _cli(argv):
    if not argv:
        print("usage: python -m novelkit.report <manuscript> [bible.md] [plan.md] [--genre <name>]")
        return 2
    genre = ""
    if "--genre" in argv:
        genre = argv[argv.index("--genre") + 1]
        argv = [a for i, a in enumerate(argv)
                if a != "--genre" and (i == 0 or argv[i - 1] != "--genre")]
    bib = next((a for a in argv[1:] if "bible" in a.lower()), "")
    plan = next((a for a in argv[1:] if "plan" in a.lower()), "")
    rest = [a for a in argv[1:] if a not in (bib, plan)]
    if not bib and rest:
        bib = rest.pop(0)
    if not plan and rest:
        plan = rest.pop(0)
    rep = inspect(argv[0], bib, plan, genre=genre)
    print(format_report(rep))
    return 0 if rep["passed"] else 1


if __name__ == "__main__":
    sys.exit(_cli(sys.argv[1:]))
