"""Hosted HTTP entry point for sarvam-mcp.

Runs the MCP server over Streamable HTTP transport (FastMCP's built-in ASGI app)
with per-request OAuth Bearer token authentication via HTTP headers.

Usage:
    sarvam-mcp-http                     # starts on 0.0.0.0:8000
    PORT=9000 sarvam-mcp-http           # custom port
    uvicorn sarvam_mcp.http_server:app  # production with uvicorn directly
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

os.environ.setdefault("SARVAM_MCP_TRANSPORT", "http")

from starlette.middleware import Middleware  # noqa: E402
from starlette.middleware.cors import CORSMiddleware  # noqa: E402
from starlette.responses import FileResponse, HTMLResponse, JSONResponse  # noqa: E402
from sarvam_mcp.auth.header import APIKeyAuthMiddleware  # noqa: E402
from sarvam_mcp.server import build_server  # noqa: E402

logger = logging.getLogger("sarvam_mcp.http")

_STATIC_DIR = Path(__file__).parent / "static"

_LANDING_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Sarvam MCP</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      font-family: "Matter", system-ui, sans-serif;
      background: #f5f5f5;
      color: #141414;
      -webkit-font-smoothing: antialiased;
    }
    .card {
      position: relative;
      width: 100%;
      max-width:600px;
      display: flex;
      flex-direction: column;
      gap: 12px;
      border-radius: 20px;
      padding: 16px;
      border: 1px solid #f0f0f0;
      background: #fff;
      transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
      text-align: center;
    }
    .logo { height: 32px; margin: 8px auto 4px; }
    p {
      color: #666;
      font-size: 14px;
      line-height: 1.5;
    }
    .cmd {
      display: flex;
      align-items: center;
      gap: 8px;
      border-radius: 20px;
      padding: 14px 16px;
      border: 1px solid #f0f0f0;
      background: #f5f5f5;
      transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
      cursor: pointer;
    }
    .cmd:hover { border-color: #e6e6e6; }
    .cmd code {
      flex: 1;
      font-family: ui-monospace, "JetBrains Mono", "Fira Code", Menlo, monospace;
      font-size: 13px;
      color: #141414;
      user-select: all;
      word-break: break-all;
      text-align: left;
    }
    .cmd .copy-icon {
      flex-shrink: 0;
      width: 18px;
      height: 18px;
      color: #999;
      cursor: pointer;
      transition: color 0.15s ease;
    }
    .cmd:hover .copy-icon { color: #141414; }
  </style>
</head>
<body>
  <div class="card">
    <img src="/static/sarvam-logo.png" alt="sarvam" class="logo">
    <p>Paste this into your agent/harness to get started.</p>
    <div class="cmd" onclick="navigator.clipboard.writeText(document.getElementById('u').textContent).then(()=>{var i=document.getElementById('ci');i.innerHTML='<path stroke-linecap=&quot;round&quot; stroke-linejoin=&quot;round&quot; stroke-width=&quot;2&quot; d=&quot;M5 13l4 4L19 7&quot;/>';i.style.color='#16a34a';setTimeout(()=>{i.innerHTML='<rect x=&quot;9&quot; y=&quot;9&quot; width=&quot;13&quot; height=&quot;13&quot; rx=&quot;2&quot; ry=&quot;2&quot; stroke-width=&quot;2&quot;/><path d=&quot;M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1&quot; stroke-width=&quot;2&quot;/>';i.style.color=''},1500)})">
      <code id="u">Install the Sarvam MCP server: https://mcp.sarvam.ai/mcp</code>
      <svg id="ci" class="copy-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><rect x="9" y="9" width="13" height="13" rx="2" ry="2" stroke-width="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" stroke-width="2"/></svg>
    </div>
  </div>
</body>
</html>
"""

_mcp = build_server()


@_mcp.custom_route("/", methods=["GET"])
async def landing(request):  # noqa: ARG001
    return HTMLResponse(_LANDING_HTML)


@_mcp.custom_route("/static/{path:path}", methods=["GET"])
async def static_files(request):
    file_path = _STATIC_DIR / request.path_params["path"]
    if file_path.is_file() and _STATIC_DIR in file_path.resolve().parents:
        return FileResponse(file_path)
    return JSONResponse({"error": "not found"}, status_code=404)


@_mcp.custom_route("/health", methods=["GET"])
async def health_check(request):  # noqa: ARG001
    return JSONResponse({
        "status": "ok",
        "service": "sarvam-mcp",
        "message": "MCP server is running"
    })


@_mcp.custom_route("/ready", methods=["GET"])
async def readiness_check(request):  # noqa: ARG001
    return JSONResponse({"status": "ready", "service": "sarvam-mcp"})


_middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
        allow_headers=[
            "mcp-protocol-version",
            "mcp-session-id",
            "Authorization",
            "Content-Type",
        ],
        expose_headers=["mcp-session-id"],
    ),
    Middleware(APIKeyAuthMiddleware),
]

from sarvam_mcp.oauth.server import (  # noqa: E402
    well_known_protected_resource,
    well_known_authorization_server,
    oauth_register,
    oauth_authorize,
    oauth_token,
)

_mcp.custom_route("/.well-known/oauth-protected-resource", methods=["GET", "OPTIONS"])(
    well_known_protected_resource
)
_mcp.custom_route("/.well-known/oauth-authorization-server", methods=["GET", "OPTIONS"])(
    well_known_authorization_server
)
_mcp.custom_route("/oauth/register", methods=["POST", "OPTIONS"])(oauth_register)
_mcp.custom_route("/oauth/authorize", methods=["GET", "OPTIONS"])(oauth_authorize)
_mcp.custom_route("/oauth/token", methods=["POST", "OPTIONS"])(oauth_token)

app = _mcp.http_app(path="/mcp", middleware=_middleware, stateless_http=True)


def main_http() -> None:
    """Console entry point for ``sarvam-mcp-http``."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s — %(message)s",
        stream=sys.stderr,
    )

    import uvicorn

    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8000"))

    logger.info("Starting sarvam-mcp HTTP server on %s:%d", host, port)
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    main_http()
