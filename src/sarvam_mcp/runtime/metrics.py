"""B13 — percentiles (p50/p95/p99), not averages."""

from __future__ import annotations


def percentile(samples: list[float], p: float) -> float:
    if not samples:
        raise ValueError("samples is empty")
    if not 0 <= p <= 100:
        raise ValueError("p must be in [0, 100]")
    ordered = sorted(samples)
    if p == 100:
        return ordered[-1]
    idx = int(len(ordered) * p / 100)
    return ordered[min(idx, len(ordered) - 1)]
