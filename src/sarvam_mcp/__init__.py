"""Sarvam AI MCP server — first-class MCP tools for the full public Sarvam API surface."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("sarvam-mcp")
except PackageNotFoundError:
    __version__ = "0.0.0-dev"
