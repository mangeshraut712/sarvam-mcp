"""HTML templates for the OAuth authorize page."""


def render_authorize_page(
    *,
    client_id: str,
    client_name: str,
    redirect_uri: str,
    state: str,
    code_challenge: str,
    code_challenge_method: str,
    error_html: str = "",
) -> str:
    """Render the authorize page with safe substitution (avoids CSS brace issues)."""
    return _AUTHORIZE_TEMPLATE.replace(
        "{{error_html}}", error_html
    ).replace(
        "{{client_name}}", client_name
    ).replace(
        "{{client_id}}", client_id
    ).replace(
        "{{redirect_uri}}", redirect_uri
    ).replace(
        "{{state}}", state
    ).replace(
        "{{code_challenge}}", code_challenge
    ).replace(
        "{{code_challenge_method}}", code_challenge_method
    )


_AUTHORIZE_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Authorize — Sarvam MCP</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: #fafafa;
      color: #1a1a1a;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 1rem;
    }
    .card {
      background: #fff;
      border: 1px solid #e5e5e5;
      border-radius: 24px;
      padding: 3rem;
      max-width: 420px;
      width: 100%;
      box-shadow: 0 4px 24px rgba(0,0,0,0.06);
    }
    h1 {
      font-size: 1.25rem;
      font-weight: 500;
      line-height: 1.2;
      margin-bottom: 0.5rem;
    }
    .subtitle {
      color: #666;
      font-size: 0.9rem;
      line-height: 1.45;
      margin-bottom: 1.5rem;
    }
    label {
      display: block;
      font-size: 0.85rem;
      font-weight: 500;
      margin-bottom: 0.4rem;
      color: #444;
    }
    input[type="password"] {
      width: 100%;
      padding: 0.65rem 1rem;
      background: #fff;
      border: 1px solid #d4d4d4;
      border-radius: 9999px;
      color: #1a1a1a;
      font-size: 0.9rem;
      font-family: monospace;
      outline: none;
      transition: border-color 0.2s;
    }
    input[type="password"]:hover {
      border-color: #999;
    }
    input[type="password"]:focus {
      border-color: #1a1a1a;
    }
    .help {
      font-size: 0.8rem;
      color: #888;
      margin-top: 0.5rem;
    }
    .help a { color: #1a1a1a; text-decoration: underline; }
    .help a:hover { color: #000; }
    .actions {
      display: flex;
      justify-content: flex-end;
      margin-top: 1.5rem;
      gap: 0.75rem;
    }
    button {
      padding: 0.6rem 1.25rem;
      background: #1a1a1a;
      color: #fff;
      border: none;
      border-radius: 9999px;
      font-size: 0.875rem;
      font-weight: 400;
      cursor: pointer;
      transition: background 0.15s;
      line-height: 1;
    }
    button:hover { background: #333; }
    button:active { transform: scale(0.95); }
    .brand {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      margin-bottom: 1.5rem;
    }
    .brand svg { width: 24px; height: 24px; }
    .brand span { font-weight: 500; font-size: 0.9rem; }
    .error {
      background: #fef2f2;
      border: 1px solid #fecaca;
      color: #dc2626;
      padding: 0.6rem 0.8rem;
      border-radius: 12px;
      font-size: 0.85rem;
      margin-bottom: 1rem;
    }
  </style>
</head>
<body>
  <div class="card">
    <div class="brand">
      <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect width="24" height="24" rx="12" fill="#1a1a1a"/>
        <text x="7" y="17" font-family="sans-serif" font-size="12" font-weight="600" fill="white">S</text>
      </svg>
      <span>Sarvam MCP</span>
    </div>
    {{error_html}}
    <h1>Connect to Sarvam APIs</h1>
    <p class="subtitle">
      <strong>{{client_name}}</strong> needs your API key to make calls on your behalf.
    </p>
    <form method="POST">
      <input type="hidden" name="client_id" value="{{client_id}}" />
      <input type="hidden" name="redirect_uri" value="{{redirect_uri}}" />
      <input type="hidden" name="state" value="{{state}}" />
      <input type="hidden" name="code_challenge" value="{{code_challenge}}" />
      <input type="hidden" name="code_challenge_method" value="{{code_challenge_method}}" />
      <label for="api_key">API Key</label>
      <input type="password" id="api_key" name="api_key" placeholder="e.g., sk_live_..." required autofocus />
      <p class="help">
        Get yours at <a href="https://dashboard.sarvam.ai/key-management" target="_blank">dashboard.sarvam.ai/key-management</a>
      </p>
      <div class="actions">
        <button type="submit">Authorize</button>
      </div>
    </form>
  </div>
</body>
</html>
"""
