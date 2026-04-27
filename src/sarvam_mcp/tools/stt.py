"""Speech-to-text tools — transcribe, speech-to-translate, batch jobs."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Literal

from fastmcp import Context, FastMCP
from pydantic import Field

from sarvam_mcp.observability import measure_tool
from sarvam_mcp.tools._common import LanguageCode, ready_ctx

STT_PATH = "/speech-to-text"
STT_TRANSLATE_PATH = "/speech-to-text-translate"
STT_BATCH_PATH = "/speech-to-text/job/init"
STT_BATCH_STATUS_PATH = "/speech-to-text/job/status"

# Live-tested 2026-04-27 — these are the only model strings the API currently
# accepts for /speech-to-text. Note: there is no `saarika:v3` — `saarika:v2.5`
# IS the latest non-deprecated transcription model on this API surface.
SaarikaModel = Literal["saarika:v2.5"]
# Saaras family powers /speech-to-text-translate. Both v3 and v2.5 work today;
# v3 is newer and is the recommended default.
SaarasModel = Literal["saaras:v3", "saaras:v3-realtime", "saaras:v2.5"]


def register(mcp: FastMCP) -> None:
    @mcp.tool(
        name="sarvam_stt_transcribe",
        description=(
            "Transcribe an audio file in any of 23 Indian languages using Saarika v3.\n\n"
            "Use this for Indic-language audio. The default `language_code='unknown'` "
            "auto-detects, but specifying the language (e.g. `hi-IN`, `ta-IN`) gives "
            "better accuracy. For very long files (>30s), prefer `sarvam_stt_batch_submit`."
        ),
    )
    async def sarvam_stt_transcribe(
        ctx: Context,
        audio_path: str = Field(
            description="Absolute path to the audio file. Supports wav, mp3, ogg, flac, m4a."
        ),
        language_code: LanguageCode = Field(
            default="unknown",
            description="BCP-47 code, e.g. 'hi-IN'. Use 'unknown' to auto-detect.",
        ),
        with_timestamps: bool = Field(
            default=False, description="Include word-level timestamps in the response."
        ),
        model: SaarikaModel = Field(
            default="saarika:v2.5",
            description="Latest Saarika ASR model. `saarika:v3` does not exist — v2.5 is current.",
        ),
    ) -> dict[str, Any]:
        sc = await ready_ctx(ctx)
        path = Path(audio_path).expanduser()
        if not path.is_file():
            raise FileNotFoundError(f"Audio file not found: {path}")

        with measure_tool() as metrics:
            with path.open("rb") as fh:
                files = {"file": (path.name, fh, _guess_audio_mime(path))}
                data: dict[str, Any] = {
                    "model": model,
                    "language_code": language_code,
                    "with_timestamps": str(with_timestamps).lower(),
                }
                payload, call = await sc.client.post_multipart(
                    STT_PATH, data=data, files=files
                )
            metrics.merge(call)

        return {
            "transcript": payload.get("transcript", ""),
            "language_code": payload.get("language_code"),
            "diarized_transcript": payload.get("diarized_transcript"),
            "timestamps": payload.get("timestamps"),
            "observability": metrics.to_response_block(),
        }

    @mcp.tool(
        name="sarvam_stt_translate",
        description=(
            "Transcribe an Indic-language audio file directly into English text "
            "using Saaras. Optimized for telephony / mixed-language audio where "
            "you want English output regardless of the input language."
        ),
    )
    async def sarvam_stt_translate(
        ctx: Context,
        audio_path: str = Field(description="Absolute path to the audio file."),
        with_diarization: bool = Field(
            default=False, description="Return per-speaker turns."
        ),
        model: SaarasModel = Field(
            default="saaras:v3",
            description=(
                "Saaras model. `saaras:v3` (default, latest) | "
                "`saaras:v3-realtime` | `saaras:v2.5`."
            ),
        ),
    ) -> dict[str, Any]:
        sc = await ready_ctx(ctx)
        path = Path(audio_path).expanduser()
        if not path.is_file():
            raise FileNotFoundError(f"Audio file not found: {path}")

        with measure_tool() as metrics:
            with path.open("rb") as fh:
                files = {"file": (path.name, fh, _guess_audio_mime(path))}
                data: dict[str, Any] = {
                    "model": model,
                    "with_diarization": str(with_diarization).lower(),
                }
                payload, call = await sc.client.post_multipart(
                    STT_TRANSLATE_PATH, data=data, files=files
                )
            metrics.merge(call)

        return {
            "transcript": payload.get("transcript", ""),
            "language_code": payload.get("language_code"),
            "diarized_transcript": payload.get("diarized_transcript"),
            "observability": metrics.to_response_block(),
        }

    @mcp.tool(
        name="sarvam_stt_batch_submit",
        description=(
            "Initialize a batch (long-audio) transcription job. Returns a "
            "`job_id` plus pre-signed Azure Blob URLs: upload your audio "
            "file(s) to `input_storage_path`, then call "
            "`sarvam_stt_batch_status` to poll completion. Outputs land at "
            "`output_storage_path`. Use this for files >30s."
        ),
    )
    async def sarvam_stt_batch_submit(
        ctx: Context,
        language_code: LanguageCode = Field(default="unknown"),
        model: SaarikaModel = Field(default="saarika:v2.5"),
        with_timestamps: bool = Field(default=False),
    ) -> dict[str, Any]:
        # Note: this endpoint takes JSON only (no file upload here). The
        # caller uploads to the returned SAS URL after init.
        sc = await ready_ctx(ctx)
        body: dict[str, Any] = {"model": model, "with_timestamps": with_timestamps}
        if language_code != "unknown":
            body["language_code"] = language_code

        with measure_tool() as metrics:
            payload, call = await sc.client.post_json(STT_BATCH_PATH, json_body=body)
            metrics.merge(call)

        return {
            "job_id": payload.get("job_id"),
            "input_storage_path": payload.get("input_storage_path"),
            "output_storage_path": payload.get("output_storage_path"),
            "storage_container_type": payload.get("storage_container_type"),
            "submitted_at": time.time(),
            "next_steps": (
                "1) Upload your audio file(s) to `input_storage_path` (Azure SAS-signed). "
                "2) Poll with sarvam_stt_batch_status(job_id). "
                "3) Read results from `output_storage_path` once status='completed'."
            ),
            "observability": metrics.to_response_block(),
        }

    @mcp.tool(
        name="sarvam_stt_batch_status",
        description=(
            "Poll the status of a batch transcription job. Returns the transcript "
            "once `status == 'completed'`."
        ),
    )
    async def sarvam_stt_batch_status(
        ctx: Context,
        job_id: str = Field(description="The job_id returned by sarvam_stt_batch_submit."),
    ) -> dict[str, Any]:
        sc = await ready_ctx(ctx)
        with measure_tool() as metrics:
            payload, call = await sc.client.get_json(
                STT_BATCH_STATUS_PATH, params={"job_id": job_id}
            )
            metrics.merge(call)

        return {
            "job_id": job_id,
            "status": payload.get("job_state") or payload.get("status"),
            "transcript": payload.get("transcript"),
            "raw": payload,
            "observability": metrics.to_response_block(),
        }


def _guess_audio_mime(path: Path) -> str:
    suffix = path.suffix.lower().lstrip(".")
    return {
        "wav": "audio/wav",
        "mp3": "audio/mpeg",
        "ogg": "audio/ogg",
        "flac": "audio/flac",
        "m4a": "audio/mp4",
        "webm": "audio/webm",
    }.get(suffix, "application/octet-stream")
