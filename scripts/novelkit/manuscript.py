"""manuscript.py — parse a prose manuscript into structure + stats. PURE PYTHON.

A manuscript is plain UTF-8 text or Markdown. We recognise:
  - Chapter breaks:  a line matching  ^#?\\s*(chapter|ch\\.?)\\s+\\w+   OR a markdown
                     "# ..." / "## ..." heading.
  - Scene breaks:    a lone line of  ***  or  ---  or  #  or  * * *  (centred sep),
                     or a markdown "### ..." heading.
Everything else is body prose. We never mutate the text; we only index into it.

Why this exists: the model loses track of where it is in a long manuscript and
mis-counts. Deterministic splitting + word counts give every later check a stable
coordinate system (chapter i / scene j / line n).
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

# --- line classifiers -------------------------------------------------------
_CHAPTER_RE = re.compile(r"^\s*#{0,2}\s*(chapter|ch\.?)\s+([0-9ivxlcdm]+|\w+)\b",
                         re.IGNORECASE)
_MD_H1H2_RE = re.compile(r"^\s*#{1,2}\s+\S")
_SCENE_SEP_RE = re.compile(r"^\s*(\*\s*\*\s*\*|-{3,}|\*{3,}|#)\s*$")
_MD_H3_RE = re.compile(r"^\s*#{3}\s+\S")

_WORD_RE = re.compile(r"[A-Za-z][A-Za-z'’-]*")
# sentence terminator: . ! ? possibly followed by quotes/brackets, then space/eol
_SENT_SPLIT_RE = re.compile(r'(?<=[.!?])["”\')\]]*\s+')


def is_chapter_break(line: str) -> bool:
    return bool(_CHAPTER_RE.match(line) or _MD_H1H2_RE.match(line))


def is_scene_break(line: str) -> bool:
    return bool(_SCENE_SEP_RE.match(line) or _MD_H3_RE.match(line))


@dataclass
class Scene:
    index: int          # global scene index (0-based)
    chapter: int        # owning chapter index (0-based)
    start_line: int     # 1-based line in the source file
    end_line: int
    heading: str        # the break line that opened it ("" if implicit)
    text: str

    @property
    def words(self) -> int:
        return len(_WORD_RE.findall(self.text))


@dataclass
class Chapter:
    index: int
    start_line: int
    end_line: int
    heading: str
    scenes: list = field(default_factory=list)

    @property
    def words(self) -> int:
        return sum(s.words for s in self.scenes)


@dataclass
class Manuscript:
    path: str
    text: str
    lines: list
    chapters: list = field(default_factory=list)

    @property
    def scenes(self) -> list:
        out = []
        for ch in self.chapters:
            out.extend(ch.scenes)
        return out

    @property
    def words(self) -> int:
        return len(_WORD_RE.findall(self.text))


def parse(text: str, path: str = "<memory>") -> Manuscript:
    """Split text into Chapter -> Scene with 1-based line spans."""
    lines = text.splitlines()
    ms = Manuscript(path=path, text=text, lines=lines)

    # First pass: find chapter boundaries (line numbers, 1-based).
    chap_starts = [i for i, ln in enumerate(lines) if is_chapter_break(ln)]
    if not chap_starts or chap_starts[0] != 0:
        chap_starts = [0] + [c for c in chap_starts if c != 0]

    for ci, start in enumerate(chap_starts):
        end = (chap_starts[ci + 1] - 1) if ci + 1 < len(chap_starts) else len(lines) - 1
        heading = lines[start].strip() if is_chapter_break(lines[start]) else ""
        chap = Chapter(index=ci, start_line=start + 1, end_line=end + 1, heading=heading)
        ms.chapters.append(chap)

        # body of this chapter = lines (start.. end), minus the heading line itself
        body_start = start + 1 if heading else start
        _split_scenes(chap, lines, body_start, end, ms)

    # Renumber scenes globally.
    gi = 0
    for ch in ms.chapters:
        for sc in ch.scenes:
            sc.index = gi
            gi += 1
    return ms


def _split_scenes(chap: Chapter, lines: list, body_start: int, end: int, ms: Manuscript):
    seg_start = body_start
    pending_heading = ""
    i = body_start
    scenes_raw = []  # (start_line0, end_line0, heading)
    while i <= end:
        if is_scene_break(lines[i]):
            if i > seg_start:
                scenes_raw.append((seg_start, i - 1, pending_heading))
            pending_heading = lines[i].strip()
            seg_start = i + 1
        i += 1
    if seg_start <= end:
        scenes_raw.append((seg_start, end, pending_heading))

    for (s0, e0, hd) in scenes_raw:
        # trim leading/trailing blank lines for the text body
        body = "\n".join(lines[s0:e0 + 1]).strip("\n")
        if not body.strip() and not hd:
            continue
        chap.scenes.append(Scene(index=0, chapter=chap.index,
                                 start_line=s0 + 1, end_line=e0 + 1,
                                 heading=hd, text=body))
    # a chapter with zero detected scenes still gets one implicit scene
    if not chap.scenes:
        body = "\n".join(lines[body_start:end + 1]).strip("\n")
        chap.scenes.append(Scene(index=0, chapter=chap.index,
                                 start_line=body_start + 1, end_line=end + 1,
                                 heading="", text=body))


def sentences(text: str) -> list:
    """Naive but serviceable sentence split (ignores abbreviations — fine for stats)."""
    text = text.replace("\n", " ")
    parts = _SENT_SPLIT_RE.split(text)
    return [p.strip() for p in parts if p.strip()]


def word_list(text: str) -> list:
    return _WORD_RE.findall(text)


def stats(text: str) -> dict:
    words = word_list(text)
    sents = sentences(text)
    slens = [len(_WORD_RE.findall(s)) for s in sents] or [0]
    n = len(words)
    uniq = len({w.lower() for w in words})
    mean = sum(slens) / len(slens)
    var = sum((x - mean) ** 2 for x in slens) / len(slens)
    return {
        "words": n,
        "sentences": len(sents),
        "unique_words": uniq,
        "type_token_ratio": round(uniq / n, 3) if n else 0.0,
        "mean_sentence_len": round(mean, 1),
        "sentence_len_stdev": round(var ** 0.5, 1),
        "longest_sentence": max(slens),
        "shortest_sentence": min(slens),
    }


def load(path: str) -> Manuscript:
    p = Path(path)
    text = p.read_text(encoding="utf-8", errors="replace")
    return parse(text, path=str(p))


def _cli(argv: list) -> int:
    if not argv:
        print("usage: python -m novelkit.manuscript <manuscript.(md|txt)>")
        return 2
    ms = load(argv[0])
    print(f"manuscript: {ms.path}")
    print(f"  total words: {ms.words:,}   chapters: {len(ms.chapters)}   "
          f"scenes: {len(ms.scenes)}")
    st = stats(ms.text)
    print(f"  sentences: {st['sentences']:,}   mean len: {st['mean_sentence_len']} "
          f"(stdev {st['sentence_len_stdev']})   TTR: {st['type_token_ratio']}")
    print()
    for ch in ms.chapters:
        head = ch.heading or f"(chapter {ch.index + 1}, no heading)"
        print(f"  [{ch.index + 1}] {head}  — {ch.words:,} w, {len(ch.scenes)} scene(s)")
        for sc in ch.scenes:
            h = sc.heading or "·"
            print(f"       scene {sc.index + 1}  L{sc.start_line}-{sc.end_line}  "
                  f"{sc.words:,} w  {h}")
    return 0


if __name__ == "__main__":
    sys.exit(_cli(sys.argv[1:]))
