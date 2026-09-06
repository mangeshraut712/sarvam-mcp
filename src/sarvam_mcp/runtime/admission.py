"""B9 / B12 — admit, queue, unload, or refuse before OOM."""

from __future__ import annotations

from typing import Literal

from sarvam_mcp.runtime.errors import InferenceClientError, ResourceExhaustedError

Decision = Literal["accept", "queue", "unload", "refuse"]


def admit(
    *,
    loaded_mb: int,
    incoming_mb: int,
    budget_mb: int,
    queue_depth: int,
    max_queue: int,
    can_unload_mb: int = 0,
    prompt_ok: bool = True,
) -> Decision:
    if not prompt_ok:
        raise InferenceClientError("malformed prompt")
    if loaded_mb + incoming_mb <= budget_mb:
        return "accept"
    if can_unload_mb and loaded_mb - can_unload_mb + incoming_mb <= budget_mb:
        return "unload"
    if queue_depth < max_queue:
        return "queue"
    raise ResourceExhaustedError(
        f"RAM {loaded_mb}+{incoming_mb}>{budget_mb} and queue {queue_depth}>={max_queue}"
    )
