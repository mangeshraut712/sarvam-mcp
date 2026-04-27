"""Latency / cost / quota / request-id tracking for tool responses.

Every tool response includes an ``observability`` block — agents can surface
quota warnings to the user, and developers can grep logs by request_id.
"""

from __future__ import annotations

import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any


@dataclass
class CallMetrics:
    """Per-API-call metrics. Aggregated up into the tool response."""

    request_id: str | None = None
    status_code: int | None = None
    cost_credits: float | None = None
    quota_remaining: float | None = None
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class ToolMetrics:
    """Aggregate metrics for a single MCP tool invocation."""

    latency_ms: float
    request_ids: list[str] = field(default_factory=list)
    cost_credits: float = 0.0
    quota_remaining: float | None = None
    upstream_calls: int = 0

    def merge(self, call: CallMetrics) -> None:
        self.upstream_calls += 1
        if call.request_id:
            self.request_ids.append(call.request_id)
        if call.cost_credits is not None:
            self.cost_credits += call.cost_credits
        if call.quota_remaining is not None:
            # Latest reading wins — quota is a running counter.
            self.quota_remaining = call.quota_remaining

    def to_response_block(self) -> dict[str, Any]:
        block: dict[str, Any] = {
            "latency_ms": round(self.latency_ms, 1),
            "upstream_calls": self.upstream_calls,
        }
        if self.request_ids:
            block["request_ids"] = self.request_ids
        if self.cost_credits:
            block["cost_credits"] = round(self.cost_credits, 4)
        if self.quota_remaining is not None:
            block["quota_remaining"] = self.quota_remaining
        return block


@contextmanager
def measure_tool():
    """Wrap a tool body. Yields a ToolMetrics that the body fills via merge()."""
    metrics = ToolMetrics(latency_ms=0.0)
    start = time.perf_counter()
    try:
        yield metrics
    finally:
        metrics.latency_ms = (time.perf_counter() - start) * 1000.0


def metrics_from_response_headers(headers: dict[str, str]) -> CallMetrics:
    """Parse standard observability fields out of Sarvam response headers.

    Sarvam responses surface ``x-request-id`` and (for some endpoints) credit
    accounting headers. This is best-effort — missing headers → ``None``.
    """
    request_id = headers.get("x-request-id") or headers.get("request-id")
    cost = _maybe_float(headers.get("x-credits-used"))
    remaining = _maybe_float(headers.get("x-credits-remaining"))
    return CallMetrics(
        request_id=request_id,
        cost_credits=cost,
        quota_remaining=remaining,
    )


def _maybe_float(raw: str | None) -> float | None:
    if raw is None:
        return None
    try:
        return float(raw)
    except (TypeError, ValueError):
        return None
