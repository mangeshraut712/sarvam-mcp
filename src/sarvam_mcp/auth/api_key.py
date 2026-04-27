"""Static API-key auth provider — v1 default."""

from __future__ import annotations


class StaticKeyProvider:
    """Wraps a static Sarvam API subscription key.

    Sarvam's HTTP APIs authenticate via the ``api-subscription-key`` header.
    """

    def __init__(self, api_key: str) -> None:
        if not api_key:
            raise ValueError("Sarvam API key is empty.")
        self._key = api_key

    async def headers(self, *, scope: str | None = None) -> dict[str, str]:
        # ``scope`` is ignored for static keys — they're not user-scoped.
        return {"api-subscription-key": self._key}

    async def refresh(self) -> None:
        # Static keys don't expire on a refresh schedule we control.
        return None

    @property
    def principal(self) -> str:
        # Last four chars only — enough to disambiguate keys in logs.
        suffix = self._key[-4:] if len(self._key) >= 4 else "****"
        return f"api-key:****{suffix}"
