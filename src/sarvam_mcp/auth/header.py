"""HTTP header-based auth: extract Bearer token from incoming request headers.

Used in hosted/HTTP mode where each request carries the client's OAuth
JWT in the ``Authorization: Bearer`` header.
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

_ISSUER = os.environ.get("SARVAM_MCP_ISSUER", "https://mcp.sarvam.ai")
_RESOURCE_METADATA_URL = f"{_ISSUER}/.well-known/oauth-protected-resource"


def _extract_token(request: Request) -> str | None:
    """Extract Bearer token from the Authorization header."""
    auth = request.headers.get("authorization", "")
    if auth.lower().startswith("bearer "):
        token = auth[7:].strip()
        if token:
            return token
    return None


def _is_exempt(path: str) -> bool:
    """Check if a path is exempt from auth."""
    exempt_exact = {"/", "/health", "/healthz", "/ready"}
    if path in exempt_exact:
        return True
    if path.startswith("/.well-known/"):
        return True
    if path.startswith("/oauth/"):
        return True
    if path.startswith("/static/"):
        return True
    return False


def _resolve_token(token: str) -> str | None:
    """Verify a token and return it if valid.

    Accepts JWT tokens verified against the dashboard public key,
    or passes them through for Bearer auth to api.sarvam.ai (which
    does its own validation).
    """
    from sarvam_mcp.auth.jwt import is_jwt_token, verify_dashboard_jwt

    if is_jwt_token(token):
        claims = verify_dashboard_jwt(token)
        if claims:
            return token
        return None

    from sarvam_mcp.oauth.store import oauth_store

    return oauth_store.lookup_token(token)


class APIKeyAuthMiddleware(BaseHTTPMiddleware):
    """Starlette middleware that sets per-request auth from the Authorization header.

    Rejects requests without a valid Bearer token with a 401 response,
    except for health-check, well-known, and OAuth endpoints.

    On 401, returns a ``WWW-Authenticate`` header with ``resource_metadata``
    URL so MCP clients can discover the OAuth authorization server.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        if _is_exempt(request.url.path):
            return await call_next(request)

        if request.method == "OPTIONS":
            return await call_next(request)

        raw_token = _extract_token(request)
        if not raw_token:
            return JSONResponse(
                status_code=401,
                content={
                    "error": "missing_token",
                    "message": (
                        "Authentication required. Use OAuth to connect, or "
                        "include a Bearer token in the Authorization header. "
                        "Log in at https://dashboard.sarvam.ai/login"
                    ),
                },
                headers={
                    "WWW-Authenticate": (
                        f'Bearer resource_metadata="{_RESOURCE_METADATA_URL}"'
                    ),
                },
            )

        verified = _resolve_token(raw_token)
        if not verified:
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

        set_auth(StaticKeyProvider(verified))
        return await call_next(request)
