"""Authentication tool — OAuth login flow for MCP clients.

Provides an explicit ``sarvam_tools_auth_login`` tool so clients that don't
support MCP OAuth discovery (e.g. Claude Code) can trigger the login flow
manually.  The tool runs a standard OAuth 2.1 authorization-code flow with
PKCE against the hosted Sarvam MCP OAuth server, catching the redirect on a
temporary localhost HTTP server.
"""

from __future__ import annotations

import asyncio
import base64
import hashlib
import logging
import os
import secrets
import webbrowser
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse

import httpx
from fastmcp import Context, FastMCP
from fastmcp.exceptions import ToolError

from sarvam_mcp.auth.api_key import StaticKeyProvider
from sarvam_mcp.auth.context import _current, set_auth

logger = logging.getLogger("sarvam_mcp.auth.tool")

ISSUER = os.environ.get("SARVAM_MCP_ISSUER", "https://mcp.sarvam.ai")
CREDENTIALS_PATH = Path("~/.sarvam/credentials").expanduser()
_CREDENTIALS_TILDE = "~/.sarvam/credentials"

_CALLBACK_TIMEOUT = 120  # seconds to wait for the browser redirect

_SUCCESS_HTML = (
    b"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nConnection: close\r\n\r\n"
    b"<html><body style='font-family:system-ui;display:flex;align-items:center;"
    b"justify-content:center;min-height:100vh;margin:0;background:#f5f5f5'>"
    b"<div style='text-align:center'>"
    b"<h2>Authenticated!</h2>"
    b"<p>You can close this tab and return to your IDE.</p>"
    b"</div></body></html>"
)
_ERROR_HTML = (
    b"HTTP/1.1 400 Bad Request\r\nContent-Type: text/html\r\nConnection: close\r\n\r\n"
    b"<html><body style='font-family:system-ui;display:flex;align-items:center;"
    b"justify-content:center;min-height:100vh;margin:0;background:#f5f5f5'>"
    b"<div style='text-align:center'>"
    b"<h2>Authentication failed</h2>"
    b"<p>Please try again from your IDE.</p>"
    b"</div></body></html>"
)


def register(mcp: FastMCP) -> None:
    """Register auth tools on the FastMCP server."""

    @mcp.tool()
    async def sarvam_tools_auth_login(ctx: Context) -> dict[str, Any]:
        """Log in to Sarvam via OAuth. Call this if you get an authentication
        error, or when connecting for the first time.

        Opens your browser to log in to your Sarvam account. Once
        authenticated, the token is saved locally and all subsequent tool
        calls work automatically.
        """
        if _current.get() is not None:
            provider = _current.get()
            return {
                "status": "authenticated",
                "principal": provider.principal,
                "message": "Already logged in.",
            }

        token = _try_stored_token()
        if token:
            set_auth(StaticKeyProvider(token))
            return {
                "status": "authenticated",
                "message": "Using stored credentials.",
            }

        if _is_http_mode():
            raise ToolError(
                "In hosted mode, authentication is handled automatically via "
                "OAuth. Your MCP client should handle the 401 response. "
                "If you're seeing this, your client may not support OAuth "
                "discovery."
            )

        try:
            jwt_token = await _run_oauth_flow(ctx)
        except Exception as exc:
            logger.error("OAuth flow failed: %r", exc)
            raise ToolError(
                f"OAuth login failed: {exc}\n\n"
                f"You can also log in manually at:\n  {ISSUER}/oauth/authorize"
            ) from exc

        set_auth(StaticKeyProvider(jwt_token))
        _persist_token(jwt_token)

        await ctx.info(
            f"Successfully logged in. Token saved to {_CREDENTIALS_TILDE} — "
            "future calls will use it automatically."
        )
        return {
            "status": "authenticated",
            "message": "Successfully logged in via OAuth.",
        }

    @mcp.tool()
    async def sarvam_tools_auth_status(
        ctx: Context,  # noqa: ARG001
    ) -> dict[str, Any]:
        """Check your current Sarvam authentication status."""
        provider = _current.get()
        if provider is not None:
            return {
                "status": "authenticated",
                "principal": provider.principal,
            }

        token = _try_stored_token()
        if token:
            return {
                "status": "token_found",
                "message": (
                    "Stored token found but not yet loaded. "
                    "It will be used on the next tool call."
                ),
            }

        return {
            "status": "not_authenticated",
            "message": "Not logged in. Call sarvam_tools_auth_login to authenticate.",
        }


# ── OAuth flow implementation ─────────────────────────────────────────────────


