"""ContextVar carrying the active auth provider for the current request.

Set once at server startup (from stored credentials) or lazily via the
``sarvam_tools_auth_login`` tool / OAuth flow.
"""

from __future__ import annotations

from contextvars import ContextVar
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sarvam_mcp.auth.api_key import StaticKeyProvider

_current: ContextVar[StaticKeyProvider | None] = ContextVar("sarvam_auth", default=None)


def set_auth(provider: StaticKeyProvider) -> None:
    """Set the active provider for the current async context."""
    _current.set(provider)


def current_auth() -> StaticKeyProvider:
    """Return the active provider, or raise if none has been set."""
    provider = _current.get()
    if provider is None:
        raise RuntimeError(
            "Not authenticated. Run the `sarvam_tools_auth_login` tool or "
            "`sarvam-mcp login` to log in via OAuth. "
            "Visit https://dashboard.sarvam.ai/login for account access."
        )
    return provider
