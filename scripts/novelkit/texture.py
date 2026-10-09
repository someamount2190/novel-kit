"""texture.py — the IMMERSION / RICHNESS scan. PURE PYTHON. The COUNTERWEIGHT to
prose_scan.

prose_scan only ever punishes EXCESS (clichés, filter words, adverbs, purple prose).
Every deterministic force in this kit therefore pushes toward terseness — and nothing
checks for the opposite failure: prose so spare the world and the people are never
rendered. (Found by a reader: "your storytelling is sparse — no worldbuilding, no
character building.") This scan is the missing opposing force. It measures whether the
page is actually FURNISHED:

  • sensory_per_1k   — concrete sense-detail (sight/sound/smell/touch/taste). How much
                       can the reader physically perceive? Also how many of the five
                       senses are engaged (sight-only prose is flat).
  • world_per_1k     — named/specific world terms (proper nouns + capitalised
                       world-things). Is the secondary world ON the page or only in
                       the bible?
  • interiority_per_1k — mental-state words (felt/thought/seemed/knew/wondered…). Not
                       bad in itself, but prose that is all interior and no exterior
                       reads as a voice floating in a white room.
  • concreteness     — (sensory + world) / interiority. Below ~1 = in the character's
                       head, not in the world.

Calibrated by a GENRE PROFILE: immersive genres (isekai/fantasy/sf/horror/thriller)
demand high furnishing; interior/literary tolerates spare. This is a FLOOR check, not
a ceiling — it catches thinness; it can't judge whether the texture is GOOD. Pair it
with the cold read's immersion lens (SOP-07) and the bible's worldbuilding + per-
character physicality (SOP-06). A clean texture scan means "furnished enough to look
at", not "vivid".
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from . import manuscript as M

# --- sensory lexicons (high-precision; a density heuristic tolerates some noise) ---
SIGHT = set("""light dark darkness gold golden grey gray white black red green blue
    yellow silver pale bright dim shadow shadows glow gleam glint shimmer flicker
    flare colour color colours colors banner banners gleaming glowing shining shone
    glittered loomed flickered glinted crimson amber scarlet shade shades hue dappled
    veined""".split())
SOUND = set("""loud quiet silence silent hush hum hummed ring rang ringing clatter
    clattered whisper whispered echo echoed creak creaked hiss hissed roar roared
    murmur murmured thud clang note rasp rustle rustled footsteps snap crackle boom
    shout shouted scream cry thunder drip dripping toll bell""".split())
SMELL = set("""smell smelled scent scents reek reeked stink stank stench fragrant
    perfume musty smoke smoky acrid sweetish rot rotten sour-smelling odour odor
    incense damp-smell""".split())
TOUCH = set("""cold colder warm warmth hot heat rough smooth damp wet dry sharp soft
    hard heavy weight ache aching sting stung draught draft chill chilled grain
    grit slick sticky coarse brittle frozen burning numb prickle clammy bristled
    pressed gripped""".split())
TASTE = set("""bitter sweet salt salty sour metallic tang tangy taste tasted savour
    savor coppery""".split())

# physical/embodiment words — bodies, faces, appearance, clothing. Low density = the
# cast (and POV) are NAMED but never rendered as physical people. This is the metric
# that actually tracks "no character building" — sensory/world density does NOT.
PHYSICAL = set("""face faces eyes eye eyebrow eyebrows hair beard moustache jaw jawline
    cheek cheeks chin brow forehead mouth lips teeth nose throat neck shoulder shoulders
    chest arm arms elbow wrist wrists hand hands finger fingers knuckles palm back spine
    waist hip hips leg legs knee foot feet skin freckles scar scars wrinkles wrinkled
    tall short thin lean lanky broad stocky gaunt wiry burly slight stooped weathered
    grizzled greying balding bearded ruddy sallow sunburnt callused limp posture frame
    build cloak coat robe robes gown armour armor breastplate boots sleeve sleeves collar
    glove gloves hood tunic dress shawl scarf apron leather livery sash belt buckle""".split())

INTERIORITY = set("""feel felt feeling feels think thought thinks thinking wonder
    wondered wonders hope hoped hoping hopes seem seemed seems sense sensed senses
    realize realized realised suspect suspected decide decided knew know knows
    believe believed remember remembered imagine imagined mean meant understand
    understood idea memory mind doubt doubted considered reckoned figured
    expected supposed""".split())

_STOPCAPS = set("""The A An And But Or So He She They It We You I His Her Their Its
    Then There Here When Where What Why How That This These Those Now Yet As If Of To
    In On At For With From By Into Out Up Down Over Mr Mrs Ms Dr Sir Lady Lord Chapter
    Some Someone Something Could Would Should Will Shall Can May Might Must See Saw
    Look Looked Still Just Even Once Every Each Many Most Both Either Neither Nobody
    Nothing Maybe Perhaps Because Before After While Until Since Though Although No
    Yes Sorry Not Nor All Any Two One First Last Next Another Other Such About Said
    Asked Told Soon Later Always Never Often Well Like Only Almost""".split())

_WORD = re.compile(r"[A-Za-z][A-Za-z'’-]*")
_CAP = re.compile(r"[A-Z][a-z]{2,}")

# genre profile -> floors (per-1k sensory, per-1k world, min concreteness ratio, min senses)
PROFILES = {
    "immersive": {"sensory": 22.0, "world": 7.0, "ratio": 1.3, "senses": 3, "physical": 14.0},
    "general":   {"sensory": 16.0, "world": 4.0, "ratio": 1.0, "senses": 2, "physical": 9.0},
    "interior":  {"sensory": 10.0, "world": 2.0, "ratio": 0.6, "senses": 2, "physical": 7.0},
}
GENRE_PROFILE = {
    "isekai": "immersive", "fantasy": "immersive", "science-fiction": "immersive",
    "horror": "immersive", "thriller": "immersive", "historical": "immersive",
    "romance": "general", "mystery": "general",
    "literary-fiction": "interior",
}


def _sentence_initial_caps(text: str) -> set:
    """Capitalised tokens that occur at a sentence start (so we don't count them as
    proper nouns just for being capitalised)."""
    inits = set()
    for m in re.finditer(r"(?:^|[.!?]['\"”’)]?\s+)([A-Z][a-z]{2,})", text):
        inits.add(m.group(1))
    return inits


def scan(text: str, profile: str = "general") -> dict:
    words = [w.lower() for w in _WORD.findall(text)]
    n = len(words) or 1
    k = n / 1000.0

    senses = {"sight": 0, "sound": 0, "smell": 0, "touch": 0, "taste": 0}
    for w in words:
        if w in SIGHT: senses["sight"] += 1
        if w in SOUND: senses["sound"] += 1
        if w in SMELL: senses["smell"] += 1
        if w in TOUCH: senses["touch"] += 1
        if w in TASTE: senses["taste"] += 1
    sensory_total = sum(senses.values())
    senses_used = sum(1 for v in senses.values() if v > 0)

    interiority = sum(1 for w in words if w in INTERIORITY)
    physical = sum(1 for w in words if w in PHYSICAL)

    # world terms: capitalised tokens not at sentence start, not stopcaps, not "I"
    inits = _sentence_initial_caps(text)
    world_hits = []
    for m in _CAP.finditer(text):
        tok = m.group(0)
        # is this occurrence sentence-initial? cheap check: preceded by . ! ? or start
        start = m.start()
        prev = text[max(0, start - 3):start]
        if start == 0 or re.search(r"[.!?]['\"”’)]?\s*$", prev):
            continue
        if tok in _STOPCAPS:
            continue
        world_hits.append(tok)
    world_unique = sorted(set(world_hits))

    sensory_pk = round(sensory_total / k, 1)
    world_pk = round(len(world_hits) / k, 1)
    inter_pk = round(interiority / k, 1)
    phys_pk = round(physical / k, 1)
    ratio = round((sensory_total + len(world_hits)) / (interiority + 1), 2)
    # naming-vs-rendering: how much sensory/physical rendering accompanies each named
    # world term. High world density with little rendering = names, not a built world.
    render_per_world = round((sensory_total + physical) / (len(world_hits) + 1), 2)

    fl = PROFILES.get(profile, PROFILES["general"])
    flags = []
    if sensory_pk < fl["sensory"]:
        flags.append(f"sensory detail thin: {sensory_pk}/1k (floor {fl['sensory']}) — "
                     f"the reader can barely perceive the scene")
    if senses_used < fl["senses"]:
        flags.append(f"only {senses_used} of 5 senses engaged (want >= {fl['senses']}) — "
                     f"go beyond sight")
    if world_pk < fl["world"]:
        flags.append(f"world barely on the page: {world_pk}/1k named/specific terms "
                     f"(floor {fl['world']}) — render the world, don't leave it in the bible")
    if ratio < fl["ratio"]:
        flags.append(f"concreteness {ratio} (floor {fl['ratio']}) — too much interiority "
                     f"vs exterior detail; a voice in a white room")
    # The embodiment + naming-vs-rendering checks need enough text to be reliable;
    # below ~300 words densities are noise (and we don't punish good spare passages).
    if n >= 300:
        if phys_pk < fl["physical"]:
            flags.append(f"characters under-embodied: {phys_pk}/1k body/appearance words "
                         f"(floor {fl['physical']}) — they're NAMED, not rendered as people")
        # naming-without-rendering: a LOT of world terms but little rendering around them
        if world_pk >= max(fl["world"], 12.0) and render_per_world < 1.2:
            flags.append(f"naming without rendering: {world_pk}/1k world terms but only "
                         f"{render_per_world} sensory/physical words per term — the world "
                         f"is NAMED, not built")

    verdict = ("rich" if not flags and sensory_pk >= fl["sensory"] * 1.3 and phys_pk >= fl["physical"]
               else "ok" if not flags else "thin")
    return {
        "words": n, "profile": profile,
        "sensory_per_1k": sensory_pk, "senses": senses, "senses_used": senses_used,
        "world_per_1k": world_pk, "world_terms": world_unique[:24],
        "physical_per_1k": phys_pk, "render_per_world": render_per_world,
        "interiority_per_1k": inter_pk, "concreteness": ratio,
        "flags": flags, "passed": not flags, "verdict": verdict,
    }


def format_report(rep: dict) -> str:
    L = [f"TEXTURE — {rep['words']:,} words  (profile: {rep['profile']})  → {rep['verdict'].upper()}"]
    s = rep["senses"]
    L.append(f"  sensory: {rep['sensory_per_1k']}/1k  "
             f"[sight {s['sight']} sound {s['sound']} smell {s['smell']} "
             f"touch {s['touch']} taste {s['taste']}]  ({rep['senses_used']}/5 senses)")
    L.append(f"  world terms: {rep['world_per_1k']}/1k  "
             f"({', '.join(rep['world_terms'][:12])}{'…' if len(rep['world_terms'])>12 else ''})")
    L.append(f"  physical/embodiment: {rep['physical_per_1k']}/1k   "
             f"render-per-world-term: {rep['render_per_world']}")
    L.append(f"  interiority: {rep['interiority_per_1k']}/1k   concreteness: {rep['concreteness']}")
    if rep["passed"]:
        L.append("  ✓ furnished enough to look at (now: is the texture GOOD? — cold read, SOP-07)")
    else:
        L.append("  THIN:")
        for f in rep["flags"]:
            L.append(f"    ✗ {f}")
    return "\n".join(L)


def profile_for_genre(genre: str) -> str:
    return GENRE_PROFILE.get((genre or "").strip().lower(), "general")


def _cli(argv):
    if not argv:
        print("usage: python -m novelkit.texture <file> [--profile immersive|general|interior]\n"
              "       python -m novelkit.texture <file> --genre isekai")
        return 2
    text = Path(argv[0]).read_text(encoding="utf-8", errors="replace")
    profile = "general"
    if "--profile" in argv:
        profile = argv[argv.index("--profile") + 1]
    elif "--genre" in argv:
        profile = profile_for_genre(argv[argv.index("--genre") + 1])
    rep = scan(text, profile)
    if "--json" in argv:
        import json
        print(json.dumps(rep, ensure_ascii=False, indent=2))
    else:
        print(format_report(rep))
    return 0 if rep["passed"] else 1


if __name__ == "__main__":
    sys.exit(_cli(sys.argv[1:]))
