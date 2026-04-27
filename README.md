# sarvam-mcp

Official Sarvam AI MCP server. Exposes every public Sarvam API — STT, TTS, Translate, Transliterate, Language ID, Text Analytics, LLM (Sarvam-M), Vision OCR — as first-class MCP tools so any MCP-aware client (Claude Desktop, Claude Code, Cursor, Windsurf, Zed, OpenAI Agents) can call Sarvam with zero boilerplate.

## Quickstart

```bash
pip install sarvam-mcp        # or:  uvx sarvam-mcp
```

Drop this JSON into your MCP client (same shape works in Cursor / Claude Desktop / Claude Code / Windsurf / Zed):

```json
{
  "mcpServers": {
    "sarvam": {
      "command": "uvx",
      "args": ["sarvam-mcp"]
    }
  }
}
```

**No API key required up front.** The server starts with auth deferred and **prompts you for the key on the first tool call** via MCP elicitation (Cursor / Claude Desktop will show a popup). The key gets saved to `~/.sarvam/credentials` (mode `0600`) so subsequent runs don't ask.

If your MCP client doesn't support elicitation, or you'd rather set the key ahead of time, three options:

```bash
# A) Interactive terminal setup (recommended for headless / scripted installs)
sarvam-mcp init

# B) Env var in the client config
#    {"env": {"SARVAM_API_KEY": "sk_..."}}

# C) Hand-write the credentials file
mkdir -p ~/.sarvam && echo "api_key = sk_..." > ~/.sarvam/credentials
```

### Per-client paths

- **Claude Desktop** — `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Claude Code** — `claude mcp add sarvam -- uvx sarvam-mcp`
- **Cursor** — `~/.cursor/mcp.json`
- **Windsurf** — Cascade settings → MCP servers
- **Zed** — `settings.json` → `context_servers`

## Tools

All defaults below reflect the latest non-deprecated models live as of 2026-04-27.

| Tool | What it does | Default model | Other accepted |
|---|---|---|---|
| `sarvam_stt_transcribe` | Audio file → transcript | `saarika:v2.5` | — (no v3 yet) |
| `sarvam_stt_translate` | Audio → English text | `saaras:v3` | `saaras:v3-realtime`, `saaras:v2.5` |
| `sarvam_stt_batch_submit` | Long-audio job init (Azure SAS) | `saarika:v2.5` | — |
| `sarvam_stt_batch_status` | Long-audio job poll | — | — |
| `sarvam_tts_speak` | Text → audio file | `bulbul:v3` (speaker `priya`) | `bulbul:v3-beta`, `bulbul:v2` |
| `sarvam_tts_stream` | Text → streamed audio | `bulbul:v3` | `bulbul:v2` |
| `sarvam_translate` | Cross-language text translate | `mayura:v1` | `sarvam-translate:v1` (22 langs) |
| `sarvam_transliterate` | Script conversion | — | — |
| `sarvam_identify_language` | Language + script detect | — | — |
| `sarvam_text_analytics` | Typed Q&A over text | — | — |
| `sarvam_llm_complete` | Chat completions | `sarvam-m` | `sarvam-30b`, `sarvam-105b` |
| `sarvam_vision_extract` | Document/image OCR | Sarvam Vision (endpoint TBD) | — |

## Configuration

| Env var | Default | Description |
|---|---|---|
| `SARVAM_API_KEY` | — | Required. API key. Falls back to `~/.sarvam/credentials`. |
| `SARVAM_API_REGION` | `in` | Data residency region. |
| `SARVAM_API_BASE_URL` | `https://api.sarvam.ai` | Override for testing/staging. |
| `SARVAM_MCP_BASE_PATH` | `~/Desktop` | Where audio/document files land in `files` mode. |
| `SARVAM_AUDIO_OUTPUT_MODE` | `files` | `files` \| `resources` \| `both`. |
| `SARVAM_MCP_ENABLE_FLOW` | `0` | Internal flag — Flow tools (v1.1). |

`~/.sarvam/credentials` format:

```ini
api_key = sk_...
region = in
```

## Status

v1 — atomic tools only. Composite workflows (`/sv-voice`, `/sv-localize`, `/sv-recall`, `/sv-dub`) ship in v1.x. Hosted remote MCP at `mcp.sarvam.ai` ships in v1.1. Samvaad control plane in v2.

## Development

```bash
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"
pytest -q
mcp dev src/sarvam_mcp/server.py    # MCP Inspector
```
