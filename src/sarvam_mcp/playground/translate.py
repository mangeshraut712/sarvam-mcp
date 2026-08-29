"""Shared translation used by the Vaani web app and WebMCP translate_content.

Reuses workflows._helpers.translate_text — the same /translate path as
sarvam_tools_translate (MCP). Default model is mayura:v1 so source auto-detect
matches the MCP tool. When source is auto, we run language ID first because
some Translate models reject the literal code ``auto``.
"""

from __future__ import annotations

import time
from typing import Any

from sarvam_mcp.http.errors import SarvamAPIError
from sarvam_mcp.playground.pipeline import build_playground_context
from sarvam_mcp.workflows._helpers import identify_language, translate_text

DEFAULT_MODEL = "mayura:v1"

ALLOWED_TARGETS = {
    "en-IN",
    "hi-IN",
    "bn-IN",
    "ta-IN",
    "te-IN",
    "gu-IN",
    "kn-IN",
    "ml-IN",
    "mr-IN",
    "pa-IN",
    "od-IN",
    "as-IN",
    "ur-IN",
    "ne-IN",
    "kok-IN",
    "ks-IN",
    "sd-IN",
    "sa-IN",
    "sat-IN",
    "mni-IN",
    "brx-IN",
    "mai-IN",
    "doi-IN",
}


async def translate_content(
    text: str,
    target_language: str,
    *,
    source_language: str = "auto",
    model: str = DEFAULT_MODEL,
) -> dict[str, Any]:
    """Translate text into an Indic (or English) BCP-47 target."""
    cleaned = text.strip()
    if not cleaned:
        return {"ok": False, "error": "text is required."}

    target = target_language.strip()
    if target not in ALLOWED_TARGETS:
        return {
            "ok": False,
            "error": f"Unsupported targetLanguage '{target}'. Use a BCP-47 code such as mr-IN.",
        }

    sc = build_playground_context()
    t0 = time.perf_counter()
    try:
        src = source_language.strip() if source_language else "auto"
        if src in {"", "unknown", "auto"}:
            detected, _script = await identify_language(sc, cleaned)
            src = detected if detected and detected not in {"unknown", "auto"} else "en-IN"

        translated = await translate_text(
            sc,
            cleaned,
            source_language_code=src,
            target_language_code=target,
            model=model,
        )
    except SarvamAPIError as exc:
        latency_ms = round((time.perf_counter() - t0) * 1000, 1)
        return {
            "ok": False,
            "error": str(exc),
            "latency_ms": latency_ms,
        }
    finally:
        await sc.client.aclose()

    latency_ms = round((time.perf_counter() - t0) * 1000, 1)
    return {
        "ok": True,
        "translated_text": translated,
        "source_language_code": src,
        "target_language_code": target,
        "latency_ms": latency_ms,
    }
