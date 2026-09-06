"""B8 — typed events for API, IPC, and SDK (token / error / done)."""

from __future__ import annotations

from typing import Any, Literal

EventType = Literal["token", "done", "error", "heartbeat"]


def stream_event(
    *,
    type: EventType,
    request_id: str,
    seq: int,
    text: str | None = None,
    error: str | None = None,
    recoverable: bool | None = None,
    finish_reason: str | None = None,
    code: str | None = None,
) -> dict[str, Any]:
    event: dict[str, Any] = {
        "type": type,
        "request_id": request_id,
        "generation_id": request_id,
        "seq": seq,
        "index": seq,
    }
    if text is not None:
        event["text"] = text
    if error is not None:
        event["error"] = error
    if recoverable is not None:
        event["recoverable"] = recoverable
    if finish_reason is not None:
        event["finish_reason"] = finish_reason
    if code is not None:
        event["code"] = code
    return event