async def _run_oauth_flow(ctx: Context) -> str:
    """Execute OAuth authorization-code flow with PKCE via localhost callback."""

    port = _find_free_port()
    redirect_uri = f"http://localhost:{port}/callback"

    code_verifier = secrets.token_urlsafe(64)
    digest = hashlib.sha256(code_verifier.encode("ascii")).digest()
    code_challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")

    async with httpx.AsyncClient(timeout=15.0) as http:
        reg_resp = await http.post(
            f"{ISSUER}/oauth/register",
            json={
                "client_name": "sarvam-mcp-cli",
                "redirect_uris": [redirect_uri],
            },
        )
        if reg_resp.status_code != 201:
            raise RuntimeError(
                f"Client registration failed: {reg_resp.status_code} "
                f"{reg_resp.text[:200]}"
            )
        client_id = reg_resp.json()["client_id"]

    state = secrets.token_urlsafe(32)
    authorize_url = (
        f"{ISSUER}/oauth/authorize?"
        + urlencode({
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
            "scope": "mcp:tools",
        })
    )

    opened = False
    try:
        opened = webbrowser.open(authorize_url)
    except Exception:
        pass

    if opened:
        await ctx.info(
            "Browser opened for login. Complete authentication in your browser."
        )
    else:
        await ctx.info(
            "Could not open browser automatically.\n"
            f"Open this URL to log in:\n  {authorize_url}"
        )

    auth_code = await _wait_for_callback(port, state)

    async with httpx.AsyncClient(timeout=15.0) as http:
        token_resp = await http.post(
            f"{ISSUER}/oauth/token",
            data={
                "grant_type": "authorization_code",
                "code": auth_code,
                "client_id": client_id,
                "redirect_uri": redirect_uri,
                "code_verifier": code_verifier,
            },
        )
        if token_resp.status_code != 200:
            raise RuntimeError(
                f"Token exchange failed: {token_resp.status_code} "
                f"{token_resp.text[:200]}"
            )
        return token_resp.json()["access_token"]


async def _wait_for_callback(port: int, expected_state: str) -> str:
    """Start a temporary HTTP server and wait for the OAuth redirect."""

    result: dict[str, str | None] = {"code": None, "error": None}

    async def handle_client(
        reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        try:
            data = await asyncio.wait_for(reader.read(4096), timeout=5)
            request_line = data.split(b"\r\n")[0].decode(errors="replace")

            if not request_line.startswith("GET /callback"):
                writer.write(b"HTTP/1.1 404 Not Found\r\nConnection: close\r\n\r\n")
                return

            path = request_line.split(" ", 2)[1]
            params = parse_qs(urlparse(path).query)

            error = params.get("error", [None])[0]
            state = params.get("state", [""])[0]
            code = params.get("code", [None])[0]

            if error:
                result["error"] = error
                writer.write(_ERROR_HTML)
            elif state != expected_state:
                result["error"] = "State mismatch"
                writer.write(_ERROR_HTML)
            elif code:
                result["code"] = code
                writer.write(_SUCCESS_HTML)
            else:
                result["error"] = "No authorization code received"
                writer.write(_ERROR_HTML)
        except Exception:
            writer.write(_ERROR_HTML)
        finally:
            await writer.drain()
            writer.close()

    server = await asyncio.start_server(handle_client, "127.0.0.1", port)

    try:
        deadline = asyncio.get_event_loop().time() + _CALLBACK_TIMEOUT
        while result["code"] is None and result["error"] is None:
            remaining = deadline - asyncio.get_event_loop().time()
            if remaining <= 0:
                raise TimeoutError(
                    f"OAuth callback not received within {_CALLBACK_TIMEOUT}s. "
                    "Please try again."
                )
            await asyncio.sleep(0.5)
    finally:
        server.close()
        await server.wait_closed()

    if result["error"]:
        raise RuntimeError(f"OAuth error: {result['error']}")

    return result["code"]  # type: ignore[return-value]


# ── Helpers ────────────────────────────────────────────────────────────────────


def _find_free_port() -> int:
    """Find a free TCP port on localhost."""
    import socket

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _is_http_mode() -> bool:
    return os.environ.get("SARVAM_MCP_TRANSPORT", "").lower() in (
        "http",
        "streamable-http",
    )


def _try_stored_token() -> str | None:
    """Check ~/.sarvam/credentials for a stored token."""
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


def _persist_token(token: str) -> None:
    """Save JWT to ~/.sarvam/credentials (preserves non-token settings)."""
    CREDENTIALS_PATH.parent.mkdir(parents=True, exist_ok=True)

    preserved: list[str] = []
    if CREDENTIALS_PATH.exists():
        for raw in CREDENTIALS_PATH.read_text().splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, _ = line.partition("=")
            if key.strip() not in ("token", "api_key"):
                preserved.append(raw)

    body = "# Sarvam credentials — written by sarvam-mcp\n"
    body += f"token = {token}\n"
    for line in preserved:
        body += f"{line}\n"

    tmp = CREDENTIALS_PATH.with_suffix(".tmp")
    tmp.write_text(body)
    os.chmod(tmp, 0o600)
    tmp.replace(CREDENTIALS_PATH)


# Re-exported for use by `sarvam-mcp login` CLI command.
run_oauth_flow_cli = _run_oauth_flow
persist_token = _persist_token
try_stored_token = _try_stored_token
