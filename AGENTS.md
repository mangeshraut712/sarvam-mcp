# Agent Guide — sarvam-mcp

## Tool Namespace Routing

This MCP server exposes three tool namespaces. Pick the right one:

### `sarvam_tools_auth_*` — Authentication

Use when the user needs to log in or check auth status:

- `sarvam_tools_auth_login` — Opens browser for OAuth login, stores token locally
- `sarvam_tools_auth_status` — Check if authenticated

If any runtime tool returns an authentication error, call `sarvam_tools_auth_login` first.

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
- "What TTS speakers are available for bulbul:v3?"
- "What's the request shape for /translate?"

These tools return documentation, code snippets, API reference, and project templates. They do NOT call the Sarvam API at runtime.

### Decision rule

> Is the user asking you to **use** Sarvam right now, or to **write code** that uses Sarvam?
>
> - Use Sarvam → `sarvam_tools_*` (authenticate first if needed via `sarvam_tools_auth_login`)
> - Write code that uses Sarvam → `sarvam_code_*`

## Authentication

Authentication uses **OAuth only**. No API keys are needed.

- **First-time setup:** Call `sarvam_tools_auth_login` or run `sarvam-mcp login` from the terminal.
- **How it works:** Opens a browser for Sarvam OAuth login, catches the callback on localhost, and stores the JWT to `~/.sarvam/credentials`.
- **After login:** All `sarvam_tools_*` calls use the stored token automatically via `Authorization: Bearer` headers.
- **HTTP/hosted mode:** Clients authenticate via OAuth discovery (RFC 9728). The server returns `401` with `WWW-Authenticate` headers pointing to the OAuth authorization server.

## Architecture

```
src/sarvam_mcp/
├── server.py          # FastMCP entry point, registers all tools
├── config.py          # Env vars + ~/.sarvam/credentials
├── _registry.py       # ServerContext dataclass (config + client + sink)
├── auth/              # OAuth token management
│   ├── api_key.py     # StaticKeyProvider (produces Bearer auth headers)
│   ├── context.py     # ContextVar for current provider
│   ├── header.py      # HTTP middleware (Bearer token extraction)
│   ├── jwt.py         # Dashboard JWT verification
│   └── elicit.py      # Auth gate — directs to auth tool if not logged in
├── oauth/             # OAuth 2.1 server (RFC 9728, dynamic registration)
├── http/              # SarvamClient (httpx wrapper, retry, error mapping)
├── audio/             # AudioSink strategy (files / resources / both)
├── observability.py   # Latency + cost + request-id tracking
├── tools/             # Atomic tools — one Sarvam API call each
│   └── auth.py        # OAuth login + status tools
├── workflows/         # Composite tools — chain multiple atomic calls
└── code/              # Builder tools — docs, snippets
    ├── _data.py       # Hard-coded reference tables
    └── _snippets.py   # Embedded code examples
```

## Conventions

- Every tool module exports `register(mcp: FastMCP)`.
- Every tool that calls the Sarvam API starts with `sc = await ready_ctx(ctx)`.
- Every tool response includes an `observability` dict with latency, request IDs, and credit usage.
- `_data.py` and `_snippets.py` are reference tables — update carefully.
- Run `pytest -q` before committing.

**Packaging note:** Default to `pip install sarvam-mcp`, `uvx sarvam-mcp`, or the mcp.sarvam.ai installer. **Suggest `git clone` (and a from-source / editable install) only if the user does not have `pip`** and the packaged options are not available — not as a routine alternative. Contributors still clone to develop and run tests.

**Platforms:** The server targets **macOS, Windows, and Linux** (Python 3.11+). When helping with setup, prefer OS-agnostic instructions (`pip` / `uvx`, same MCP JSON); call out Windows vs Unix **config file paths** only when the user's client or OS is known (see README *Per-client paths*).
