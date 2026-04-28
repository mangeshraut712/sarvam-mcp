"""``sarvam_code_*`` namespace — builder tools that help devs CREATE
Sarvam-using apps (vs ``sarvam_tools_*`` which INVOKE Sarvam at runtime).

Two families (registered separately so individual modules stay small):

- ``code.docs``   — 5 reference tools (search_docs, api_reference, languages,
                    speakers, pricing). Backed by a TTL-cached fetch of
                    ``docs.sarvam.ai/llms-full.txt`` plus hard-coded tables.
- ``code.snippets`` — tested code snippets + model recommendation + request
                      validation.
"""

from fastmcp import FastMCP


def register(mcp: FastMCP) -> None:
    """Register all sarvam_code_* tools onto the FastMCP server."""
    from sarvam_mcp.code import docs, snippets

    docs.register(mcp)
    snippets.register(mcp)
