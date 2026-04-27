# mcp.sarvam.ai — landing page

Static site that hosts:
- **Setup instructions** for every supported MCP client (Cursor, Claude Desktop, Claude Code, Windsurf, Zed)
- **`curl | bash` install script** that auto-detects clients and edits their config files
- **Tool catalog** + example prompts

## Files

```
web/
├── index.html       # the landing page itself
├── style.css        # dark theme inspired by linear / vercel
├── app.js           # tab switching + clipboard
└── README.md        # this file
```

## Local preview

```bash
cd web && python3 -m http.server 8080
# open http://localhost:8080
```

## Deploy

The site is purely static — drop it on any host:

| Host | How | URL |
|---|---|---|
| **Cloudflare Pages** | `wrangler pages deploy web/` | `mcp.sarvam.ai` (CNAME) |
| **Vercel** | `vercel --prod web/` | custom domain |
| **GitHub Pages** | enable Pages on the repo, set source to `web/` | `*.github.io` |
| **S3 + CloudFront** | `aws s3 sync web/ s3://...` | custom domain |

The `install.sh` lives at the **repo root** (`/install.sh`). On `mcp.sarvam.ai`, route requests to `/install` to serve that file with `Content-Type: text/x-shellscript`. With Cloudflare Pages, add a `_redirects`:

```
/install     /install.sh    200
```

(That file is shipped at `web/_redirects`.)

## Future (v1.1+)

When the hosted MCP ships, this same site grows:
- "Add to Cursor" button that does `cursor://settings/mcp/add?config=...` deep link
- Authenticated section: paste your Sarvam API key, get a personalized JSON snippet
- OAuth "Sign in with Sarvam" flow

For now, all paths funnel to the local-install story.
