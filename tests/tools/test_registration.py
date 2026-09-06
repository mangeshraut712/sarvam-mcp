"""Smoke test: every expected tool registers on the FastMCP server.

This is the minimum bar for "ships" — if a tool fails to import or
register, the server won't start and Claude Desktop will fail silently.
"""

from __future__ import annotations

EXPECTED_TOOLS = {
    "sarvam_tools_set_api_key",
    "sarvam_tools_upgrade",
    "sarvam_tools_stt_transcribe",
    "sarvam_tools_stt_translate",
    "sarvam_tools_stt_batch_submit",
    "sarvam_tools_stt_batch_status",
    "sarvam_tools_tts_speak",
    "sarvam_tools_tts_stream",
    "sarvam_tools_translate",
    "sarvam_tools_transliterate",
    "sarvam_tools_identify_language",
    "sarvam_tools_text_analytics",
    "sarvam_tools_llm_complete",
    "sarvam_tools_vision_extract",
    "sarvam_tools_vision_job_status",
    "sarvam_tools_pronunciation_list",
    "sarvam_tools_pronunciation_get",
    "sarvam_tools_pronunciation_create",
    "sarvam_tools_pronunciation_delete",
    "sarvam_tools_voice",
    "sarvam_tools_dub",
    "sarvam_tools_localize",
    "sarvam_tools_recall",
    "sarvam_code_api_reference",
    "sarvam_code_languages",
    "sarvam_code_speakers",
    "sarvam_code_pricing",
    "sarvam_code_snippet",
    "sarvam_code_recommend_model",
    "sarvam_code_validate_request",
}


async def test_all_expected_tools_register():
    from sarvam_mcp.server import build_server

    server = build_server()
    tools = await server.list_tools()
    names = {t.name for t in tools}

    missing = EXPECTED_TOOLS - names
    extra = names - EXPECTED_TOOLS
    assert not missing, f"Tools failed to register: {missing}"
    assert not extra, f"Unexpected tools registered: {extra}"
