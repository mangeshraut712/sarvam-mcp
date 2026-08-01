"""Unit tests for TTS REST body construction (no API key)."""

from __future__ import annotations

from sarvam_mcp.tools.tts import _speak_body


def test_speak_body_uses_text_not_inputs_for_v3():
    body = _speak_body(
        text="hello",
        target_language_code="en-IN",
        speaker="priya",
        speech_sample_rate=24000,
        model="bulbul:v3",
        pace=1.0,
        pitch=0.1,
        loudness=1.5,
        enable_preprocessing=True,
    )
    assert body["text"] == "hello"
    assert "inputs" not in body
    assert "pitch" not in body
    assert "loudness" not in body
    assert "enable_preprocessing" not in body
    assert body["pace"] == 1.0
