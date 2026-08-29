"""Tests for Vaani / playground translate_content (shared with WebMCP)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

from sarvam_mcp.http.errors import SarvamCreditsError
from sarvam_mcp.playground.translate import translate_content


async def test_translate_content_happy_path() -> None:
    sc = MagicMock()
    sc.client.aclose = AsyncMock()

    with (
        patch(
            "sarvam_mcp.playground.translate.build_playground_context",
            return_value=sc,
        ),
        patch(
            "sarvam_mcp.playground.translate.identify_language",
            new_callable=AsyncMock,
            return_value=("en-IN", "Latin"),
        ) as mock_lid,
        patch(
            "sarvam_mcp.playground.translate.translate_text",
            new_callable=AsyncMock,
            return_value="नमस्कार",
        ) as mock_tr,
    ):
        result = await translate_content("Hello", "hi-IN")

    assert result["ok"] is True
    assert result["translated_text"] == "नमस्कार"
    assert result["source_language_code"] == "en-IN"
    assert result["target_language_code"] == "hi-IN"
    mock_lid.assert_awaited()
    mock_tr.assert_awaited_once()
    kwargs = mock_tr.await_args.kwargs
    assert kwargs["target_language_code"] == "hi-IN"
    assert kwargs["source_language_code"] == "en-IN"
    assert kwargs["model"] == "mayura:v1"


async def test_translate_content_rejects_empty_and_bad_target() -> None:
    empty = await translate_content("   ", "mr-IN")
    assert empty["ok"] is False

    bad = await translate_content("hello", "xx-XX")
    assert bad["ok"] is False
    assert "Unsupported" in bad["error"]


async def test_translate_content_maps_credits_error() -> None:
    sc = MagicMock()
    sc.client.aclose = AsyncMock()

    with (
        patch(
            "sarvam_mcp.playground.translate.build_playground_context",
            return_value=sc,
        ),
        patch(
            "sarvam_mcp.playground.translate.identify_language",
            new_callable=AsyncMock,
            side_effect=SarvamCreditsError("No credits remaining."),
        ),
    ):
        result = await translate_content("Hello", "mr-IN")

    assert result["ok"] is False
    assert "credit" in result["error"].lower()
    sc.client.aclose.assert_awaited()
