"""Naive keyword + heading-rank search over the docs dump.

v1 strategy:
  1. Split the document into chunks at H1/H2 headings (markdown ``#`` /``##``).
  2. For each chunk, build an inverted index of word → count.
  3. Score: `2 * heading_match + sum(term_freq_in_body) / chunk_len`.

This is intentionally simple. For a docs corpus that's ~100 KB, it returns
high-quality results for the kinds of queries an agent issues (endpoint
names, parameter names, model names). Upgrade path: swap this module for
a vector-embedding index without changing tool code.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_HEADING_RE = re.compile(r"^(#{1,3})\s+(.+?)\s*$", re.MULTILINE)
_WORD_RE = re.compile(r"[a-zA-Z][a-zA-Z0-9_/-]+")


@dataclass
class DocChunk:
    """One section of the docs, addressable by its heading."""

    heading: str         # human-readable section title
    level: int           # 1, 2, or 3
    text: str            # full section body (incl. heading line)
    anchor: str          # github-style heading anchor for URL fragment

    @property
    def url(self) -> str:
        # Best-effort: docs.sarvam.ai uses heading anchors. Without exact page
        # mapping we point at the docs root; the heading + snippet make the
        # match findable manually.
        return f"https://docs.sarvam.ai/#{self.anchor}"


def chunk_docs(text: str) -> list[DocChunk]:
    """Split full docs text into sections by H1/H2/H3 markers."""
    headings = list(_HEADING_RE.finditer(text))
    if not headings:
        return [DocChunk(heading="docs", level=1, text=text, anchor="docs")]

    chunks: list[DocChunk] = []
    for i, match in enumerate(headings):
        start = match.start()
        end = headings[i + 1].start() if i + 1 < len(headings) else len(text)
        level = len(match.group(1))
        title = match.group(2).strip()
        body = text[start:end].strip()
        anchor = _slugify(title)
        chunks.append(DocChunk(heading=title, level=level, text=body, anchor=anchor))
    return chunks


def _slugify(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_]+", "-", s)
    return s.strip("-")


@dataclass
class SearchHit:
    chunk: DocChunk
    score: float
    snippet: str


def search(chunks: list[DocChunk], query: str, *, limit: int = 5) -> list[SearchHit]:
    """Rank chunks by keyword overlap with the query."""
    terms = [t.lower() for t in _WORD_RE.findall(query) if len(t) > 1]
    if not terms:
        return []

    hits: list[SearchHit] = []
    for chunk in chunks:
        body = chunk.text.lower()
        title = chunk.heading.lower()
        score = 0.0
        for term in terms:
            if term in title:
                score += 2.0
            score += body.count(term)
        if score == 0:
            continue
        # Normalize by length so giant sections don't always win.
        score = score / max(1, len(chunk.text)) * 1000
        hits.append(SearchHit(chunk=chunk, score=score, snippet=_snippet(chunk.text, terms)))

    hits.sort(key=lambda h: h.score, reverse=True)
    return hits[:limit]


def _snippet(text: str, terms: list[str], window: int = 320) -> str:
    """Return a window of text around the first matching term."""
    lower = text.lower()
    idx = -1
    for term in terms:
        idx = lower.find(term)
        if idx >= 0:
            break
    if idx < 0:
        return text[:window].rstrip()
    half = window // 2
    start = max(0, idx - half)
    end = min(len(text), idx + half)
    out = text[start:end]
    if start > 0:
        out = "…" + out
    if end < len(text):
        out = out + "…"
    return out
