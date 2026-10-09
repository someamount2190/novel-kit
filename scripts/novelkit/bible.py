"""bible.py — the STORY BIBLE: machine-checkable canon. PURE PYTHON.

In a long manuscript the model contradicts its own established facts — a
character's eyes change colour, a name's spelling drifts, a planted gun never
fires. There is no "render" of a novel, but canon CAN be made checkable: commit
facts to a structured bible once, and `continuity.py` validates the prose against
it forever after. This module parses + represents that bible.

FORMAT (a markdown file; sections are case-insensitive H2 headings):

    # Story Bible: <title>

    ## CHARACTERS
    ### Mara Vance
    - aliases: Mara, Ms. Vance, the warden
    - eyes: grey
    - hair: black
    - age: 34
    - role: protagonist
    - voice: clipped; nautical metaphors; never swears
    - knows: that the boathouse is locked   # facts this character is aware of

    ## WORLD
    - setting: Harkness, a coastal town, 1890s
    - currency: shillings
    - rule: no magic exists

    ## TIMELINE
    - day 1: the flood
    - day 3: the body is found

    ## SETUP/PAYOFF
    - setup: locked boathouse @ch1 => payoff: @ch12 the key is found
    - setup: Mara never swears => payoff: she swears at the climax

    ## FORBIDDEN
    - the word "okay" (anachronistic for 1890s)

`- key: value` lines under a character become that character's attributes;
`aliases` and `knows` are split on commas/semicolons. Lines under WORLD/TIMELINE
are free facts. SETUP/PAYOFF lines use the `setup: X => payoff: Y` shape.
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

_H2 = re.compile(r"^\s*##\s+(.+?)\s*$")
_H3 = re.compile(r"^\s*###\s+(.+?)\s*$")
_KV = re.compile(r"^\s*[-*]\s*([A-Za-z][\w ]*?)\s*:\s*(.+?)\s*$")
_BULLET = re.compile(r"^\s*[-*]\s+(.+?)\s*$")
_SPLIT = re.compile(r"\s*[;,]\s*")

# attribute -> the noun(s) to look for in prose, and a value vocabulary to compare.
CHECKABLE_ATTRS = {
    # NOTE: "gaze" was dropped from the eye nouns — "dark/pale gaze" near a named
    # character (and generic colors like "dark basin") produced false contradictions.
    # Eye COLOUR is given via "eye(s)"; "gaze" carries expression, not colour.
    "eyes": (["eye", "eyes"], None),     # value vocab filled from COLORS
    "hair": (["hair", "locks", "mane"], None),
}
COLORS = {"black", "brown", "blond", "blonde", "blue", "green", "grey", "gray",
          "hazel", "amber", "red", "auburn", "ginger", "white", "silver", "golden",
          "dark", "fair", "chestnut", "copper", "violet", "pale"}


@dataclass
class Character:
    name: str
    attrs: dict = field(default_factory=dict)
    aliases: list = field(default_factory=list)
    knows: list = field(default_factory=list)

    @property
    def all_names(self) -> list:
        return [self.name] + list(self.aliases)


@dataclass
class SetupPayoff:
    setup: str
    payoff: str
    raw: str


@dataclass
class Bible:
    title: str = ""
    characters: dict = field(default_factory=dict)   # name -> Character
    world: list = field(default_factory=list)        # free facts
    timeline: list = field(default_factory=list)
    ledger: list = field(default_factory=list)       # SetupPayoff
    forbidden: list = field(default_factory=list)

    def character_by_any_name(self, token: str):
        t = (token or "").lower().strip()
        if not t:
            return None
        # exact full-name / alias match first
        for c in self.characters.values():
            if any(t == n.lower() for n in c.all_names):
                return c
        # fall back to a single-word match (e.g. "Mara" -> "Mara Vance")
        for c in self.characters.values():
            if any(t in n.lower().split() for n in c.all_names):
                return c
        return None


def parse(text: str) -> Bible:
    b = Bible()
    m = re.search(r"^#\s+Story Bible:?\s*(.*)$", text, re.IGNORECASE | re.MULTILINE)
    if m:
        b.title = m.group(1).strip()

    section = None
    cur_char = None
    for raw in text.splitlines():
        h2 = _H2.match(raw)
        if h2:
            section = h2.group(1).strip().lower()
            cur_char = None
            continue
        h3 = _H3.match(raw)
        if h3 and section and section.startswith("character"):
            name = h3.group(1).strip()
            cur_char = Character(name=name)
            b.characters[name] = cur_char
            continue

        if section and section.startswith("character") and cur_char is not None:
            kv = _KV.match(raw)
            if kv:
                key, val = kv.group(1).strip().lower(), kv.group(2).strip()
                if key == "aliases":
                    cur_char.aliases = [x for x in _SPLIT.split(val) if x]
                elif key == "knows":
                    cur_char.knows = [x for x in _SPLIT.split(val) if x]
                else:
                    cur_char.attrs[key] = val
            continue

        if section == "world":
            bm = _BULLET.match(raw)
            if bm:
                b.world.append(bm.group(1).strip())
        elif section == "timeline":
            bm = _BULLET.match(raw)
            if bm:
                b.timeline.append(bm.group(1).strip())
        elif section and "forbidden" in section:
            bm = _BULLET.match(raw)
            if bm:
                b.forbidden.append(bm.group(1).strip())
        elif section and ("setup" in section or "payoff" in section or "ledger" in section):
            bm = _BULLET.match(raw)
            if bm:
                line = bm.group(1).strip()
                parts = re.split(r"\s*=>\s*|\s*->\s*", line, maxsplit=1)
                setup = re.sub(r"^setup:\s*", "", parts[0], flags=re.IGNORECASE).strip()
                payoff = ""
                if len(parts) > 1:
                    payoff = re.sub(r"^payoff:\s*", "", parts[1], flags=re.IGNORECASE).strip()
                b.ledger.append(SetupPayoff(setup=setup, payoff=payoff, raw=line))
    return b


def load(path: str) -> Bible:
    return parse(Path(path).read_text(encoding="utf-8", errors="replace"))


SCAFFOLD = """# Story Bible: {title}

