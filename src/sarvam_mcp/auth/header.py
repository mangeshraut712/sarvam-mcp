"""HTTP header-based auth: extract API key from incoming request headers.

Used in hosted/HTTP mode where each request carries the client's own
Sarvam API key in the ``api-subscription-key`` or ``Authorization`` header.
Also supports OAuth Bearer tokens issued by the built-in OAuth server.
"""

from __future__ import annotations

import logging
import os

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from sarvam_mcp.auth.api_key import StaticKeyProvider
from sarvam_mcp.auth.context import set_auth

logger = logging.getLogger("sarvam_mcp.auth.header")

_HEADER_NAME = "api-subscription-key"
_AUTH_HEADER = "authorization"

_ISSUER = os.environ.get("SARVAM_MCP_ISSUER", "https://mcp.sarvam.ai")
_RESOURCE_METADATA_URL = f"{_ISSUER}/.well-known/oauth-protected-resource"


def _extract_api_key(request: Request) -> str | None:
    """Extract API key from request headers.

    Priority:
      1. api-subscription-key header (Sarvam convention)
      2. Authorization: Bearer <key> — could be a raw API key or an OAuth token
    """
    if key := request.headers.get(_HEADER_NAME):
        return key.strip()

    auth = request.headers.get(_AUTH_HEADER, "")
    if auth.lower().startswith("bearer "):
        token = auth[7:].strip()
        if token:
            return token

    return None


def _is_exempt(path: str) -> bool:
    """Check if a path is exempt from auth."""
    exempt_exact = {"/health", "/healthz", "/ready"}
    if path in exempt_exact:
        return True
    if path.startswith("/.well-known/"):
        return True
    if path.startswith("/oauth/"):
        return True
    return False


def _resolve_api_key(token: str) -> str | None:
    """Resolve a token to a usable credential for Sarvam API calls.

    Priority:
      1. Raw Sarvam API key (sk_ prefix) — use directly.
      2. JWT token — verify and return as-is (used as Bearer for api.sarvam.ai).
      3. Opaque OAuth token — look up in store (legacy fallback).
    """
    if token.startswith("sk_"):
        return token

    from sarvam_mcp.auth.jwt import is_jwt_token, verify_dashboard_jwt

    if is_jwt_token(token):
        claims = verify_dashboard_jwt(token)
        if claims:
            return token
        # JWT looks valid structurally but failed verification.
        return None

    from sarvam_mcp.oauth.store import oauth_store

    return oauth_store.lookup_token(token)


class APIKeyAuthMiddleware(BaseHTTPMiddleware):
    """Starlette middleware that sets per-request auth from HTTP headers.

    Rejects requests without a valid API key with a 401 response, except
    for health-check, well-known, and OAuth endpoints.

    On 401, returns a WWW-Authenticate header with resource_metadata URL
    so MCP clients can discover the OAuth authorization server.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        if _is_exempt(request.url.path):
            return await call_next(request)

        if request.method == "OPTIONS":
            return await call_next(request)

        raw_token = _extract_api_key(request)
        if not raw_token:
            return JSONResponse(
                status_code=401,
                content={
                    "error": "missing_api_key",
                    "message": (
                        "Authentication required. Use OAuth or provide an API key "
                        "in the `api-subscription-key` header. "
                        "Log in at https://dashboard.sarvam.ai/login"
                    ),
                },
                headers={
                    "WWW-Authenticate": f'Bearer resource_metadata="{_RESOURCE_METADATA_URL}"',
                },
            )

        api_key = _resolve_api_key(raw_token)
        if not api_key:
            return JSONResponse(
                status_code=401,
                content={
                    "error": "invalid_token",
                    "message": "The access token is invalid or expired.",
                },
                headers={
                    "WWW-Authenticate": (
                        f'Bearer error="invalid_token", '
                        f'error_description="The access token is invalid or expired", '
                        f'resource_metadata="{_RESOURCE_METADATA_URL}"'
                    ),
                },
            )

        set_auth(StaticKeyProvider(api_key))
        return await call_next(request)
