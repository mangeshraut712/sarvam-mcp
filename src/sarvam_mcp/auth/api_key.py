"""Static token auth provider — wraps an OAuth JWT for outbound API calls."""

from __future__ import annotations


class StaticKeyProvider:
    """Wraps an OAuth JWT token obtained via the Sarvam login flow.

    All outbound requests to ``api.sarvam.ai`` use the
    ``Authorization: Bearer`` header.
    """

    def __init__(self, token: str) -> None:
        if not token:
            raise ValueError("Auth token is empty.")
        self._key = token

    async def headers(self, *, scope: str | None = None) -> dict[str, str]:  # noqa: ARG002
        return {"Authorization": f"Bearer {self._key}"}

    async def refresh(self) -> None:
        return None

    @property
    def principal(self) -> str:
        suffix = self._key[-4:] if len(self._key) >= 4 else "****"
        return f"jwt:****{suffix}"
