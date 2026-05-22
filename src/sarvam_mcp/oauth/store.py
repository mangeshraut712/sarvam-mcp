"""In-memory store for OAuth state: client registrations, auth codes, tokens."""

from __future__ import annotations

import hashlib
import secrets
import time
from dataclasses import dataclass, field


@dataclass
class RegisteredClient:
    client_id: str
    client_name: str | None = None
    redirect_uris: list[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)


@dataclass
class AuthCode:
    code: str
    client_id: str
    redirect_uri: str
    api_key: str
    code_challenge: str | None = None
    code_challenge_method: str | None = None
    created_at: float = field(default_factory=time.time)
    used: bool = False


@dataclass
class AccessToken:
    token: str
    api_key: str
    client_id: str
    created_at: float = field(default_factory=time.time)
    expires_in: int = 3600 * 24 * 30  # 30 days


class OAuthStore:
    """Simple in-memory OAuth store. Resets on server restart."""

    def __init__(self) -> None:
        self._clients: dict[str, RegisteredClient] = {}
        self._codes: dict[str, AuthCode] = {}
        self._tokens: dict[str, AccessToken] = {}

    def register_client(
        self,
        client_name: str | None = None,
        redirect_uris: list[str] | None = None,
    ) -> RegisteredClient:
        client_id = secrets.token_urlsafe(24)
        client = RegisteredClient(
            client_id=client_id,
            client_name=client_name,
            redirect_uris=redirect_uris or [],
        )
        self._clients[client_id] = client
        return client

    def get_client(self, client_id: str) -> RegisteredClient | None:
        return self._clients.get(client_id)

    def create_code(
        self,
        client_id: str,
        redirect_uri: str,
        api_key: str,
        code_challenge: str | None = None,
        code_challenge_method: str | None = None,
    ) -> str:
        code = secrets.token_urlsafe(32)
        self._codes[code] = AuthCode(
            code=code,
            client_id=client_id,
            redirect_uri=redirect_uri,
            api_key=api_key,
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method,
        )
        return code

    def exchange_code(
        self, code: str, client_id: str, code_verifier: str | None = None
    ) -> AccessToken | None:
        auth_code = self._codes.get(code)
        if not auth_code:
            return None
        if auth_code.used:
            return None
        if auth_code.client_id != client_id:
            return None
        # Codes expire after 10 minutes
        if time.time() - auth_code.created_at > 600:
            return None
        # Verify PKCE
        if auth_code.code_challenge and auth_code.code_challenge_method == "S256":
            if not code_verifier:
                return None
            digest = hashlib.sha256(code_verifier.encode("ascii")).digest()
            import base64

            expected = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
            if expected != auth_code.code_challenge:
                return None

        auth_code.used = True
        token_str = secrets.token_urlsafe(48)
        token = AccessToken(
            token=token_str,
            api_key=auth_code.api_key,
            client_id=client_id,
        )
        self._tokens[token_str] = token
        return token

    def lookup_token(self, token: str) -> str | None:
        """Return the API key associated with a token, or None."""
        access_token = self._tokens.get(token)
        if not access_token:
            return None
        if time.time() - access_token.created_at > access_token.expires_in:
            del self._tokens[token]
            return None
        return access_token.api_key

    def cleanup_expired(self) -> None:
        """Remove expired codes and tokens."""
        now = time.time()
        self._codes = {
            k: v for k, v in self._codes.items() if now - v.created_at < 600
        }
        self._tokens = {
            k: v
            for k, v in self._tokens.items()
            if now - v.created_at < v.expires_in
        }


# Singleton instance
oauth_store = OAuthStore()
