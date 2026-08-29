# sarvam-mcp + Vaani

[![License: MIT](https://img.shields.io/badge/License-MIT-0B6.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](CODE_OF_CONDUCT.md)

**Public, MIT-licensed** community fork of [sarvamai/sarvam-mcp](https://github.com/sarvamai/sarvam-mcp).

Two agent surfaces, one Sarvam language layer:

```
Sarvam APIs
 └── this repo
      ├── MCP server (`uvx` / `pip`) → Cursor, Claude, Windsurf, Zed
      └── Vaani (`web/`)             → browser agents via WebMCP
```

**Vaani** is a voice- and language-first web app: humans speak or type in Indian languages; browser agents call `document.modelContext.registerTool` and update the **same** page. The Python package remains the MCP server for developer tools.

See [NOTICE](NOTICE) for attribution, [CONTRIBUTING.md](CONTRIBUTING.md) to hack on it, and [SUBMISSION.md](SUBMISSION.md) if you are entering the OpenAI WebMCP Challenge.

## Quickstart — MCP (desktop agents)

1. Get an API key at [dashboard.sarvam.ai/key-management](https://dashboard.sarvam.ai/key-management).

2. Install **upstream** PyPI (official Sarvam package):

```bash
uvx sarvam-mcp
# or: pip install sarvam-mcp
```

3. Or run **this fork** from source:

```bash
git clone https://github.com/mangeshraut712/sarvam-mcp.git
cd sarvam-mcp
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"
```

MCP client config:

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

From a source checkout, point `command` at `.venv/bin/sarvam-mcp` (or `python -m sarvam_mcp.server` if you add that later). Config paths: Cursor `~/.cursor/mcp.json`; Claude Desktop `claude_desktop_config.json`; Windows uses `%USERPROFILE%` / `%APPDATA%`.

You can store `api_key = sk_...` in `~/.sarvam/credentials` instead of the JSON `env` block.

## Quickstart — Vaani (WebMCP)

```bash
export SARVAM_API_KEY=sk_...   # optional; labeled demo mode works without credits
cd web && npm ci && npm run dev
# http://localhost:3000/vaani
```

Tools registered on the page: `understand_audio`, `translate_content`, `explain_content`, `summarize_content`, `speak_content`, `create_multilingual_note`.

Test WebMCP in ChatGPT’s in-app browser, or Chrome 149+ with `chrome://flags/#enable-webmcp-testing`.

Voice playground (STT → Lang ID → LLM → TTS): `/playground`.

### Deploy the site

```bash
cd web
npx vercel --prod          # set SARVAM_API_KEY in the Vercel project
# or
docker build -t vaani-web .
docker run --rm -p 8000:8000 -e SARVAM_API_KEY=sk_... vaani-web
```

Health: `/health`, `/ready`, `/api/sarvam-status`.

## MCP tools

Defaults match current non-deprecated Sarvam models.

| Tool | What it does | Default model |
|---|---|---|
| `sarvam_stt_transcribe` | Audio file → transcript | `saaras:v3` |
| `sarvam_tts_speak` | Text → audio file | `bulbul:v3` |
| `sarvam_tts_stream` | Text → streamed audio | `bulbul:v3` |
| `sarvam_translate` | Cross-language text translate | `mayura:v1` |
| `sarvam_transliterate` | Script conversion | — |
| `sarvam_identify_language` | Language + script detect | — |
| `sarvam_text_analytics` | Typed Q&A over text | — |
| `sarvam_llm_complete` | Chat completions | `sarvam-105b` |
| `sarvam_vision_extract` | Document Intelligence | Sarvam Vision |
| `sarvam_vision_job_status` | Poll Document Intelligence job | — |
| `sarvam_pronunciation_*` | Pronunciation dictionaries | — |

Namespaces: `sarvam_tools_*` (call APIs now) vs `sarvam_code_*` (docs and snippets for builders).

## Configuration

| Env var | Default | Description |
|---|---|---|
| `SARVAM_API_KEY` | — | API key from dashboard.sarvam.ai |
| `SARVAM_API_BASE_URL` | `https://api.sarvam.ai` | Override for testing |
| `SARVAM_MCP_BASE_PATH` | `~/Desktop` | Where audio/document files land |
| `SARVAM_AUDIO_OUTPUT_MODE` | `files` | `files` \| `resources` \| `both` |
| `VAANI_DEMO` | on unless `0` | Labeled UI demo if inference returns 402 or no key |

`GET https://api.sarvam.ai/v1/models` is unmetered; STT/TTS/LLM/translate consume credits.

## Development

```bash
uv pip install -e ".[dev]"
pytest -q
ruff check .
cd web && npx tsc --noEmit
mcp dev src/sarvam_mcp/server.py
```

## License and community

- [LICENSE](LICENSE) — MIT (Sarvam AI + Vaani contributors)
- [NOTICE](NOTICE) — fork attribution
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- [SECURITY.md](SECURITY.md)