> Canon. `continuity.py` checks the manuscript against this. Commit a fact ONCE
> here, then never contradict it. Update this file the instant canon changes.

## CHARACTERS
### {protagonist}
- aliases:
- pronouns:         # she/her etc — sharpens continuity's pronoun resolution
- eyes:
- hair:
- age:
- role: protagonist
- traits:           # 3-5 personality traits + a defining flaw (the CHARACTER baseline)
- backstory:        # the wound/history that drives them — 1-3 sentences
- physicality:      # a RENDERED body + a signature mannerism (what we SEE, not just a name)
- voice:            # 2-3 concrete speech markers — diction, rhythm, what they never say
- wants:            # external goal
- needs:            # internal lack
- arc:              # from "<start belief>" to "<end belief>" — realised as a subplot in the plan
- knows:            # facts this POV is aware of (drives dramatic irony)

## WORLD
- setting:
- time period:
- rule:             # one hard rule of this world (tech/magic/social)

## WORLDBUILDING
<!-- Render the world so it can go ON THE PAGE, not just be named. Concrete, sensory,
     lived-in. Naming "the Weave" is not worldbuilding; this is. -->
- look & feel:      # what the place looks/sounds/smells like — sensory signature
- daily life:       # how ordinary people live; what the central rule (magic/tech) means in practice
- social order:     # classes, power, who's up/down, customs, money
- texture details:  # 3-5 concrete specifics (a food, a street sound, a ritual, an object)

## TIMELINE
- day 1:

## SETUP/PAYOFF
- setup:  => payoff:

## FORBIDDEN
- # anachronisms / words / facts that must NEVER appear
"""


def scaffold(title: str = "Untitled", protagonist: str = "Protagonist") -> str:
    return SCAFFOLD.format(title=title, protagonist=protagonist)


def summary(b: Bible) -> str:
    L = [f"STORY BIBLE: {b.title or '(untitled)'}"]
    L.append(f"  characters: {len(b.characters)}")
    for c in b.characters.values():
        checked = ", ".join(f"{k}={v}" for k, v in c.attrs.items()
                            if k in CHECKABLE_ATTRS)
        L.append(f"    • {c.name}"
                 + (f"  [{', '.join(c.aliases)}]" if c.aliases else "")
                 + (f"  ({checked})" if checked else ""))
    L.append(f"  world facts: {len(b.world)}   timeline: {len(b.timeline)}   "
             f"ledger: {len(b.ledger)}   forbidden: {len(b.forbidden)}")
    return "\n".join(L)


def _cli(argv):
    if not argv:
        print("usage: python -m novelkit.bible <bible.md>           (summarise)\n"
              "       python -m novelkit.bible --scaffold <title> [protagonist]")
        return 2
    if argv[0] == "--scaffold":
        title = argv[1] if len(argv) > 1 else "Untitled"
        prot = argv[2] if len(argv) > 2 else "Protagonist"
        print(scaffold(title, prot))
        return 0
    print(summary(load(argv[0])))
    return 0


if __name__ == "__main__":
    sys.exit(_cli(sys.argv[1:]))
