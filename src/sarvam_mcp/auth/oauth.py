"""OAuth provider stub — wired in v1.1 for hosted MCP at mcp.sarvam.ai.

Kept here so the Protocol has a second implementation in-tree from day 1
and so ``SarvamClient`` already accepts the ``scope`` parameter without
needing a refactor when v1.1 lands.
"""

from __future__ import annotations


class FlowAuthNotConfiguredError(RuntimeError):
    """Raised when an OAuth-scoped tool is called in v1 (local stdio) mode."""


class OAuthProvider:
    """Per-user OAuth token provider. Activated by hosted-MCP middleware in v1.1.

    In v1 this class is importable but not constructed at runtime — local
    stdio servers always use ``StaticKeyProvider``. The hosted transport in
    v1.1 will instantiate this per request and attach via ``set_auth(...)``.
    """

    def __init__(
        self,
        access_token: str,
        *,
        principal_id: str,
        refresh_token: str | None = None,
        expires_at: float | None = None,
    ) -> None:
        self._access_token = access_token
        self._refresh_token = refresh_token
        self._expires_at = expires_at
        self._principal_id = principal_id

    async def headers(self, *, scope: str | None = None) -> dict[str, str]:
        # Future: enforce scope-vs-token-scope checks here.
        return {"Authorization": f"Bearer {self._access_token}"}

    async def refresh(self) -> None:
        # Wired up in v1.1 alongside the token-exchange flow.
        raise FlowAuthNotConfiguredError(
            "OAuth refresh is not available in v1 (local stdio). "
            "Run sarvam-mcp via the hosted MCP at mcp.sarvam.ai (v1.1)."
        )

    @property
    def principal(self) -> str:
        return f"user:{self._principal_id}"
