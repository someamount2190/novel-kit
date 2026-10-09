"""genre.py — the GENRE PRE-PROCESS. PURE PYTHON (+ live-research handoff).

THE FIRST STEP when a premise arrives, before any design (SOP-10). The model writes
genre-blind: it ignores the conventions readers came for and breaks the genre's
promise (a mystery with no fair clues, a romance with no emotional payoff, a thriller
that never tightens). This module categorises the premise's genre, then assembles
what that genre REQUIRES so the whole design honours it:

  • the READER PROMISE — the emotional payoff people read this genre FOR;
  • the CONVENTIONS / OBLIGATORY SCENES — the genre's "SOP": what it must deliver;
  • WHAT SUCCESSFUL STORIES DO — exemplar comps and the moves they share;
  • TROPES to honour + genre-specific CLICHÉS to avoid.

`classify()` is a deterministic signal classifier (premise -> ranked genres).
`load_genre()` reads the curated knowledge base in references/genres/. `brief()`
assembles a GENRE BRIEF and flags what still needs LIVE research (current comps, what
readers actually praise) — SOP-10 fills that via WebSearch and records verified
findings back into references/genres/ (anti-poison: only what a source confirmed).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# genre -> weighted signal terms found in premises (word-boundary, lowercased)
SIGNALS = {
    "mystery": ["murder", "detective", "clue", "solve", "killer", "investigat",
                "whodunit", "crime", "suspect", "alibi", "sleuth", "case", "missing",
                "disappear", "body", "uncover", "cover-up", "inquest", "hunt",
                "who opened", "who killed", "who did", "responsible", "to blame",
                "expose", "guilty", "the truth", "what really happened", "witness"],
    "thriller": ["assassin", "conspiracy", "race against time", "bomb", "terrorist",
                 "hostage", "spy", "espionage", "hunted", "on the run", "ticking clock",
                 "heist", "sabotage", "manhunt", "agent", "double-cross"],
    "romance": ["love", "fall for", "falls in love", "relationship", "wedding",
                "marriage", "lovers", "heart", "romance", "courtship", "ex-",
                "second chance", "enemies to lovers", "soulmate", "affair"],
    "fantasy": ["magic", "dragon", "kingdom", "prophecy", "wizard", "sorcer", "quest",
                "elf", "elves", "sword", "throne", "spell", "enchant", "realm",
                "chosen one", "gods", "mythical", "fae", "dark lord"],
    "science-fiction": ["spaceship", "starship", "ai", "artificial intelligence",
                        "robot", "future", "planet", "galaxy", "alien", "cyborg",
                        "dystopia", "time travel", "colony", "android", "space station",
                        "interstellar", "genetic", "simulation"],
    "horror": ["haunted", "ghost", "monster", "demon", "possess", "curse", "vampire",
               "zombie", "nightmare", "ritual", "occult", "blood", "terror",
               "supernatural", "cult", "creature", "the dark"],
    "literary-fiction": ["grief", "memory", "family", "identity", "loss", "marriage",
                         "coming of age", "generations", "belonging", "alienation",
                         "mortality", "small town", "quiet", "interior", "ordinary"],
    "historical": ["18th century", "19th century", "world war", "wwi", "wwii", "1800s",
                   "1700s", "1900s", "medieval", "victorian", "regency", "ancient",
                   "the war", "empire", "revolution", "plague"],
    "isekai": ["isekai", "transported to another world", "another world", "summoned",
               "summoned as a hero", "reincarnated", "reborn in", "demon king",
               "level up", "status screen", "skill", "stats", "guild", "adventurer",
               "portal to", "different world", "as a hero", "the hero"],
}

ALIASES = {  # accept user shorthands
    "scifi": "science-fiction", "sci-fi": "science-fiction", "sf": "science-fiction",
    "litfic": "literary-fiction", "literary": "literary-fiction",
    "romantic": "romance", "crime": "mystery", "detective": "mystery",
}

GENRE_DIR = Path(__file__).resolve().parents[2] / "references" / "genres"


def classify(premise: str) -> list:
    """Return ranked [(genre, score, [matched terms])] for a premise."""
    p = " " + premise.lower() + " "
    scored = []
    for genre, terms in SIGNALS.items():
        matched = []
        for t in terms:
            pat = re.escape(t)
            # whole-word for short alpha terms, substring for multiword/stems
            rx = rf"\b{pat}" if " " not in t and "-" not in t else pat
            if re.search(rx, p):
                matched.append(t)
        if matched:
            scored.append((genre, len(matched), matched))
    scored.sort(key=lambda x: (-x[1], x[0]))
    return scored


def normalise(name: str) -> str:
    n = name.strip().lower().replace(" ", "-")
    return ALIASES.get(n, ALIASES.get(name.strip().lower(), n))


def load_genre(slug: str) -> dict:
    """Parse references/genres/<slug>.md into a section dict (lists of bullets / text)."""
    slug = normalise(slug)
    path = GENRE_DIR / f"{slug}.md"
    if not path.is_file():
        return {}
    text = path.read_text(encoding="utf-8", errors="replace")
    out = {"slug": slug, "_path": str(path)}
    section = None
    for ln in text.splitlines():
        h = re.match(r"^##\s+(.+?)\s*$", ln)
        if h:
            section = h.group(1).strip().lower()
            out[section] = []
            continue
        if section is not None:
            bm = re.match(r"^\s*[-*]\s+(.+?)\s*$", ln)
            if bm:
                out[section].append(bm.group(1).strip())
            elif ln.strip():
                # a wrapped continuation line: join it to the last bullet if there is
                # one, else it's prose for this section (e.g. the promise paragraph)
                if out.get(section):
                    out[section][-1] += " " + ln.strip()
                else:
                    out.setdefault(section + "_text", "")
                    out[section + "_text"] += ln.strip() + " "
    return out


def brief(premise: str, force_genre: str = "") -> dict:
    ranked = classify(premise)
    if force_genre:
        primary = normalise(force_genre)
        ranked = [(primary, 99, ["(forced)"])] + [r for r in ranked if r[0] != primary]
    primary = ranked[0][0] if ranked else None
    # include a close-second genre when it's within 1 signal of the top (cross-genre)
    secondary = None
    if len(ranked) > 1 and ranked[0][1] - ranked[1][1] <= 1:
        secondary = ranked[1][0]

    kb = {g: load_genre(g) for g in filter(None, [primary, secondary])}
    missing = [g for g in filter(None, [primary, secondary]) if not kb.get(g)]
    return {"premise": premise, "ranked": ranked, "primary": primary,
            "secondary": secondary, "kb": kb, "missing_kb": missing}


def scaffold(title: str, b: dict) -> str:
    L = [f"# Genre Brief: {title}", ""]
    rk = ", ".join(f"{g} ({n})" for g, n, _ in b["ranked"][:4]) or "undetected"
    L.append(f"detected: {rk}")
    L.append(f"primary: {b['primary'] or '(set manually)'}"
             + (f"   secondary: {b['secondary']}" if b["secondary"] else ""))
    L.append("")
    for g in filter(None, [b["primary"], b["secondary"]]):
        kb = b["kb"].get(g) or {}
        L.append(f"## {g.upper()}")
        if not kb:
            L.append("  (no knowledge-base entry — RESEARCH this genre live per SOP-10,")
            L.append("   then record a references/genres/%s.md entry.)" % g)
            L.append("")
            continue
        for sec, label in [("reader promise", "READER PROMISE (what people come for)"),
                           ("conventions / obligatory scenes",
                            "CONVENTIONS / OBLIGATORY SCENES (deliver these)"),
                           ("what successful stories do",
                            "WHAT SUCCESSFUL STORIES DO"),
                           ("tropes to honour", "TROPES TO HONOUR"),
                           ("cliches to avoid", "CLICHÉS TO AVOID")]:
            items = kb.get(sec) or []
            txt = kb.get(sec + "_text", "")
            if items or txt:
                L.append(f"### {label}")
                for it in items:
                    L.append(f"- {it}")
                if txt:
                    L.append(txt.strip())
                L.append("")
    L.append("## RESEARCH LOG (live — fill via SOP-10; cite each source)")
    L.append("- current comps (titles published recently in this genre): ")
    L.append("- what readers praise (from reviews / communities): ")
    L.append("- conventions confirmed by >=2 sources: ")
    L.append("- surprises / shifts from the knowledge-base baseline: ")
    L.append("")
    L.append("> Feeds the plan: AUDIENCE & COMPS and RESEARCH & FAILURE MODES must be "
             "consistent with this brief; let it inform the STRUCTURE choice and the "
             "obligatory scenes in the SCENE LEDGER.")
    return "\n".join(L)


def format_brief(b: dict) -> str:
    L = ["GENRE PRE-PROCESS"]
    if not b["ranked"]:
        L.append("  no genre signals detected — ask the user, or set --genre. Then "
                 "research it live (SOP-10).")
        return "\n".join(L)
    L.append("  detected: " + ", ".join(f"{g} ({n} signals: {', '.join(m[:4])})"
                                         for g, n, m in b["ranked"][:4]))
    L.append(f"  primary: {b['primary']}"
             + (f"   secondary: {b['secondary']}" if b["secondary"] else ""))
    for g in filter(None, [b["primary"], b["secondary"]]):
        kb = b["kb"].get(g)
        if kb:
            promise = (kb.get("reader promise") or [kb.get("reader promise_text", "")])[0]
            L.append(f"  [{g}] KB entry found — promise: {promise[:90]}")
        else:
            L.append(f"  [{g}] NO KB entry — research live (SOP-10) and record it.")
    L.append("  → next: research the genre (SOP-10), write the brief, THEN design (SOP-06).")
    return "\n".join(L)


def _cli(argv):
    if not argv:
        print("usage: python -m novelkit.genre \"<premise>\" [--genre <name>] [--scaffold \"<title>\"]")
        return 2
    premise = argv[0]
    forced = ""
    if "--genre" in argv:
        forced = argv[argv.index("--genre") + 1]
    b = brief(premise, force_genre=forced)
    if "--scaffold" in argv:
        title = argv[argv.index("--scaffold") + 1] if argv.index("--scaffold") + 1 < len(argv) else "Untitled"
        print(scaffold(title, b))
        return 0
    print(format_brief(b))
    return 0


if __name__ == "__main__":
    sys.exit(_cli(sys.argv[1:]))
