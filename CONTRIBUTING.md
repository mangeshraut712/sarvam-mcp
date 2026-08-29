# Contributing

Thanks for helping. This repo is a public MIT fork: the Python MCP server comes from [Sarvam AI](https://github.com/sarvamai/sarvam-mcp); Vaani (`web/`) is the WebMCP surface. See [NOTICE](NOTICE) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- Node.js 20+ if you touch `web/`
- A Sarvam API key from [dashboard.sarvam.ai/key-management](https://dashboard.sarvam.ai/key-management) for live API calls (unit tests do not need one)

## Setup

```bash
git clone https://github.com/mangeshraut712/sarvam-mcp.git
cd sarvam-mcp
uv venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
cd web && npm ci && cd ..
```

Optional live key:

```bash
mkdir -p ~/.sarvam
echo "api_key = sk_..." > ~/.sarvam/credentials
# or: export SARVAM_API_KEY=sk_...
```

## Tests (required before a PR)

```bash
pytest -q
ruff check .
ruff format --check .
cd web && npx tsc --noEmit
```

## Project layout

```
src/sarvam_mcp/     MCP server (tools, HTTP client, playground CLI)
tests/              pytest
web/                Vaani Next.js app + WebMCP registerTool
SUBMISSION.md       WebMCP Challenge Devpost notes
```

## Adding an MCP tool

1. New module in `src/sarvam_mcp/tools/` (or `workflows/` for composites).
2. Export `register(mcp: FastMCP)`.
3. Start API tools with `sc = await ready_ctx(ctx)` and return `observability`.
4. Add tests under `tests/`.

Do **not** dump every MCP operation onto `document.modelContext`. WebMCP tools live in `web/components/VaaniWorkspace.tsx` and must update the same UI state a human sees. Use current `registerTool(..., { signal })` — not obsolete `provideContext` / `unregisterTool`.

## Local run

```bash
mcp dev src/sarvam_mcp/server.py          # MCP Inspector
cd web && npm run dev -- --port 3000      # Vaani at /vaani
```

## Pull requests

1. Fork (or branch) from `main`.
2. One logical change per PR; `pytest -q` and Ruff must pass.
3. Do not commit API keys, `.env`, or `web/.next`.
4. Fill in the PR template.

Questions: open a GitHub Discussion or issue. Upstream MCP questions can also go to `support@sarvam.ai`.
