"""Observability helpers."""

from __future__ import annotations

import time

from sarvam_mcp.observability import (
    CallMetrics,
    measure_tool,
    metrics_from_response_headers,
)


def test_metrics_from_headers_parses_known_fields():
    m = metrics_from_response_headers(
        {
            "x-request-id": "req_42",
            "x-credits-used": "0.0125",
            "x-credits-remaining": "9999",
            "content-type": "application/json",
        }
    )
    assert m.request_id == "req_42"
    assert m.cost_credits == 0.0125
    assert m.quota_remaining == 9999.0


def test_metrics_from_headers_tolerates_missing():
    m = metrics_from_response_headers({})
    assert m.request_id is None
    assert m.cost_credits is None


def test_measure_tool_aggregates():
    with measure_tool() as metrics:
        metrics.merge(CallMetrics(request_id="r1", cost_credits=0.5, quota_remaining=100))
        metrics.merge(CallMetrics(request_id="r2", cost_credits=0.25, quota_remaining=99))
        time.sleep(0.005)

    block = metrics.to_response_block()
    assert block["upstream_calls"] == 2
    assert block["request_ids"] == ["r1", "r2"]
    assert abs(block["cost_credits"] - 0.75) < 1e-6
    assert block["quota_remaining"] == 99
    assert block["latency_ms"] >= 5.0


def test_measure_tool_omits_empty_fields():
    with measure_tool() as metrics:
        pass
    block = metrics.to_response_block()
    assert "request_ids" not in block
    assert "cost_credits" not in block
    assert "quota_remaining" not in block
