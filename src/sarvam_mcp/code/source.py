"""Fetch + cache ``docs.sarvam.ai/llms-full.txt`` for the docs search tool.

We pull the whole single-file LLM-friendly docs dump and cache locally with
a 1-hour TTL. This is the same artifact the Sarvam team publishes for AI
agents to consume; using it directly keeps us in sync with Sarvam's own docs
without scraping HTML.
"""

from __future__ import annotations

import os
import time
from pathlib import Path

import httpx

DOCS_URL_DEFAULT = "https://docs.sarvam.ai/llms-full.txt"
DEFAULT_CACHE_TTL = 60 * 60  # 1 hour

# Cache file lives under ~/.cache/sarvam-mcp/docs.txt by default.
def _cache_path() -> Path:
    base = os.environ.get("XDG_CACHE_HOME", str(Path.home() / ".cache"))
    p = Path(base) / "sarvam-mcp" / "docs.txt"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def _ttl_seconds() -> int:
    raw = os.environ.get("SARVAM_DOCS_CACHE_TTL")
    try:
        return int(raw) if raw else DEFAULT_CACHE_TTL
    except ValueError:
        return DEFAULT_CACHE_TTL


def _docs_url() -> str:
    return os.environ.get("SARVAM_DOCS_URL", DOCS_URL_DEFAULT)


async def fetch_docs(force_refresh: bool = False) -> str:
    """Return the docs text, refreshing the cache if it's stale."""
    cache = _cache_path()
    if cache.exists() and not force_refresh:
        age = time.time() - cache.stat().st_mtime
        if age < _ttl_seconds():
            return cache.read_text()

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(_docs_url())
        response.raise_for_status()
    text = response.text
    cache.write_text(text)
    return text
