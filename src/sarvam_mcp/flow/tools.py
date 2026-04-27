"""Flow tool stubs. Real implementation ships with v1.1 + hosted MCP.

These exist so the auth abstraction has a concrete second consumer in tree —
that means we'll catch any leak of "API key only" assumptions at design time
rather than during the v1.1 cutover.
"""

from __future__ import annotations

from fastmcp import FastMCP


class FlowNotAvailableError(RuntimeError):
    """Raised when Flow tools are invoked without OAuth-backed auth."""


_NOT_AVAILABLE_MSG = (
    "Sarvam Flow tools require user-scoped OAuth, which is only available "
    "via the hosted MCP at mcp.sarvam.ai (v1.1). For v1 (local stdio), only "
    "API-key tools (STT, TTS, translate, etc.) are supported."
)


def register(mcp: FastMCP) -> None:
    @mcp.tool(
        name="sarvam_flow_list",
        description=(
            "[v1.1 preview] List the saved Sarvam Flows owned by the authenticated user. "
            "Requires hosted MCP (OAuth)."
        ),
    )
    async def sarvam_flow_list() -> dict:  # type: ignore[return-value]
        raise FlowNotAvailableError(_NOT_AVAILABLE_MSG)

    @mcp.tool(
        name="sarvam_flow_run",
        description=(
            "[v1.1 preview] Trigger a saved Sarvam Flow with the given inputs. "
            "Requires hosted MCP (OAuth)."
        ),
    )
    async def sarvam_flow_run(flow_id: str, inputs: dict) -> dict:  # type: ignore[return-value]
        raise FlowNotAvailableError(_NOT_AVAILABLE_MSG)
