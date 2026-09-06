"""Build-time notes for local / on-device runtimes (Sarvam cloud vs laptop)."""

from __future__ import annotations

from typing import Any, Literal

from fastmcp import Context, FastMCP
from pydantic import Field

Topic = Literal[
    "overview",
    "process_isolation",
    "hardware_fallback",
    "memory",
    "streaming",
    "scheduling",
    "idempotency",
    "sarvam_repos",
]

GUIDE: dict[str, dict[str, Any]] = {
    "overview": {
        "title": "On-device AI is a systems problem",
        "points": [
            "Sarvam's public GitHub (sarvam-mcp, cookbook, skills, AI SDK) is cloud API first.",
            "Open weights (sarvam-30b / 105b) are on Hugging Face.",
            "Laptop GGUF/Ollama is still blocked on llama.cpp sarvam_moe support.",
            "This repo implements study-note control-plane pieces (breaker, KV math, LRU, replay).",
        ],
    },
    "process_isolation": {
        "title": "Crash isolation",
        "points": [
            "Treat the inference worker as crash-prone; keep HTTP/MCP/API in a separate process or task.",
            "Keep a warm or fast-respawn worker so a die is not a multi-second cold start.",
            "See sarvam_mcp.runtime.Supervisor — workers raise WorkerCrashError; clients resume from seq.",
        ],
    },
    "hardware_fallback": {
        "title": "Hardware fallback",
        "points": [
            "Detect NPU/GPU/CPU at runtime; do not trust a static device marketing name.",
            "Never send tokens to the cloud unless the user opted in (privacy + surprise cost).",
            "DeviceProfile.allow_cloud defaults to False. choose_backend('cloud') raises otherwise.",
        ],
    },
    "memory": {
        "title": "Memory and models",
        "points": [
            "Quantization (int8/int4) trades quality for RAM and latency.",
            "KV cache grows with context; swap or refuse a second model when over budget.",
            "can_load_model(device, already_mb, incoming_mb) is the hard ceiling.",
        ],
    },
    "streaming": {
        "title": "Streaming",
        "points": [
            "Push tokens as they exist (SSE, IPC, or MCP notifications). Do not buffer the full reply.",
            "Use one typed event: type, request_id, seq, text/error — API, worker, and SDK must match.",
        ],
    },
    "scheduling": {
        "title": "Concurrency",
        "points": [
            "A phone has a handful of inference slots, not a cloud autoscaler.",
            "Weighted slots: interactive work must not be starved by background jobs.",
            "SlotScheduler refuses background the last slot while interactive waiters exist.",
        ],
    },
    "idempotency": {
        "title": "Idempotent streams",
        "points": [
            "A retry of a half-finished generation must reuse request_id and resume_from_seq.",
            "Appending the same tokens twice corrupts the user-visible stream.",
            "Supervisor caches tokens per request_id so resume continues, not restarts.",
        ],
    },
    "sarvam_repos": {
        "title": "Where this fits official Sarvam repos",
        "points": [
            "sarvamai/sarvam-mcp — cloud tools; this fork adds runtime/ + Vaani WebMCP.",
            "sarvamai/sarvam-ai-cookbook — cloud notebooks; a PR could add local vs hosted routing.",
            "sarvamai/skills — agent skills for STT/TTS/chat; an on-device skill waits on GGUF/Ollama.",
            "sarvamai/sarvam-ai-sdk — Vercel AI SDK provider for hosted chat/STT/TTS.",
            "sarvamai/model-deployments — empty placeholder as of last check.",
            "Community: mtr7x/sarvam-gguf + patched llama.cpp for 30B; Ollama still blocked.",
        ],
    },
}


def register(mcp: FastMCP) -> None:
    @mcp.tool(
        name="sarvam_code_ondevice_runtime",
        description=(
            "Build-time tool — local/on-device runtime patterns for Sarvam-class models. "
            "Does not call the cloud API. Does not reproduce any employer's interview assignment. "
            "For hosted chat now, use sarvam_tools_llm_complete."
        ),
    )
    async def sarvam_code_ondevice_runtime(
        ctx: Context,
        topic: Topic = Field(
            default="overview",
            description="Which slice of the local-runtime guide to return.",
        ),
    ) -> dict[str, Any]:
        _ = ctx
        return {"topic": topic, **GUIDE[topic]}
