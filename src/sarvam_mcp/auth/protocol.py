"""AuthProvider Protocol — the contract every auth strategy implements."""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class AuthProvider(Protocol):
    """Anything that can produce auth headers for a Sarvam API request.

    Implementations:
    - ``StaticKeyProvider`` — wraps a static API key (v1, local stdio).
    - ``OAuthProvider`` — wraps a user-scoped OAuth token (v1.1, hosted MCP).

    Tools never touch headers directly. They go through ``SarvamClient``,
    which calls ``auth.headers()`` per request. The ``scope`` parameter is a
    forward-looking hook for OAuth scoping; ``StaticKeyProvider`` ignores it.
    """

    async def headers(self, *, scope: str | None = None) -> dict[str, str]:
        """Return the auth headers to merge into the outbound request."""
        ...

    async def refresh(self) -> None:
        """Refresh the underlying credential. No-op for static keys."""
        ...

    @property
    def principal(self) -> str:
        """Stable identifier for logs/observability — never the secret itself."""
        ...
