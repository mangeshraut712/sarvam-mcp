"""Just-in-time auth gate for tool calls.

Every runtime tool calls ``await ensure_auth(ctx)`` (via ``ready_ctx``)
before hitting the Sarvam API.  If no auth provider is set yet, this
module checks for a stored OAuth token in ``~/.sarvam/credentials``.

If no token is found:
  - **HTTP mode**: raises ``ToolError`` (the middleware should have already
    handled auth via the ``Authorization: Bearer`` header).
  - **stdio mode**: raises ``ToolError`` directing the user to call the
    ``sarvam_tools_auth_login`` tool.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

from fastmcp import Context
from fastmcp.exceptions import ToolError

from sarvam_mcp.auth.api_key import StaticKeyProvider
from sarvam_mcp.auth.context import _current, set_auth

logger = logging.getLogger("sarvam_mcp.auth")

DASHBOARD_LOGIN_URL = "https://dashboard.sarvam.ai/login"

_CREDENTIALS_TILDE = "~/.sarvam/credentials"
CREDENTIALS_PATH = Path(_CREDENTIALS_TILDE).expanduser()


def _is_http_mode() -> bool:
    """Detect if we're running in hosted HTTP mode."""
    return os.environ.get("SARVAM_MCP_TRANSPORT", "").lower() in (
        "http",
        "streamable-http",
    )


async def ensure_auth(ctx: Context) -> None:  # noqa: ARG001
    """Guarantee that ``current_auth()`` will succeed for this call.

    Checks stored credentials first.  If nothing is available, raises a
    ``ToolError`` directing the user to the auth tool or OAuth flow.
    """
    if _current.get() is not None:
        return

    refreshed = _try_stored_token()
    if refreshed:
        set_auth(StaticKeyProvider(refreshed))
        return

    if _is_http_mode():
        raise ToolError(
            "Authentication required. Include your token in the "
            "`Authorization: Bearer <token>` header. "
            f"Log in at {DASHBOARD_LOGIN_URL}"
        )

    raise ToolError(
        "Not authenticated. Please call the `sarvam_tools_auth_login` tool "
        "to log in via OAuth, then retry this tool."
    )


def _try_stored_token() -> str | None:
    """Read ``~/.sarvam/credentials`` for a stored OAuth token."""
    if not CREDENTIALS_PATH.exists():
        return None
    for raw in CREDENTIALS_PATH.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        if key.strip() == "token":
            return value.strip().strip('"').strip("'")
    return None
