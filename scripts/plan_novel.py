#!/usr/bin/env python
"""plan_novel.py — start a novel build. Scaffolds the BUILD PLAN + STORY BIBLE for
a premise, into _work/, and prints the next steps. Mirrors blender-kit/plan_build.py.

    python plan_novel.py "A river warden hunts the flood that took her sister"
    python plan_novel.py "<premise>" --title "The River Warden" --protagonist "Mara Vance"

Then fill both files and run the design gate:
    python -m novelkit.plan _work/<slug>_plan.md      # must PASS before any prose
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from novelkit import plan, bible, genre  # noqa: E402


def slugify(s: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return "-".join(s.split("-")[:6]) or "untitled"


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    premise = argv[0]
    title = _opt(argv, "--title") or premise[:40]
    protagonist = _opt(argv, "--protagonist") or "Protagonist"
    slug = slugify(_opt(argv, "--slug") or title)

    work = Path(__file__).resolve().parents[1] / "_work"
    work.mkdir(exist_ok=True)
    plan_path = work / f"{slug}_plan.md"
    bible_path = work / f"{slug}_bible.md"
    genre_path = work / f"{slug}_genre.md"

    if plan_path.exists() and "--force" not in argv:
        print(f"refusing to overwrite {plan_path} (use --force)")
        return 1

    # GENRE PRE-PROCESS (SOP-10) runs first: classify the premise + seed the brief.
    forced = _opt(argv, "--genre") or ""
    gb = genre.brief(premise, force_genre=forced)
    genre_path.write_text(genre.scaffold(title, gb), encoding="utf-8")
    plan_path.write_text(plan.scaffold(premise), encoding="utf-8")
    bible_path.write_text(bible.scaffold(title, protagonist), encoding="utf-8")

    print(genre.format_brief(gb))
    print()
    print(f"scaffolded:\n  genre: {genre_path}\n  plan : {plan_path}\n  bible: {bible_path}\n")
    miss = ", ".join(gb["missing_kb"])
    print("NEXT (SOP-10 genre pre-process → SOP-06 design-first → SOP-00 new-novel):")
    print(f"  1. RESEARCH the genre (SOP-10): fill the RESEARCH LOG in {genre_path.name}")
    print("     with current comps + what readers praise; verify conventions vs >=2 sources."
          + (f"  ({miss}: NO knowledge-base entry — research from scratch + record it.)" if miss else ""))
    print("  2. Fill the bible (CHARACTER field): traits, backstory, voice, want/need, arc.")
    print("  3. Fill the plan (SCENE+PLOT): ledger w/ `moves` + tension, SUBPLOTS, etc.,")
    print("     honouring the genre's obligatory scenes + avoiding its clichés.")
    print("  4. Gate ALL fields:")
    print(f"       python -m novelkit.plan {plan_path.name}")
    print(f"       python -m novelkit.character {bible_path.name}")
    print(f"       python -m novelkit.structure {plan_path.name} {bible_path.name}")
    print(f"       python -m novelkit.plot {plan_path.name} {bible_path.name}")
    print("     (all must PASS — no prose until then.)")
    print("  5. Draft a scene, then INSPECT + COLD READ + FIDELITY:")
    print(f"       python -m novelkit.report <scene.md> {bible_path.name} {plan_path.name}")
    return 0


def _opt(argv, flag):
    if flag in argv:
        i = argv.index(flag)
        if i + 1 < len(argv):
            return argv[i + 1]
    return None


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
