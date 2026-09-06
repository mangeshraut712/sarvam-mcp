"""Typed token-stream events shared by API, IPC, and the client SDK.

Every layer must agree on these names so a resume after a worker crash
does not invent a second schema.
"""

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
) -> dict[str, Any]:
    event: dict[str, Any] = {
        "type": type,
        "request_id": request_id,
        "seq": seq,
    }
    if text is not None:
        event["text"] = text
    if error is not None:
        event["error"] = error
    return event
