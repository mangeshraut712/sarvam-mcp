"""Smoke test: every expected tool registers on the FastMCP server.

This is the minimum bar for "ships" — if a tool fails to import or
register, the server won't start and Claude Desktop will fail silently.
"""

from __future__ import annotations

import pytest

EXPECTED_TOOLS = {
    # Atomic — one tool per Sarvam endpoint
    "sarvam_stt_transcribe",
    "sarvam_stt_translate",
    "sarvam_stt_batch_submit",
    "sarvam_stt_batch_status",
    "sarvam_tts_speak",
    "sarvam_tts_stream",
    "sarvam_translate",
    "sarvam_transliterate",
    "sarvam_identify_language",
    "sarvam_text_analytics",
    "sarvam_llm_complete",
    "sarvam_vision_extract",
    # Composite /sv-* workflows
    "sv_voice",
    "sv_dub",
    "sv_localize",
    "sv_recall",
}


@pytest.fixture
def _api_key(monkeypatch):
    monkeypatch.setenv("SARVAM_API_KEY", "sk_test_smoke")


async def test_all_expected_tools_register(_api_key):
    from sarvam_mcp.server import build_server

    server = build_server()

    # FastMCP's tool registry: prefer the public API, fall back to internal.
    if hasattr(server, "list_tools"):
        tools = await server.list_tools()
        names = {t.name for t in tools}
    else:  # pragma: no cover — older FastMCP
        names = set(server._tool_manager._tools.keys())  # type: ignore[attr-defined]

    missing = EXPECTED_TOOLS - names
    assert not missing, f"Tools failed to register: {missing}"


async def test_flow_tools_hidden_unless_flagged(_api_key, monkeypatch):
    monkeypatch.delenv("SARVAM_MCP_ENABLE_FLOW", raising=False)
    from sarvam_mcp.server import build_server

    server = build_server()
    if hasattr(server, "list_tools"):
        names = {t.name for t in await server.list_tools()}
    else:  # pragma: no cover
        names = set(server._tool_manager._tools.keys())  # type: ignore[attr-defined]

    assert "sarvam_flow_list" not in names
    assert "sarvam_flow_run" not in names


async def test_flow_tools_appear_when_flagged(monkeypatch):
    monkeypatch.setenv("SARVAM_API_KEY", "sk_test_smoke")
    monkeypatch.setenv("SARVAM_MCP_ENABLE_FLOW", "1")
    # Re-import to pick up env change at config load time inside build_server.
    from sarvam_mcp.server import build_server

    server = build_server()
    if hasattr(server, "list_tools"):
        names = {t.name for t in await server.list_tools()}
    else:  # pragma: no cover
        names = set(server._tool_manager._tools.keys())  # type: ignore[attr-defined]

    assert "sarvam_flow_list" in names
    assert "sarvam_flow_run" in names
