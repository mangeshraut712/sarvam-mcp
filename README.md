# sarvam-mcp

Official Sarvam MCP server. Exposes every public Sarvam API — STT, TTS, Translate, Transliterate, Language ID, Text Analytics, LLM (`sarvam-105b`), Vision Document Intelligence, Pronunciation Dictionaries — as first-class MCP tools so any MCP-aware client (Claude Desktop, Claude Code, Cursor, Windsurf, Zed) can call Sarvam with zero boilerplate.

Cross-platform Python package: **macOS, Windows, and Linux** (Python 3.11+).

## Quickstart

### 1. Get your API key

Sign up or log in at **[dashboard.sarvam.ai/key-management](https://dashboard.sarvam.ai/key-management)** and copy your API key (`sk_...`).

### 2. Add to your MCP client

Paste this into your MCP config JSON:

```json
{
  "mcpServers": {
    "sarvam": {
      "command": "uvx",
      "args": ["sarvam-mcp"],
      "env": {
        "SARVAM_API_KEY": "sk_..."
      }
    }
  }
}
```

Replace `sk_...` with your actual API key.

If you've installed via `pip install sarvam-mcp`, you can use the console script directly:

```json
{
  "mcpServers": {
    "sarvam": {
      "command": "sarvam-mcp",
      "env": {
        "SARVAM_API_KEY": "sk_..."
      }
    }
  }
}
```

### 3. Config file locations

| Client | Config path |
|---|---|
| **Cursor** | `~/.cursor/mcp.json` (macOS/Linux) · `%USERPROFILE%\.cursor\mcp.json` (Windows) |
| **Claude Desktop** | `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) · `%APPDATA%\Claude\claude_desktop_config.json` (Windows) |
| **Claude Code** | `claude mcp add sarvam -- uvx sarvam-mcp` (then set `SARVAM_API_KEY` env var) |
| **Windsurf** | Cascade settings → MCP servers |
| **Zed** | `settings.json` → `context_servers` |

### Alternative: credentials file

Instead of setting `SARVAM_API_KEY` in the JSON config, you can store it in `~/.sarvam/credentials`:

```ini
api_key = sk_...
```

The server checks `SARVAM_API_KEY` env var first, then falls back to `~/.sarvam/credentials`.

## Install

```bash
# Option A: run directly (no install needed)
uvx sarvam-mcp

# Option B: install globally
pip install sarvam-mcp
```

## Tools

All defaults below reflect the latest non-deprecated models.

| Tool | What it does | Default model |
|---|---|---|
| `sarvam_stt_transcribe` | Audio file → transcript (5 modes) | `saaras:v3` |
| `sarvam_tts_speak` | Text → audio file | `bulbul:v3` |
| `sarvam_tts_stream` | Text → streamed audio | `bulbul:v3` |
| `sarvam_translate` | Cross-language text translate | `mayura:v1` |
| `sarvam_transliterate` | Script conversion | — |
| `sarvam_identify_language` | Language + script detect | — |
| `sarvam_text_analytics` | Typed Q&A over text | — |
| `sarvam_llm_complete` | Chat completions | `sarvam-105b` |
| `sarvam_vision_extract` | Document Intelligence | Sarvam Vision |
| `sarvam_vision_job_status` | Poll Document Intelligence job | — |
| `sarvam_pronunciation_list` | List pronunciation dictionaries | — |
| `sarvam_pronunciation_get` | Get a pronunciation dictionary | — |
| `sarvam_pronunciation_create` | Create a pronunciation dictionary | — |
| `sarvam_pronunciation_delete` | Delete a pronunciation dictionary | — |

## Configuration

| Env var | Default | Description |
|---|---|---|
| `SARVAM_API_KEY` | — | Required. API key from dashboard.sarvam.ai. |
| `SARVAM_API_BASE_URL` | `https://api.sarvam.ai` | Override for testing/staging. |
| `SARVAM_MCP_BASE_PATH` | `~/Desktop` | Where audio/document files land. |
| `SARVAM_AUDIO_OUTPUT_MODE` | `files` | `files` \| `resources` \| `both`. |

## Two namespaces

The server exposes tools across two namespaces:

- **`sarvam_tools_*`** — *runtime* tools. Call Sarvam APIs to do things (transcribe, speak, translate, etc.).
- **`sarvam_code_*`** — *builder* tools. Help you write code that uses Sarvam: docs, endpoint shapes, language lists, code snippets, starter projects.

## Voice Agent Playground

The `web/` Next.js app includes **Sarvam Voice Agent** at `/playground`. It makes the existing MCP primitives visible as a single loop:

microphone → STT → language ID → LLM (same language) → TTS → browser playback

No extra Sarvam HTTP client: the Next.js route shells out to `python -m sarvam_mcp.playground`, which reuses `workflows/_helpers.py`. Translation is not in the default chain; the LLM is instructed to answer in the user's language.

```bash
export SARVAM_API_KEY=sk_...
cd web && npm run dev   # http://localhost:3000/playground
```

Meetup demo: hold **Hold to Speak** and say *“या text चा सारांश करा आणि मला मराठीत वाचून दाखवा.”* Show the tool timeline, play the Marathi reply, then open Cursor with `uvx sarvam-mcp` from the config above — same STT / Lang ID / LLM / TTS tools.

## Web deploy

```bash
cd web
npm ci && npm run build
# Production image (healthcheck on :8000/health)
docker build -t sarvam-mcp-web .
docker run --rm -p 8000:8000 -e SARVAM_API_KEY=sk_... sarvam-mcp-web
```

Verify: `GET /health`, `GET /ready`, `GET /`, `GET /playground`, `GET /api/sarvam-status`.

## Development

```bash
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"
pytest -q
mcp dev src/sarvam_mcp/server.py
```
