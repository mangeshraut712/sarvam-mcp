"""Stateless JWT verification for dashboard_auth tokens (RS256).

Mirrors how exa-mcp-server verifies JWTs: no server-side session store,
just cryptographic verification per request. The public key is derived from
the same RSA private key used by the dashboard to sign tokens.

Env vars:
  DASHBOARD_JWT_PUBLIC_KEY_BASE64  — preferred; base64-encoded PEM public key.
  DASHBOARD_JWT_PRIVATE_KEY_BASE64 — fallback; derives the public key from the private key.

If neither is set, JWT verification is disabled (tokens pass through unverified
and are used as-is for Bearer auth to the Sarvam API).
"""

from __future__ import annotations

import base64
import logging
import os
from dataclasses import dataclass
from typing import Any

import jwt as pyjwt
from jwt.exceptions import InvalidTokenError

logger = logging.getLogger("sarvam_mcp.auth.jwt")

_cached_public_key: str | None = None


@dataclass
class JWTClaims:
    sub: str
    email: str
    name: str | None = None
    aud: list[str] | None = None
    exp: int | None = None
    iat: int | None = None


def _get_public_key() -> str | None:
    """Load or derive the RSA public key for JWT verification."""
    global _cached_public_key
    if _cached_public_key is not None:
        return _cached_public_key

    pub_b64 = os.environ.get("DASHBOARD_JWT_PUBLIC_KEY_BASE64")
    if pub_b64:
        _cached_public_key = base64.b64decode(pub_b64).decode("utf-8")
        return _cached_public_key

    priv_b64 = os.environ.get("DASHBOARD_JWT_PRIVATE_KEY_BASE64")
    if priv_b64:
        from cryptography.hazmat.primitives.serialization import (
            Encoding,
            PublicFormat,
            load_pem_private_key,
        )

        private_pem = base64.b64decode(priv_b64)
        private_key = load_pem_private_key(private_pem, password=None)
        public_key = private_key.public_key()
        _cached_public_key = public_key.public_bytes(
            Encoding.PEM, PublicFormat.SubjectPublicKeyInfo
        ).decode("utf-8")
        return _cached_public_key

    return None


def is_jwt_token(token: str) -> bool:
    """Check if a token looks like a JWT (3 base64url-encoded segments)."""
    parts = token.split(".")
    return len(parts) == 3 and all(len(p) > 0 for p in parts)


def verify_dashboard_jwt(token: str) -> JWTClaims | None:
    """Verify a dashboard_auth JWT and return claims, or None if invalid.

    If no public key is configured, returns claims without signature
    verification (trusting the token as-is for Bearer pass-through).
    """
    public_key = _get_public_key()

    try:
        if public_key:
            payload: dict[str, Any] = pyjwt.decode(
                token,
                public_key,
                algorithms=["RS256"],
                options={"verify_aud": False},
            )
        else:
            # No key configured — decode without verification.
            # Token will still be used as Bearer for the Sarvam API,
            # which does its own validation.
            logger.debug("No JWT public key configured; skipping signature verification")
            payload = pyjwt.decode(
                token,
                options={"verify_signature": False},
            )

        return JWTClaims(
            sub=payload.get("sub", ""),
            email=payload.get("email", ""),
            name=payload.get("name"),
            aud=payload.get("aud"),
            exp=payload.get("exp"),
            iat=payload.get("iat"),
        )
    except InvalidTokenError as exc:
        logger.warning("JWT verification failed: %s", exc)
        return None
