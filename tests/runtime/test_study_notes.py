"""Cover study-note mechanisms we implement (math + control plane, not weights)."""

from __future__ import annotations

import pytest

from sarvam_mcp.runtime.admission import admit
from sarvam_mcp.runtime.breaker import CircuitBreaker
from sarvam_mcp.runtime.coverage import STUDY_COVERAGE
from sarvam_mcp.runtime.errors import InferenceClientError, ResourceExhaustedError
from sarvam_mcp.runtime.kv_budget import kv_cache_bytes, kv_heads, max_context_tokens
from sarvam_mcp.runtime.lru import LruCache, LruK
from sarvam_mcp.runtime.metrics import percentile
from sarvam_mcp.runtime.quant import size_vs_fp16, weight_bytes
from sarvam_mcp.runtime.replay import TokenReplayBuffer
from sarvam_mcp.runtime.scheduler import aged_priority
from sarvam_mcp.runtime.warmup import WarmPool


def test_study_map_has_core_sections() -> None:
    for key in ("B3", "B4", "B6", "B8", "B9", "B10", "B11", "B12", "B13", "C1", "C5"):
        assert key in STUDY_COVERAGE


def test_circuit_breaker_opens_and_probes() -> None:
    clock = {"t": 0.0}

    def now() -> float:
        return clock["t"]

    br = CircuitBreaker(failure_threshold=2, cooldown_s=5, clock=now)
    br.record_failure()
    assert br.allow() is True
    br.record_failure()
    assert br.state == "open"
    assert br.allow() is False
    clock["t"] = 6
    assert br.allow() is True
    assert br.state == "half_open"
    br.record_success()
    assert br.state == "closed"


def test_replay_ages_out() -> None:
    buf = TokenReplayBuffer(maxlen=2)
    buf.append(0, "a")
    buf.append(1, "b")
    buf.append(2, "c")
    assert buf.replay_from(0) is None
    assert buf.replay_from(1) == [(1, "b"), (2, "c")]


def test_admission_levers() -> None:
    assert admit(loaded_mb=100, incoming_mb=50, budget_mb=200, queue_depth=0, max_queue=2) == "accept"
    assert (
        admit(
            loaded_mb=180,
            incoming_mb=50,
            budget_mb=200,
            queue_depth=0,
            max_queue=2,
            can_unload_mb=40,
        )
        == "unload"
    )
    assert (
        admit(loaded_mb=190, incoming_mb=50, budget_mb=200, queue_depth=0, max_queue=2)
        == "queue"
    )
    with pytest.raises(ResourceExhaustedError):
        admit(loaded_mb=190, incoming_mb=50, budget_mb=200, queue_depth=2, max_queue=2)
    with pytest.raises(InferenceClientError):
        admit(
            loaded_mb=0,
            incoming_mb=1,
            budget_mb=10,
            queue_depth=0,
            max_queue=1,
            prompt_ok=False,
        )


def test_lru_and_lruk() -> None:
    lru = LruCache(2)
    assert lru.touch("a", 10) is None
    assert lru.touch("b", 10) is None
    assert lru.touch("c", 10) == "a"
    k = LruK(k=2)
    k.touch("hot")
    k.touch("hot")
    k.touch("cold")
    assert k.victim(["hot", "cold"]) == "cold"


def test_kv_gqa_smaller_than_mha() -> None:
    kwargs = dict(layers=32, num_heads=32, head_dim=128, seq_len=1024)
    mha = kv_cache_bytes(**kwargs, attention="mha")
    gqa = kv_cache_bytes(**kwargs, attention="gqa", num_groups=8)
    mqa = kv_cache_bytes(**kwargs, attention="mqa")
    assert mqa < gqa < mha
    assert kv_heads("mqa", 32) == 1
    assert (
        max_context_tokens(
            kv_budget_bytes=mha,
            layers=32,
            num_heads=32,
            head_dim=128,
            attention="mha",
        )
        == 1024
    )


def test_quant_int4_is_quarter_fp16() -> None:
    assert size_vs_fp16(4) == 0.25
    assert weight_bytes(1_000_000, 8) == 1_000_000


def test_warm_pool_handoff_beats_cold() -> None:
    pool = WarmPool()
    assert pool.recover_ms() == 40
    assert pool.recover_ms() == 2500


def test_percentiles_and_aging() -> None:
    samples = [10, 20, 30, 40, 100]
    assert percentile(samples, 50) == 30
    assert percentile(samples, 99) == 100
    assert aged_priority(1, 3500) == 4
