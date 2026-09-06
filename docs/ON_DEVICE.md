# On-device / local runtime (this fork)

Practice code for the **systems** half of on-device AI study notes. This is
**not** a hiring take-home and **not** a weight-loading engine.

## Study-note coverage

| Notes | In this repo | How |
|---|---|---|
| A1–A5 transformers / train / compress | Documented only | `sarvam_code_ondevice_runtime` |
| B1 different systems problem | Yes | comments + `DeviceProfile` |
| B2 formats / mmap | Documented | no pickle loader (on purpose) |
| B3 quantization | Similar | `quant.weight_bytes` / `size_vs_fp16` (math, not GPTQ) |
| B4 MHA/MQA/GQA | Yes | `kv_budget.py` |
| B5 engines | Partial | `choose_backend` + docs |
| B6 fallback + breaker | Yes | `CircuitBreaker` + no silent cloud |
| B7 KV + warm pool + swap | Yes | `kv_budget`, `WarmPool`, `LruCache` / `LruK` |
| B8 streaming + resume | Yes | `stream_event`, `TokenReplayBuffer`, supervisor |
| B9 slots + aging | Yes | `SlotScheduler`, `aged_priority` |
| B10 process isolation | Similar | `Supervisor` (task-isolated; not OS processes in CI) |
| B11 idempotency / errors | Yes | `resume_from_seq`, `errors.py` |
| B12 multi-model RAM | Yes | `admit` accept/unload/queue/refuse |
| B13 metrics | Similar | `percentile` (p50/p99) |
| B14–B17 power / security / rollout / prior art | Documented | `docs/ON_DEVICE.md` |
| C1 / C3 / C5 | Yes | LRU, breaker, ring buffer |

Map in code: `sarvam_mcp.runtime.coverage.STUDY_COVERAGE`.

## Official Sarvam GitHub

Cloud-first (`sarvam-mcp`, cookbook, skills, AI SDK). Open weights on HF; everyday Ollama still blocked on `sarvam_moe`.

```python
from sarvam_mcp.runtime import CircuitBreaker, admit, kv_cache_bytes

choose_backend = __import__("sarvam_mcp.runtime", fromlist=["choose_backend"]).choose_backend
```
