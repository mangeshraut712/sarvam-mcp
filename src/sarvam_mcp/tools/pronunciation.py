"""Pronunciation Dictionary — CRUD for custom TTS pronunciation rules.

Pronunciation dictionaries let users define how specific words should be
pronounced in TTS output. All endpoints live under
``/text-to-speech/pronunciation-dictionary``.
"""

from __future__ import annotations

from typing import Any

from fastmcp import Context, FastMCP
from pydantic import Field

from sarvam_mcp.observability import measure_tool
from sarvam_mcp.tools._common import ready_ctx

PRONDICT_BASE = "/text-to-speech/pronunciation-dictionary"


def register(mcp: FastMCP) -> None:
    @mcp.tool(
        name="sarvam_tools_pronunciation_list",
        description=(
            "Runtime tool — calls Sarvam API now.\n\n"
            "List all pronunciation dictionary IDs owned by the authenticated user. "
            "Returns dictionary_count and a list of dictionary IDs."
        ),
    )
    async def sarvam_pronunciation_list(
        ctx: Context,
    ) -> dict[str, Any]:
        sc = await ready_ctx(ctx)
        with measure_tool() as metrics:
            payload, call = await sc.client.get_json(PRONDICT_BASE)
            metrics.merge(call)
        return {
            "dictionary_count": payload.get("dictionary_count", 0),
            "dictionaries": payload.get("dictionaries", []),
            "observability": metrics.to_response_block(),
        }

    @mcp.tool(
        name="sarvam_tools_pronunciation_get",
        description=(
            "Runtime tool — calls Sarvam API now.\n\n"
            "Retrieve a specific pronunciation dictionary by its ID. "
            "Returns the dictionary entries (word → pronunciation mappings)."
        ),
    )
    async def sarvam_pronunciation_get(
        ctx: Context,
        dictionary_id: str = Field(description="The pronunciation dictionary ID."),
    ) -> dict[str, Any]:
        sc = await ready_ctx(ctx)
        with measure_tool() as metrics:
            payload, call = await sc.client.get_json(
                f"{PRONDICT_BASE}/{dictionary_id}"
            )
            metrics.merge(call)
        return {
            "dictionary_id": dictionary_id,
            "raw": payload,
            "observability": metrics.to_response_block(),
        }

    @mcp.tool(
        name="sarvam_tools_pronunciation_create",
        description=(
            "Runtime tool — calls Sarvam API now.\n\n"
            "Create a new pronunciation dictionary with word → pronunciation "
            "mappings. These dictionaries can be referenced in TTS calls to "
            "control how specific words are spoken."
        ),
    )
    async def sarvam_pronunciation_create(
        ctx: Context,
        entries: dict[str, str] = Field(
            description=(
                "Word-to-pronunciation mappings: "
                "{'Sarvam': 'सर्वम', 'API': 'ए पी आई'}."
            ),
        ),
    ) -> dict[str, Any]:
        sc = await ready_ctx(ctx)
        with measure_tool() as metrics:
            payload, call = await sc.client.post_json(
                PRONDICT_BASE, json_body={"entries": entries}
            )
            metrics.merge(call)
        return {
            "raw": payload,
            "observability": metrics.to_response_block(),
        }

    @mcp.tool(
        name="sarvam_tools_pronunciation_delete",
        description=(
            "Runtime tool — calls Sarvam API now.\n\n"
            "Delete a pronunciation dictionary by its ID."
        ),
    )
    async def sarvam_pronunciation_delete(
        ctx: Context,
        dictionary_id: str = Field(description="The pronunciation dictionary ID to delete."),
    ) -> dict[str, Any]:
        sc = await ready_ctx(ctx)
        with measure_tool() as metrics:
            payload, call = await sc.client.post_json(
                f"{PRONDICT_BASE}/{dictionary_id}/delete", json_body={}
            )
            metrics.merge(call)
        return {
            "dictionary_id": dictionary_id,
            "deleted": True,
            "raw": payload,
            "observability": metrics.to_response_block(),
        }
