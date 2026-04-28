# Agent Guide — sarvam-mcp

## Tool Namespace Routing

This MCP server exposes two tool namespaces. Pick the right one:

### `sarvam_tools_*` — Runtime (do the thing NOW)

Use when the user wants to **perform** a Sarvam action in the current conversation:

- "Translate this paragraph to Tamil"
- "Read this audio file and transcribe it"
- "Say this in Hindi" (TTS)
- "Dub this audio into Kannada"

These tools call the Sarvam API live and return results (text, audio files, etc.).

Includes composite workflows that chain multiple API calls:

- `sarvam_tools_voice` — audio in → STT → LLM reply → TTS → audio out
- `sarvam_tools_dub` — audio in → STT → Translate → TTS (dubbing)
- `sarvam_tools_localize` — translate an entire i18n string-table file
- `sarvam_tools_recall` — audio in → STT → LLM summary

### `sarvam_code_*` — Build-time (help the user WRITE code)

Use when the user is **building an app** that calls Sarvam APIs:

- "How do I call the TTS endpoint from Python?"
- "Which languages does STT support?"
- "What speakers are available for Bulbul v3?"
- "Scaffold me a Next.js app with Sarvam translation"
- "What's the request shape for /translate?"

These tools return documentation, code snippets, API reference, and project templates. They do NOT call the Sarvam API at runtime.

### Decision rule

> Is the user asking you to **use** Sarvam right now, or to **write code** that uses Sarvam?
>
> - Use Sarvam → `sarvam_tools_*`
> - Write code that uses Sarvam → `sarvam_code_*`

## Architecture

```
src/sarvam_mcp/
├── server.py          # FastMCP entry point, registers all tools
├── config.py          # Env vars + ~/.sarvam/credentials
├── _registry.py       # ServerContext dataclass (config + client + sink)
├── auth/              # API key management + MCP elicitation flow
│   ├── api_key.py     # StaticKeyProvider (produces auth headers)
│   ├── context.py     # ContextVar for current provider
│   └── elicit.py      # Ask user for API key on first tool call
├── http/              # SarvamClient (httpx wrapper, retry, error mapping)
├── audio/             # AudioSink strategy (files / resources / both)
├── observability.py   # Latency + cost + request-id tracking
├── tools/             # Atomic tools — one Sarvam API call each
├── workflows/         # Composite tools — chain multiple atomic calls
└── code/              # Builder tools — docs, snippets, scaffolders
    ├── _data.py       # Hard-coded reference tables
    ├── _snippets.py   # Embedded code examples
    └── templates/     # Scaffold project templates
```

## Conventions

- Every tool module exports `register(mcp: FastMCP)`.
- Every tool that calls the Sarvam API starts with `sc = await ready_ctx(ctx)`.
- Every tool response includes an `observability` dict with latency, request IDs, and credit usage.
- `_data.py` and `_snippets.py` are reference tables — update carefully.
- Scaffold templates in `code/templates/` contain `${VAR}` placeholders — ruff skips them.
- Run `pytest -q` before committing.
