"""ContextVar carrying the active AuthProvider for the current request.

Why a ContextVar:
- v1 (local stdio): set once at server startup; every request uses the same key.
- v1.1 (hosted MCP): set per-request by transport middleware to the user's
  OAuth provider, so tool code remains identical between modes.
"""

from __future__ import annotations

from contextvars import ContextVar
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sarvam_mcp.auth.protocol import AuthProvider

_current: ContextVar[AuthProvider | None] = ContextVar("sarvam_auth", default=None)


def set_auth(provider: AuthProvider) -> None:
    """Set the active provider for the current async context."""
    _current.set(provider)


def current_auth() -> AuthProvider:
    """Return the active provider, or raise if none has been set."""
    provider = _current.get()
    if provider is None:
        raise RuntimeError(
            "No AuthProvider configured. Set SARVAM_API_KEY or write "
            "~/.sarvam/credentials before starting the MCP server."
        )
    return provider
