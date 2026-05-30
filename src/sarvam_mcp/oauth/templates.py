"""HTML templates for the OAuth authorize page.

The primary flow redirects to Kratos login automatically; this template
is kept only as a minimal fallback showing a redirect message.
"""


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
    """Render a minimal authorize page (redirect fallback)."""
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
      text-align: center;
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
    .brand {
      display: flex;
      align-items: center;
      justify-content: center;
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
    .spinner {
      width: 32px;
      height: 32px;
      border: 3px solid #e5e5e5;
      border-top-color: #1a1a1a;
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
      margin: 1rem auto;
    }
    @keyframes spin { to { transform: rotate(360deg); } }
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
    <h1>Connecting to Sarvam</h1>
    <p class="subtitle">
      <strong>{{client_name}}</strong> is requesting access.
      Redirecting you to log in...
    </p>
    <div class="spinner"></div>
  </div>
</body>
</html>
"""
