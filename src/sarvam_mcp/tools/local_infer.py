"""Runtime demo of the local supervisor (echo tokens, optional resume)."""

from __future__ import annotations

from typing import Any, Literal

from fastmcp import Context, FastMCP
from pydantic import Field

from sarvam_mcp.observability import measure_tool
from sarvam_mcp.runtime import SlotScheduler, Supervisor

Kind = Literal["interactive", "background"]


def register(mcp: FastMCP) -> None:
    @mcp.tool(
        name="sarvam_tools_local_infer",
        description=(
            "Runtime tool — local supervisor demo (echo tokenizer). "
            "Shows crash isolation and idempotent resume. "
            "Does not load weights and does not call Sarvam cloud. "
            "Put __CRASH__ in the prompt to simulate a worker death, then retry "
            "the same request_id with resume_from_seq from the error event."
        ),
    )
    async def sarvam_tools_local_infer(
        ctx: Context,
        prompt: str = Field(description="Whitespace-separated tokens. Use __CRASH__ to kill the worker."),
        request_id: str = Field(description="Idempotency key for this generation."),
        resume_from_seq: int = Field(default=0, ge=0),
        kind: Kind = Field(default="interactive"),
    ) -> dict[str, Any]:
        _ = ctx
        supervisor = Supervisor(scheduler=SlotScheduler(max_slots=2))
        events: list[dict[str, Any]] = []
        with measure_tool() as metrics:
            async for event in supervisor.stream(
                prompt,
                request_id=request_id,
                resume_from_seq=resume_from_seq,
                kind=kind,
            ):
                events.append(event)
        return {
            "events": events,
            "restarts": supervisor.restarts,
            "cached_tokens": supervisor.tokens_for(request_id),
            "observability": metrics.to_response_block(),
        }
