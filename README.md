# sarvam-mcp

Official Sarvam MCP server. Exposes every public Sarvam API — STT, TTS, Translate, Transliterate, Language ID, Text Analytics, LLM (Sarvam-M), Vision OCR — as first-class MCP tools so any MCP-aware client (Claude Desktop, Claude Code, Cursor, Windsurf, Zed, OpenAI Agents) can call Sarvam with zero boilerplate.

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
| `sarvam_stt_transcribe` | Audio file → transcript (5 modes: transcribe, translate, verbatim, translit, codemix) | `saaras:v3` | `saarika:v2.5` (legacy) |
| `sarvam_stt_translate` | Audio → English text (DEPRECATED — use `stt_transcribe` with `mode=translate`) | `saaras:v2.5` | — |
| `sarvam_stt_batch_submit` | Long-audio job init (Azure SAS) | `saaras:v3` | `saarika:v2.5` (legacy) |
| `sarvam_stt_batch_status` | Long-audio job poll | — | — |
| `sarvam_tts_speak` | Text → audio file | `bulbul:v3` (speaker `priya`) | `bulbul:v3-beta`, `bulbul:v2` |
| `sarvam_tts_stream` | Text → streamed audio | `bulbul:v3` | `bulbul:v2` |
| `sarvam_translate` | Cross-language text translate | `mayura:v1` | `sarvam-translate:v1` (22 langs) |
| `sarvam_transliterate` | Script conversion | — | — |
| `sarvam_identify_language` | Language + script detect (11 languages) | — | — |
| `sarvam_text_analytics` | Typed Q&A over text | — | — |
| `sarvam_llm_complete` | Chat completions | `sarvam-30b` | `sarvam-105b`, `sarvam-m` (legacy) |
| `sarvam_vision_extract` | Document Intelligence (job-based pipeline) | Sarvam Vision (3B VLM) | — |
| `sarvam_vision_job_status` | Poll Document Intelligence job status | — | — |
| `sarvam_pronunciation_list` | List pronunciation dictionaries | — | — |
| `sarvam_pronunciation_get` | Get a pronunciation dictionary | — | — |
| `sarvam_pronunciation_create` | Create a pronunciation dictionary | — | — |
| `sarvam_pronunciation_delete` | Delete a pronunciation dictionary | — | — |

## Configuration

| Env var | Default | Description |
|---|---|---|
| `SARVAM_API_KEY` | — | Required. API key. Falls back to `~/.sarvam/credentials`. |
| `SARVAM_API_REGION` | `in` | Data residency region. |
| `SARVAM_API_BASE_URL` | `https://api.sarvam.ai` | Override for testing/staging. |
| `SARVAM_MCP_BASE_PATH` | `~/Desktop` | Where audio/document files land in `files` mode. |
| `SARVAM_AUDIO_OUTPUT_MODE` | `files` | `files` \| `resources` \| `both`. |

`~/.sarvam/credentials` format:

```ini
api_key = sk_...
region = in
```

## Status

Atomic tools + composite workflows (`/sv-voice`, `/sv-localize`, `/sv-recall`, `/sv-dub`) + code-builder tools (docs, snippets, scaffolders).

## Development

```bash
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"
pytest -q
mcp dev src/sarvam_mcp/server.py    # MCP Inspector
```
