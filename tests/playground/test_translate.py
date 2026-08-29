"""Tests for Vaani / playground translate_content (shared with WebMCP)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

from sarvam_mcp.http.errors import SarvamCreditsError
from sarvam_mcp.observability import CallMetrics
from sarvam_mcp.playground.translate import translate_content


async def test_translate_content_happy_path() -> None:
    payload = {"translated_text": "नमस्कार", "source_language_code": "en-IN"}
    call = CallMetrics(request_id="req-1")

    sc = MagicMock()
    sc.client.post_json = AsyncMock(return_value=(payload, call))
    sc.client.aclose = AsyncMock()

    with patch(
        "sarvam_mcp.playground.translate.build_playground_context",
        return_value=sc,
    ):
        result = await translate_content("Hello", "hi-IN")

    assert result["ok"] is True
    assert result["translated_text"] == "नमस्कार"
    assert result["target_language_code"] == "hi-IN"
    assert result["request_id"] == "req-1"
    sc.client.post_json.assert_awaited_once()
    body = sc.client.post_json.await_args.kwargs["json_body"]
    assert body["target_language_code"] == "hi-IN"
    assert body["model"] == "sarvam-translate:v1"


async def test_translate_content_rejects_empty_and_bad_target() -> None:
    empty = await translate_content("   ", "mr-IN")
    assert empty["ok"] is False

    bad = await translate_content("hello", "xx-XX")
    assert bad["ok"] is False
    assert "Unsupported" in bad["error"]


async def test_translate_content_maps_credits_error() -> None:
    sc = MagicMock()
    sc.client.post_json = AsyncMock(
        side_effect=SarvamCreditsError("No credits remaining.")
    )
    sc.client.aclose = AsyncMock()

    with patch(
        "sarvam_mcp.playground.translate.build_playground_context",
        return_value=sc,
    ):
        result = await translate_content("Hello", "mr-IN")

    assert result["ok"] is False
    assert "credits" in result["error"].lower() or "Credits" in result["error"]
    sc.client.aclose.assert_awaited()
