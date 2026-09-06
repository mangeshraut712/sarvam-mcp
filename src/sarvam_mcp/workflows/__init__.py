"""Composite ``sarvam_tools_*`` workflow tools.

These chain multiple atomic Sarvam APIs into single MCP tools so common
end-to-end flows (voice loops, dubbing, repo localization, indexed recall)
fit in one prompt instead of five.

Each module exposes ``register(mcp)``. ``server.py`` registers them after
the atomic tools.
"""

from sarvam_mcp.workflows import dub, localize, recall, voice

__all__ = ["dub", "localize", "recall", "voice"]
