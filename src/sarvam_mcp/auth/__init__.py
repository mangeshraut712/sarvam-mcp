"""Auth: OAuth JWT provider + HTTP header auth + JWT verification."""

from sarvam_mcp.auth.api_key import StaticKeyProvider
from sarvam_mcp.auth.context import current_auth, set_auth
from sarvam_mcp.auth.header import APIKeyAuthMiddleware
from sarvam_mcp.auth.jwt import is_jwt_token, verify_dashboard_jwt

__all__ = [
    "APIKeyAuthMiddleware",
    "StaticKeyProvider",
    "current_auth",
    "is_jwt_token",
    "set_auth",
    "verify_dashboard_jwt",
]
