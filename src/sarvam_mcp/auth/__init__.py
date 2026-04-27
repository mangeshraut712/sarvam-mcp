"""Auth providers. v1 ships StaticKeyProvider; v1.1 wires in OAuthProvider."""

from sarvam_mcp.auth.api_key import StaticKeyProvider
from sarvam_mcp.auth.context import current_auth, set_auth
from sarvam_mcp.auth.oauth import OAuthProvider
from sarvam_mcp.auth.protocol import AuthProvider

__all__ = [
    "AuthProvider",
    "StaticKeyProvider",
    "OAuthProvider",
    "current_auth",
    "set_auth",
]
