"""On-device runtime practice code mapped to the study notes (not a take-home)."""

from sarvam_mcp.runtime.admission import admit
from sarvam_mcp.runtime.breaker import CircuitBreaker
from sarvam_mcp.runtime.coverage import STUDY_COVERAGE
from sarvam_mcp.runtime.device import DeviceProfile, can_load_model, choose_backend
from sarvam_mcp.runtime.errors import (
    FatalInferenceError,
    InferenceClientError,
    ResourceExhaustedError,
    TransientInferenceError,
)
from sarvam_mcp.runtime.events import stream_event
from sarvam_mcp.runtime.kv_budget import kv_cache_bytes, max_context_tokens
from sarvam_mcp.runtime.lru import LruCache, LruK
from sarvam_mcp.runtime.metrics import percentile
from sarvam_mcp.runtime.quant import size_vs_fp16, weight_bytes
from sarvam_mcp.runtime.replay import TokenReplayBuffer
from sarvam_mcp.runtime.scheduler import SlotScheduler, aged_priority
from sarvam_mcp.runtime.supervisor import Supervisor, WorkerCrashError, echo_tokens
from sarvam_mcp.runtime.warmup import WarmPool

__all__ = [
    "STUDY_COVERAGE",
    "CircuitBreaker",
    "DeviceProfile",
    "FatalInferenceError",
    "InferenceClientError",
    "LruCache",
    "LruK",
    "ResourceExhaustedError",
    "SlotScheduler",
    "Supervisor",
    "TokenReplayBuffer",
    "TransientInferenceError",
    "WarmPool",
    "WorkerCrashError",
    "admit",
    "aged_priority",
    "can_load_model",
    "choose_backend",
    "echo_tokens",
    "kv_cache_bytes",
    "max_context_tokens",
    "percentile",
    "size_vs_fp16",
    "stream_event",
    "weight_bytes",
]
