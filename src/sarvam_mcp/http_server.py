"""Simple landing page for mcp.sarvam.ai.

Shows installation instructions for the local MCP server.
No MCP protocol serving — this is informational only.

Usage:
    sarvam-mcp-http                     # starts on 0.0.0.0:8000
    PORT=9000 sarvam-mcp-http           # custom port
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

from starlette.applications import Starlette
from starlette.responses import FileResponse, HTMLResponse, JSONResponse
from starlette.routing import Route

logger = logging.getLogger("sarvam_mcp.http")

_STATIC_DIR = Path(__file__).parent / "static"

_LANDING_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Sarvam MCP — Install</title>
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
      padding: 24px;
    }
    .card {
      width: 100%;
      max-width: 640px;
      display: flex;
      flex-direction: column;
      gap: 16px;
      border-radius: 20px;
      padding: 24px;
      border: 1px solid #f0f0f0;
      background: #fff;
    }
    .logo { height: 32px; margin: 0 auto 4px; }
    h1 { font-size: 20px; text-align: center; font-weight: 600; }
    h2 { font-size: 14px; font-weight: 600; color: #333; margin-top: 8px; }
    p, li {
      color: #555;
      font-size: 13px;
      line-height: 1.6;
    }
    ol { padding-left: 20px; }
    ol li { margin-bottom: 8px; }
    a { color: #2563eb; text-decoration: none; }
    a:hover { text-decoration: underline; }
    .cmd {
      display: flex;
      align-items: center;
      gap: 8px;
      border-radius: 12px;
      padding: 12px 16px;
      border: 1px solid #e5e5e5;
      background: #fafafa;
      cursor: pointer;
      transition: border-color 0.15s;
    }
    .cmd:hover { border-color: #ccc; }
    .cmd code {
      flex: 1;
      font-family: ui-monospace, "JetBrains Mono", "Fira Code", Menlo, monospace;
      font-size: 12px;
      color: #141414;
      user-select: all;
      white-space: pre-wrap;
      word-break: break-all;
      text-align: left;
    }
    .cmd .copy-icon {
      flex-shrink: 0;
      width: 16px;
      height: 16px;
      color: #999;
      cursor: pointer;
      transition: color 0.15s ease;
    }
    .cmd:hover .copy-icon { color: #141414; }
    .section { margin-top: 4px; }
    .note {
      font-size: 12px;
      color: #888;
      margin-top: 4px;
    }
  </style>
  <script>
    function copyText(id) {
      const el = document.getElementById(id);
      navigator.clipboard.writeText(el.textContent);
    }
  </script>
</head>
<body>
  <div class="card">
    <img src="/static/sarvam-logo.png" alt="Sarvam" class="logo">
    <h1>Sarvam MCP Server</h1>
    <p style="text-align:center;color:#666;">Use Sarvam AI APIs (STT, TTS, Translate, LLM, Vision) from any MCP client.</p>

    <div class="section">
      <h2>1. Get your API key</h2>
      <p>Sign up or log in at <a href="https://dashboard.sarvam.ai/key-management" target="_blank">dashboard.sarvam.ai/key-management</a> and copy your API key.</p>
    </div>

    <div class="section">
      <h2>2. Add to your MCP client</h2>
      <p>Paste this JSON into your MCP config (Cursor, Claude Desktop, Windsurf, etc.):</p>
    </div>

    <div class="cmd" onclick="copyText('json-config')">
      <code id="json-config">{
  "mcpServers": {
    "sarvam": {
      "command": "uvx",
      "args": ["sarvam-mcp"],
      "env": {
        "SARVAM_API_KEY": "your_api_key_here"
      }
    }
  }
}</code>
      <svg class="copy-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><rect x="9" y="9" width="13" height="13" rx="2" ry="2" stroke-width="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" stroke-width="2"/></svg>
    </div>

    <p class="note">Replace <code>your_api_key_here</code> with your actual API key from the dashboard.</p>

    <div class="section">
      <h2>Config file locations</h2>
      <ol>
        <li><strong>Cursor</strong> — <code>~/.cursor/mcp.json</code></li>
        <li><strong>Claude Desktop</strong> — <code>~/Library/Application Support/Claude/claude_desktop_config.json</code> (macOS)</li>
        <li><strong>Claude Code</strong> — <code>claude mcp add sarvam -- uvx sarvam-mcp</code></li>
      </ol>
    </div>

    <div class="section">
      <h2>That's it!</h2>
      <p>Once configured, your MCP client will have access to all Sarvam tools — transcription, speech synthesis, translation, transliteration, language detection, LLM, and document intelligence.</p>
    </div>
  </div>
</body>
</html>
"""


async def landing(request):  # noqa: ARG001
    return HTMLResponse(_LANDING_HTML)


async def static_files(request):
    file_path = _STATIC_DIR / request.path_params["path"]
    if file_path.is_file() and _STATIC_DIR in file_path.resolve().parents:
        return FileResponse(file_path)
    return JSONResponse({"error": "not found"}, status_code=404)


async def health_check(request):  # noqa: ARG001
    return JSONResponse({"status": "ok", "service": "sarvam-mcp"})


app = Starlette(
    routes=[
        Route("/", landing),
        Route("/health", health_check),
        Route("/ready", health_check),
        Route("/static/{path:path}", static_files),
    ],
)


def main_http() -> None:
    """Console entry point for the landing page server."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s — %(message)s",
        stream=sys.stderr,
    )

    import uvicorn

    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8000"))

    logger.info("Starting sarvam-mcp landing page on %s:%d", host, port)
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    main_http()
