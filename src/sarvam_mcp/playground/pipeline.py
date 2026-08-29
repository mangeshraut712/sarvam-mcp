"""Playground voice pipeline — composes existing workflow helpers with per-step timing."""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from sarvam_mcp._registry import ServerContext
from sarvam_mcp.audio import ResourceSink
from sarvam_mcp.http import SarvamClient
from sarvam_mcp.auth.api_key import StaticKeyProvider
from sarvam_mcp.auth.context import set_auth
from sarvam_mcp.config import Config
from sarvam_mcp.workflows._helpers import (
    coerce_tts_language,
    identify_language,
    llm_complete,
    stt_transcribe,
    tts_synthesize,
)

DEFAULT_SYSTEM_PROMPT = (
    "You are a concise, helpful assistant fluent in Indic languages. "
    "Answer in the same language as the user unless they ask otherwise. "
    "Keep replies short — one or two sentences for voice playback."
)


@dataclass(frozen=True)
class PipelineStep:
    name: str
    status: str
    latency_ms: float
    detail: str | None = None


def build_playground_context() -> ServerContext:
    """Build a ServerContext for the playground (resources sink for browser playback)."""
    config = Config.load()
    if not config.api_key:
        raise RuntimeError(
            "No API key found. Set SARVAM_API_KEY or ~/.sarvam/credentials before using the playground."
        )
    set_auth(StaticKeyProvider(config.api_key))
    client = SarvamClient(config.base_url)
    return ServerContext(config=config, client=client, audio_sink=ResourceSink())


async def run_pipeline(
    audio_path: Path,
    *,
    system_prompt: str = DEFAULT_SYSTEM_PROMPT,
) -> dict[str, Any]:
    """Run STT → Lang ID → LLM → TTS and return a JSON-serializable result."""
    sc = build_playground_context()
    steps: list[PipelineStep] = []

    try:
        # --- STT ---
        t0 = time.perf_counter()
        transcript, stt_lang = await stt_transcribe(sc, audio_path)
        stt_ms = (time.perf_counter() - t0) * 1000
        if not transcript.strip():
            steps.append(PipelineStep("STT", "error", stt_ms, "Empty transcript"))
            return _error_result(steps, "STT returned an empty transcript.")
        steps.append(
            PipelineStep(
                "STT",
                "ok",
                stt_ms,
                stt_lang,
            )
        )

        # --- Language ID ---
        t0 = time.perf_counter()
        lid_lang, script = await identify_language(sc, transcript)
        lid_ms = (time.perf_counter() - t0) * 1000
        detected_lang = lid_lang or stt_lang
        detail = detected_lang or "unknown"
        if script:
            detail = f"{detail} ({script})"
        steps.append(PipelineStep("Lang ID", "ok", lid_ms, detail))

        # --- LLM ---
        t0 = time.perf_counter()
        reply_text = await llm_complete(
            sc,
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": transcript},
            ],
        )
        llm_ms = (time.perf_counter() - t0) * 1000
        if not reply_text:
            steps.append(PipelineStep("LLM", "error", llm_ms, "Empty reply"))
            return _error_result(steps, "LLM returned an empty reply.")
        steps.append(PipelineStep("LLM", "ok", llm_ms))

        # --- TTS ---
        tts_lang = coerce_tts_language(detected_lang)
        t0 = time.perf_counter()
        stored = await tts_synthesize(
            sc,
            reply_text,
            target_language_code=tts_lang,
            filename_prefix="playground",
        )
        tts_ms = (time.perf_counter() - t0) * 1000
        steps.append(PipelineStep("TTS", "ok", tts_ms, tts_lang))

        return {
            "ok": True,
            "transcript": transcript,
            "detected_language": detected_lang,
            "script_code": script,
            "reply_language": tts_lang,
            "reply_text": reply_text,
            "audio_base64": stored.base64_data,
            "audio_mime_type": stored.mime_type,
            "steps": [_step_dict(s) for s in steps],
        }
    finally:
        await sc.client.aclose()


def _step_dict(step: PipelineStep) -> dict[str, Any]:
    out: dict[str, Any] = {
        "name": step.name,
        "status": step.status,
        "latency_ms": round(step.latency_ms, 1),
    }
    if step.detail:
        out["detail"] = step.detail
    return out


def _error_result(steps: list[PipelineStep], message: str) -> dict[str, Any]:
    return {
        "ok": False,
        "error": message,
        "steps": [_step_dict(s) for s in steps],
    }
