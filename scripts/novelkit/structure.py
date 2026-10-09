"""structure.py — scene-ledger completeness + tension-curve diagnostics. PURE PYTHON.

Fights the model's structural failures: episodic scenes that don't build, a
sagging middle, no escalation into the climax, scenes with no goal/conflict/turn
(things merely happen). It reads the SCENE LEDGER from the plan — a markdown pipe
table — and checks craft invariants that hold regardless of genre:

  • every scene declares a GOAL, a CONFLICT, and a TURN/OUTCOME (a scene that
    changes nothing is a candidate for cutting);
  • the value/tension of consecutive scenes CHANGES (a flat run = sag);
  • tension trends UP across acts and the CLIMAX is at/near the global max;
  • POV is declared (head-hopping guard);
  • scene outcomes alternate (relentless wins or relentless losses both flatten).

Expected ledger (header names matched loosely, order-free):

    ## SCENE LEDGER
    | # | scene        | pov  | goal            | conflict        | turn          | tension |
    |---|--------------|------|-----------------|-----------------|---------------|---------|
    | 1 | The flood    | Mara | reach the bridge| current too fast| fails, swept  | 4       |
    | 2 | ...          | ...  | ...             | ...             | ...           | 6       |

`tension` is 1-10 (the planner's felt intensity). `turn` may encode valence with a
leading +/- or the words win/loss/up/down for the win-loss alternation check.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

_REQUIRED = ["goal", "conflict", "turn", "moves"]
_ALIASES = {
    "turn": ["turn", "outcome", "turn/outcome", "disaster", "result", "change"],
    "goal": ["goal", "objective", "want", "scene goal"],
    "conflict": ["conflict", "obstacle", "opposition"],
    "moves": ["moves", "move", "moves who", "character move", "delta", "effect"],
    "tension": ["tension", "intensity", "stakes", "value"],
    "pov": ["pov", "viewpoint", "narrator"],
    "scene": ["scene", "title", "summary", "what happens"],
    "chapter": ["ch", "chapter", "chap", "ch#"],
    "num": ["#", "no", "num", "n"],
}


def _canon_header(h: str):
    h = h.strip().lower()
    for canon, al in _ALIASES.items():
        if h in al:
            return canon
    return h


def parse_ledger(text: str) -> list:
    """Extract the SCENE LEDGER pipe table -> list of dict rows."""
    # isolate the section after a '## ... LEDGER' heading (else scan whole doc)
    m = re.search(r"^##\s+.*ledger.*$", text, re.IGNORECASE | re.MULTILINE)
    body = text[m.end():] if m else text
    # stop at next H2
    nxt = re.search(r"^##\s+\S", body, re.MULTILINE)
    if nxt:
        body = body[:nxt.start()]

    rows = []
    headers = None
    for ln in body.splitlines():
        if not ln.strip().startswith("|"):
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if re.match(r"^[\s:|-]+$", ln.strip().replace("|", "")):  # separator row
            continue
        if all(re.match(r"^:?-{2,}:?$", c) for c in cells if c):  # --- separator
            continue
        if headers is None:
            headers = [_canon_header(c) for c in cells]
            continue
        row = {}
        for i, c in enumerate(cells):
            if i < len(headers):
                row[headers[i]] = c
        if any(v for v in row.values()):
            rows.append(row)
    return rows


def _tension(row) -> float:
    raw = row.get("tension", "")
    m = re.search(r"-?\d+(?:\.\d+)?", raw or "")
    return float(m.group(0)) if m else None


def _valence(row) -> int:
    t = (row.get("turn") or "").lower()
    if t.startswith("+") or "win" in t or "success" in t or " up" in t:
        return +1
    if t.startswith("-") or "loss" in t or "fail" in t or "down" in t or "disaster" in t:
        return -1
    return 0


_BELIEF = re.compile(r"->|→|belief|realiz|decid|learns?|discovers?|believ|"
                     r"changes? (?:her|his|their) mind|accepts?|admits?", re.IGNORECASE)
_ACTION = re.compile(r"resolv|act|does|kills?|escapes?|wins?|loses?|takes?|"
                     r"commits?|chooses?|refus|confront|leaves?|saves?", re.IGNORECASE)


def _one_move(part: str, known_names):
    """Parse a single 'Name: <change>' move -> (who, kind, valid)."""
    part = part.strip()
    if not part:
        return None
    head = part.split(":", 1)[0].strip() if ":" in part else ""
    who = ""
    if head and (not known_names or any(head.lower() == k.lower()
                                        or head.lower() in k.lower() for k in known_names)):
        who = head
    elif known_names:
        pl = part.lower()
        for k in known_names:
            if re.search(rf"\b{re.escape(k.lower())}\b", pl):
                who = k
                break
    if not who:
        who = head
    kind = ("belief" if _BELIEF.search(part) else
            "action" if _ACTION.search(part) else "unclear")
    valid = bool(who) and (not known_names or any(
        who.lower() == k.lower() or who.lower() in k.lower() or k.lower() in who.lower()
        for k in known_names))
    return {"who": who, "kind": kind, "valid": valid}


def _parse_moves(moves: str, known_names) -> list:
    """A scene may move several characters; split on ';' (and ' and ' / newline)."""
    if not moves:
        return []
    parts = re.split(r";|\n|\s+and\s+(?=[A-Z])", moves)
    return [m for m in (_one_move(p, known_names) for p in parts) if m]


def _moved_characters(moves: str, known_names) -> list:
    return [m["who"] for m in _parse_moves(moves, known_names) if m["who"]]


def check(rows: list, known_names=None) -> dict:
    issues = {"incomplete": [], "flat_run": [], "escalation": [], "climax": [],
              "pov": [], "valence": [], "moves": []}
    n = len(rows)

    for i, r in enumerate(rows, 1):
        missing = [f for f in _REQUIRED if not (r.get(f) or "").strip()
                   or (r.get(f) or "").strip() in ("-", "—", "tbd", "TBD")]
        if missing:
            issues["incomplete"].append({"scene": i, "missing": missing,
                                         "title": r.get("scene", "")})
        if not (r.get("pov") or "").strip():
            issues["pov"].append({"scene": i, "title": r.get("scene", "")})
        # SCENE FIELD: a scene must MOVE >=1 character (resolve an action or change
        # a belief). 'moves' missing is already in `incomplete`; here we check that
        # what's there actually names a character and a delta.
        moves = (r.get("moves") or "").strip()
        if moves and moves not in ("-", "—"):
            parsed = _parse_moves(moves, known_names)
            valid = [m for m in parsed if m["valid"]]
            problem = None
            if not any(m["who"] for m in parsed):
                problem = "names no character ('moves' should be 'Name: <change>')"
            elif not valid:
                bad = ", ".join(sorted({m["who"] for m in parsed if m["who"]}))
                problem = f"moves '{bad}', who isn't a known character"
            elif all(m["kind"] == "unclear" for m in valid):
                problem = ("delta unclear — is an action RESOLVED or a belief "
                           "CHANGED? say which")
            if problem:
                issues["moves"].append({"scene": i, "title": r.get("scene", ""),
                                        "moves": moves, "problem": problem})

    tens = [_tension(r) for r in rows]
    have = [(i + 1, t) for i, t in enumerate(tens) if t is not None]
    if len(have) >= 4:
        vals = [t for _, t in have]
        # flat runs: >= 3 consecutive equal tensions
        run = 1
        for i in range(1, len(vals)):
            if vals[i] == vals[i - 1]:
                run += 1
                if run >= 3:
                    issues["flat_run"].append({"around_scene": have[i][0], "value": vals[i]})
            else:
                run = 1
        # sagging middle: mean of middle third <= mean of first third
        third = max(1, len(vals) // 3)
        first = sum(vals[:third]) / third
        mid = sum(vals[third:2 * third]) / max(1, len(vals[third:2 * third]))
        if mid < first:
            issues["escalation"].append(
                {"note": f"middle third mean tension {round(mid,1)} < opening third "
                         f"{round(first,1)} — sagging middle"})
        # climax: global max should be in the last ~25%
        gmax = max(vals)
        max_pos = have[vals.index(gmax)][0]
        if max_pos < 0.7 * n:
            issues["climax"].append(
                {"note": f"peak tension ({gmax}) at scene {max_pos}/{n} — climax should "
                         f"land in the final quarter, not the middle"})

    # valence monotony: all wins or all losses
    vs = [_valence(r) for r in rows]
    nz = [v for v in vs if v != 0]
    if len(nz) >= 4 and (all(v > 0 for v in nz) or all(v < 0 for v in nz)):
        issues["valence"].append(
            {"note": "every scene turns the same way (all "
                     + ("wins" if nz[0] > 0 else "losses")
                     + ") — alternate the yes/no to avoid a flat line"})

    moved = {i + 1: _moved_characters((r.get("moves") or ""), known_names)
             for i, r in enumerate(rows)}
    total = sum(len(v) for v in issues.values())
    hard = (len(issues["incomplete"]) + len(issues["escalation"])
            + len(issues["climax"]) + len(issues["moves"]))
    return {"scenes": n, "with_tension": len(have), "issues": issues,
            "tension_curve": tens, "moved": moved, "total": total,
            "passed": hard == 0}


def format_report(rep: dict) -> str:
    iss = rep["issues"]
    L = [f"STRUCTURE — {rep['scenes']} scene(s), {rep['with_tension']} with tension"]
    curve = rep["tension_curve"]
    if any(t is not None for t in curve):
        L.append("  tension curve: " + " ".join(
            (f"{int(t)}" if (t is not None and t == int(t)) else (str(t) if t is not None else "·"))
            for t in curve))
    if rep["passed"] and rep["total"] == 0:
        L.append("  ✓ every scene has goal/conflict/turn, MOVES a character; "
                 "tension escalates; climax lands late")
        return "\n".join(L)
    for i in iss["incomplete"]:
        L.append(f"  ✗ scene {i['scene']} missing {i['missing']}  ({i['title']})")
    for i in iss["moves"]:
        L.append(f"  ✗ scene {i['scene']} moves: {i['problem']}  "
                 f"(\"{i['moves']}\")")
    for i in iss["escalation"]:
        L.append(f"  ✗ {i['note']}")
    for i in iss["climax"]:
        L.append(f"  ✗ {i['note']}")
    for i in iss["flat_run"]:
        L.append(f"  • flat tension run near scene {i['around_scene']} (={i['value']})")
    for i in iss["valence"]:
        L.append(f"  • {i['note']}")
    for i in iss["pov"]:
        L.append(f"  • scene {i['scene']} has no POV declared ({i['title']})")
    return "\n".join(L)


def _cli(argv):
    if not argv:
        print("usage: python -m novelkit.structure <plan_or_ledger.md> [bible.md] [--json]")
        return 2
    text = Path(argv[0]).read_text(encoding="utf-8", errors="replace")
    rows = parse_ledger(text)
    if not rows:
        print("no SCENE LEDGER table found (expected a markdown pipe table under "
              "a '## SCENE LEDGER' heading).")
        return 2
    known = None
    bib_arg = next((a for a in argv[1:] if a.lower().endswith(".md") and "bible" in a.lower()), "")
    if not bib_arg:
        bib_arg = next((a for a in argv[1:] if a.lower().endswith(".md")), "")
    if bib_arg and Path(bib_arg).is_file():
        from . import bible as _B
        known = [n for c in _B.load(bib_arg).characters.values() for n in c.all_names]
    rep = check(rows, known_names=known)
    if "--json" in argv:
        import json
        print(json.dumps(rep, ensure_ascii=False, indent=2))
    else:
        print(format_report(rep))
    return 0 if rep["passed"] else 1


if __name__ == "__main__":
    sys.exit(_cli(sys.argv[1:]))
