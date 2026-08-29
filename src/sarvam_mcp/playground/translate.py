"""Shared translation used by the Vaani web app and WebMCP translate_content.

Calls the same /translate endpoint as sarvam_tools_translate (MCP).
"""

from __future__ import annotations

import time
from typing import Any

from sarvam_mcp.http.errors import SarvamAPIError
from sarvam_mcp.playground.pipeline import build_playground_context
from sarvam_mcp.tools.translate import TRANSLATE_PATH

# Match sarvam_tools_translate: Mayura for short/stylized, Translate v1 for coverage.
DEFAULT_MODEL = "sarvam-translate:v1"

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

    src = "auto" if source_language in {"", "unknown", "auto"} else source_language
    body: dict[str, Any] = {
        "input": cleaned,
        "source_language_code": src,
        "target_language_code": target,
        "model": model,
        "numerals_format": "international",
        "enable_preprocessing": True,
    }
    if model == "mayura:v1":
        body["mode"] = "formal"

    sc = build_playground_context()
    t0 = time.perf_counter()
    try:
        payload, call = await sc.client.post_json(TRANSLATE_PATH, json_body=body)
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
        "translated_text": payload.get("translated_text", ""),
        "source_language_code": payload.get("source_language_code") or src,
        "target_language_code": target,
        "latency_ms": latency_ms,
        "request_id": call.request_id,
    }
