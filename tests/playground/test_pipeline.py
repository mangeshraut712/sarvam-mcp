"""Tests for the Voice Agent Playground pipeline."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from sarvam_mcp.audio import StoredAudio
from sarvam_mcp.http.errors import SarvamCreditsError
from sarvam_mcp.playground.pipeline import run_pipeline
from sarvam_mcp.workflows._helpers import coerce_tts_language


@pytest.mark.parametrize(
    ("detected", "expected"),
    [
        ("mr-IN", "mr-IN"),
        ("hi-IN", "hi-IN"),
        ("as-IN", "hi-IN"),
        (None, "hi-IN"),
    ],
)
def test_coerce_tts_language(detected: str | None, expected: str) -> None:
    assert coerce_tts_language(detected) == expected


async def test_run_pipeline_happy_path(tmp_path: Path) -> None:
    audio = tmp_path / "sample.webm"
    audio.write_bytes(b"fake-audio")

    stored = StoredAudio(
        file_path=None,
        resource_uri="sarvam://playground.wav",
        base64_data="d2F2",
        mime_type="audio/wav",
        size_bytes=4,
    )

    with (
        patch("sarvam_mcp.playground.pipeline.build_playground_context") as mock_ctx,
        patch("sarvam_mcp.playground.pipeline.stt_transcribe", new_callable=AsyncMock) as mock_stt,
        patch("sarvam_mcp.playground.pipeline.identify_language", new_callable=AsyncMock) as mock_lid,
        patch("sarvam_mcp.playground.pipeline.llm_complete", new_callable=AsyncMock) as mock_llm,
        patch("sarvam_mcp.playground.pipeline.tts_synthesize", new_callable=AsyncMock) as mock_tts,
    ):
        sc = AsyncMock()
        sc.client.aclose = AsyncMock()
        mock_ctx.return_value = sc

        mock_stt.return_value = ("नमस्कार", "mr-IN")
        mock_lid.return_value = ("mr-IN", "Devanagari")
        mock_llm.return_value = "हा एक छोटा उत्तर आहे."
        mock_tts.return_value = stored

        result = await run_pipeline(audio)

    assert result["ok"] is True
    assert result["transcript"] == "नमस्कार"
    assert result["detected_language"] == "mr-IN"
    assert result["reply_text"] == "हा एक छोटा उत्तर आहे."
    assert result["audio_base64"] == "d2F2"
    assert [step["name"] for step in result["steps"]] == ["STT", "Lang ID", "LLM", "TTS"]
    assert all(step["status"] == "ok" for step in result["steps"])
    assert all(step["latency_ms"] >= 0 for step in result["steps"])


async def test_run_pipeline_empty_transcript(tmp_path: Path) -> None:
    audio = tmp_path / "silent.webm"
    audio.write_bytes(b"silent")

    with (
        patch("sarvam_mcp.playground.pipeline.build_playground_context") as mock_ctx,
        patch("sarvam_mcp.playground.pipeline.stt_transcribe", new_callable=AsyncMock) as mock_stt,
    ):
        sc = AsyncMock()
        sc.client.aclose = AsyncMock()
        mock_ctx.return_value = sc
        mock_stt.return_value = ("", None)

        result = await run_pipeline(audio)

    assert result["ok"] is False
    assert "empty transcript" in result["error"].lower()
    assert result["steps"][0]["name"] == "STT"
    assert result["steps"][0]["status"] == "error"


async def test_run_pipeline_maps_credits_error(tmp_path: Path) -> None:
    audio = tmp_path / "clip.webm"
    audio.write_bytes(b"audio")

    with (
        patch("sarvam_mcp.playground.pipeline.build_playground_context") as mock_ctx,
        patch("sarvam_mcp.playground.pipeline.stt_transcribe", new_callable=AsyncMock) as mock_stt,
    ):
        sc = AsyncMock()
        sc.client.aclose = AsyncMock()
        mock_ctx.return_value = sc
        mock_stt.side_effect = SarvamCreditsError(
            "No credits available. Add credits at https://dashboard.sarvam.ai → Billing.",
            status_code=402,
        )

        result = await run_pipeline(audio)

    assert result["ok"] is False
    assert "credits" in result["error"].lower()
    assert result["steps"][0]["name"] == "STT"
    assert result["steps"][0]["status"] == "error"
