"""OAuth 2.1 endpoints for MCP client auth (RFC 9728 + dynamic registration).

All routes are mounted as custom_routes on the FastMCP app or as a
separate Starlette sub-application.
"""

from __future__ import annotations

import logging
import os
from urllib.parse import urlencode, urlparse, parse_qs

from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from starlette.routing import Route

from sarvam_mcp.oauth.store import oauth_store
from sarvam_mcp.oauth.templates import render_authorize_page

logger = logging.getLogger("sarvam_mcp.oauth")

ISSUER = os.environ.get("SARVAM_MCP_ISSUER", "https://mcp.sarvam.ai")
MCP_RESOURCE = os.environ.get("SARVAM_MCP_RESOURCE", "https://mcp.sarvam.ai/mcp")

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization, api-subscription-key, mcp-protocol-version, mcp-session-id",
}


def _cors_json(data: dict, status: int = 200) -> JSONResponse:
    return JSONResponse(data, status_code=status, headers=CORS_HEADERS)


def _cors_options() -> Response:
    return Response(status_code=204, headers=CORS_HEADERS)


# ─── /.well-known/oauth-protected-resource ────────────────────────────────────

async def well_known_protected_resource(request: Request) -> Response:
    if request.method == "OPTIONS":
        return _cors_options()
    return _cors_json({
        "resource": MCP_RESOURCE,
        "authorization_servers": [ISSUER],
        "scopes_supported": ["mcp:tools"],
        "bearer_methods_supported": ["header"],
    })


# ─── /.well-known/oauth-authorization-server ──────────────────────────────────

async def well_known_authorization_server(request: Request) -> Response:
    if request.method == "OPTIONS":
        return _cors_options()
    return _cors_json({
        "issuer": ISSUER,
        "authorization_endpoint": f"{ISSUER}/oauth/authorize",
        "token_endpoint": f"{ISSUER}/oauth/token",
        "registration_endpoint": f"{ISSUER}/oauth/register",
        "response_types_supported": ["code"],
        "grant_types_supported": ["authorization_code"],
        "code_challenge_methods_supported": ["S256"],
        "token_endpoint_auth_methods_supported": ["none"],
        "scopes_supported": ["mcp:tools"],
    })


# ─── POST /oauth/register (Dynamic Client Registration — RFC 7591) ────────────

async def oauth_register(request: Request) -> Response:
    if request.method == "OPTIONS":
        return _cors_options()

    try:
        body = await request.json()
    except Exception:
        return _cors_json({"error": "invalid_request"}, 400)

    client_name = body.get("client_name", "MCP Client")
    redirect_uris = body.get("redirect_uris", [])

    client = oauth_store.register_client(
        client_name=client_name,
        redirect_uris=redirect_uris,
    )
    logger.info("Registered client %s (%s)", client.client_id, client_name)

    return _cors_json({
        "client_id": client.client_id,
        "client_name": client_name,
        "redirect_uris": redirect_uris,
        "grant_types": ["authorization_code"],
        "response_types": ["code"],
        "token_endpoint_auth_method": "none",
    }, 201)


# ─── GET/POST /oauth/authorize ────────────────────────────────────────────────

async def oauth_authorize(request: Request) -> Response:
    if request.method == "OPTIONS":
        return _cors_options()

    if request.method == "GET":
        params = request.query_params
        client_id = params.get("client_id", "")
        redirect_uri = params.get("redirect_uri", "")
        state = params.get("state", "")
        code_challenge = params.get("code_challenge", "")
        code_challenge_method = params.get("code_challenge_method", "")

        client = oauth_store.get_client(client_id)
        client_name = client.client_name if client else "Unknown Client"

        html = render_authorize_page(
            client_id=client_id,
            client_name=client_name,
            redirect_uri=redirect_uri,
            state=state,
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method,
        )
        return HTMLResponse(html)

    # POST — form submission
    form = await request.form()
    client_id = str(form.get("client_id", ""))
    redirect_uri = str(form.get("redirect_uri", ""))
    state = str(form.get("state", ""))
    api_key = str(form.get("api_key", "")).strip()
    code_challenge = str(form.get("code_challenge", ""))
    code_challenge_method = str(form.get("code_challenge_method", ""))

    if not api_key:
        client = oauth_store.get_client(client_id)
        client_name = client.client_name if client else "Unknown Client"
        html = render_authorize_page(
            client_id=client_id,
            client_name=client_name,
            redirect_uri=redirect_uri,
            state=state,
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method,
            error_html='<div class="error">Please enter your API key.</div>',
        )
        return HTMLResponse(html, status_code=400)

    code = oauth_store.create_code(
        client_id=client_id,
        redirect_uri=redirect_uri,
        api_key=api_key,
        code_challenge=code_challenge or None,
        code_challenge_method=code_challenge_method or None,
    )

    # Redirect back to client with the code
    separator = "&" if "?" in redirect_uri else "?"
    location = f"{redirect_uri}{separator}{urlencode({'code': code, 'state': state})}"
    return RedirectResponse(location, status_code=302)


# ─── POST /oauth/token ────────────────────────────────────────────────────────

async def oauth_token(request: Request) -> Response:
    if request.method == "OPTIONS":
        return _cors_options()

    try:
        body = await request.form()
    except Exception:
        try:
            body = await request.json()
        except Exception:
            return _cors_json({"error": "invalid_request"}, 400)

    grant_type = body.get("grant_type", "")
    if grant_type != "authorization_code":
        return _cors_json({"error": "unsupported_grant_type"}, 400)

    code = str(body.get("code", ""))
    client_id = str(body.get("client_id", ""))
    code_verifier = body.get("code_verifier")
    if code_verifier:
        code_verifier = str(code_verifier)

    token = oauth_store.exchange_code(code, client_id, code_verifier)
    if not token:
        return _cors_json({"error": "invalid_grant"}, 400)

    return _cors_json({
        "access_token": token.token,
        "token_type": "Bearer",
        "expires_in": token.expires_in,
        "scope": "mcp:tools",
    })


# ─── Starlette routes ─────────────────────────────────────────────────────────

oauth_routes = [
    Route(
        "/.well-known/oauth-protected-resource",
        well_known_protected_resource,
        methods=["GET", "OPTIONS"],
    ),
    Route(
        "/.well-known/oauth-protected-resource/{path:path}",
        well_known_protected_resource,
        methods=["GET", "OPTIONS"],
    ),
    Route(
        "/.well-known/oauth-authorization-server",
        well_known_authorization_server,
        methods=["GET", "OPTIONS"],
    ),
    Route("/oauth/register", oauth_register, methods=["POST", "OPTIONS"]),
    Route("/oauth/authorize", oauth_authorize, methods=["GET", "POST", "OPTIONS"]),
    Route("/oauth/token", oauth_token, methods=["POST", "OPTIONS"]),
]
