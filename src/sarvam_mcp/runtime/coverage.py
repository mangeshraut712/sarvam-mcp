"""Map study-note sections to code in this repo (honest: similar work, not full ML)."""

from __future__ import annotations

# Practice code vs notes-only. A* is documented, not a training stack.
STUDY_COVERAGE: dict[str, str] = {
    "A1-A5": "docs/ON_DEVICE.md + sarvam_code_ondevice_runtime (no weight training)",
    "B1": "runtime/device.py + Supervisor comments",
    "B2": "docs (mmap/safetensors/GGUF) — no pickle loader",
    "B3": "runtime/quant.py weight_bytes / size_vs_fp16",
    "B4": "runtime/kv_budget.py mha/mqa/gqa",
    "B5": "docs engines; choose_backend probes preference",
    "B6": "runtime/breaker.py CircuitBreaker",
    "B7": "kv_budget + warmup.WarmPool + lru",
    "B8": "runtime/replay.py + events.stream_event",
    "B9": "runtime/scheduler.py + admission.admit",
    "B10": "runtime/supervisor.py + WarmPool",
    "B11": "runtime/errors.py + resume_from_seq",
    "B12": "admission unload/queue/refuse",
    "B13": "runtime/metrics.py percentile",
    "B14": "docs thermal — no OS sensors in CI",
    "B15": "docs; no pickle load path",
    "B16": "docs staged rollout",
    "B17": "docs prior art",
    "C1": "runtime/lru.py",
    "C3": "runtime/breaker.py",
    "C5": "lru + replay ring buffer",
}
