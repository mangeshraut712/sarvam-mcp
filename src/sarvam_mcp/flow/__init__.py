"""Sarvam Flow tools — v1.1 preview.

Flow lets users save and trigger Sarvam workflows (analogous to ElevenLabs
Conversational AI). Triggering requires user-scoped OAuth, not just an API
key, so these tools are gated behind ``SARVAM_MCP_ENABLE_FLOW=1`` until
v1.1 ships the hosted MCP at ``mcp.sarvam.ai`` with proper auth.

To preview locally (won't actually work without OAuth):
    SARVAM_MCP_ENABLE_FLOW=1 sarvam-mcp
"""

from __future__ import annotations

from fastmcp import FastMCP

from sarvam_mcp.config import Config


def register(mcp: FastMCP, config: Config) -> None:
    """Register Flow tools only if the feature flag is on. Hidden by default."""
    if not config.flow_enabled:
        return

    # Lazy import: pulls in the stub module only when actually wanted.
    from sarvam_mcp.flow import tools as flow_tools

    flow_tools.register(mcp)
