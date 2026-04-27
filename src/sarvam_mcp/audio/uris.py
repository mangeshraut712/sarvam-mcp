"""``sarvam://`` resource URI scheme.

Used when ``SARVAM_AUDIO_OUTPUT_MODE`` is ``resources`` or ``both`` — the
hosted MCP transport (v1.1) exposes URIs as MCP resources fetchable by the
client without disk access.
"""

from __future__ import annotations

from urllib.parse import quote, unquote, urlparse

SCHEME = "sarvam"


def build_resource_uri(filename: str) -> str:
    """Build a ``sarvam://<filename>`` URI. Filename is URL-quoted."""
    return f"{SCHEME}://{quote(filename, safe='')}"


def parse_resource_uri(uri: str) -> str:
    """Inverse of ``build_resource_uri``. Returns the filename or raises."""
    parsed = urlparse(uri)
    if parsed.scheme != SCHEME:
        raise ValueError(f"Not a sarvam:// URI: {uri!r}")
    # urlparse puts the host part in ``netloc`` for ``scheme://host`` URIs.
    raw = parsed.netloc or parsed.path.lstrip("/")
    if not raw:
        raise ValueError(f"sarvam:// URI is missing a filename: {uri!r}")
    return unquote(raw)
