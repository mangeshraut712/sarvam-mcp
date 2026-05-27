"""In-memory store for OAuth state: client registrations, auth codes, tokens.

Auth codes are self-contained (encrypted blobs) so they work across
multiple server replicas without shared state. Client registrations
remain in-memory (short-lived, re-created on each OAuth flow).
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from dataclasses import dataclass, field


def _get_code_secret() -> bytes:
    """Derive a secret for signing auth codes.

    Uses OAUTH_CODE_SECRET env var if set, otherwise derives from
    DASHBOARD_JWT_PRIVATE_KEY_BASE64, or falls back to a per-process random.
    """
    if secret := os.environ.get("OAUTH_CODE_SECRET"):
        return secret.encode()
    if key_b64 := os.environ.get("DASHBOARD_JWT_PRIVATE_KEY_BASE64"):
        return hashlib.sha256(key_b64.encode()).digest()
    # Per-process fallback (won't survive restarts or work cross-pod
    # without one of the above env vars).
    return hashlib.sha256(b"sarvam-mcp-default-" + str(os.getpid()).encode()).digest()


_CODE_SECRET = _get_code_secret()


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


def _sign_code_payload(payload: dict) -> str:
    """Create a signed, base64url-encoded auth code containing the payload."""
    data = json.dumps(payload, separators=(",", ":")).encode()
    sig = hmac.new(_CODE_SECRET, data, hashlib.sha256).digest()[:16]
    token = base64.urlsafe_b64encode(data + sig).rstrip(b"=").decode()
    return token


def _verify_code_payload(code: str) -> dict | None:
    """Verify and decode a signed auth code. Returns None if invalid."""
    try:
        padding = 4 - len(code) % 4
        if padding < 4:
            code += "=" * padding
        raw = base64.urlsafe_b64decode(code)
        data, sig = raw[:-16], raw[-16:]
        expected = hmac.new(_CODE_SECRET, data, hashlib.sha256).digest()[:16]
        if not hmac.compare_digest(sig, expected):
            return None
        payload = json.loads(data)
        if time.time() - payload.get("iat", 0) > 600:
            return None
        return payload
    except Exception:
        return None


class OAuthStore:
    """OAuth store with stateless auth codes (work across pods)."""

    def __init__(self) -> None:
        self._clients: dict[str, RegisteredClient] = {}
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
        payload = {
            "cid": client_id,
            "ruri": redirect_uri,
            "key": api_key,
            "iat": int(time.time()),
        }
        if code_challenge:
            payload["cc"] = code_challenge
            payload["ccm"] = code_challenge_method or "S256"
        return _sign_code_payload(payload)

    def exchange_code(
        self, code: str, client_id: str, code_verifier: str | None = None
    ) -> AccessToken | None:
        payload = _verify_code_payload(code)
        if not payload:
            return None
        if payload.get("cid") != client_id:
            return None
        # Verify PKCE
        if cc := payload.get("cc"):
            if not code_verifier:
                return None
            digest = hashlib.sha256(code_verifier.encode("ascii")).digest()
            expected = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
            if expected != cc:
                return None

        return AccessToken(
            token=payload["key"],
            api_key=payload["key"],
            client_id=client_id,
        )

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
        """Remove expired tokens."""
        now = time.time()
        self._tokens = {
            k: v
            for k, v in self._tokens.items()
            if now - v.created_at < v.expires_in
        }


# Singleton instance
oauth_store = OAuthStore()
