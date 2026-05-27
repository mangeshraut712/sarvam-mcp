"""Static API-key auth provider — v1 default."""

from __future__ import annotations


class StaticKeyProvider:
    """Wraps a static Sarvam API subscription key or a dashboard JWT.

    Sarvam's HTTP APIs authenticate via the ``api-subscription-key`` header
    for sk_* keys, or ``Authorization: Bearer`` for dashboard JWTs.
    """

    def __init__(self, api_key: str) -> None:
        if not api_key:
            raise ValueError("Sarvam API key is empty.")
        self._key = api_key

    async def headers(self, *, scope: str | None = None) -> dict[str, str]:
        if self._key.startswith("sk_"):
            return {"api-subscription-key": self._key}
        return {"Authorization": f"Bearer {self._key}"}

    async def refresh(self) -> None:
        return None

    @property
    def principal(self) -> str:
        suffix = self._key[-4:] if len(self._key) >= 4 else "****"
        if self._key.startswith("sk_"):
            return f"api-key:****{suffix}"
        return f"jwt:****{suffix}"
