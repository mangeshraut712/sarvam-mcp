#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

export PATH="${HOME}/.local/bin:${PATH}"

if [[ ! -d .venv ]]; then
  echo "error: .venv missing — run install first" >&2
  exit 1
fi

if [[ ! -d web/node_modules ]]; then
  echo "error: web/node_modules missing — run install first" >&2
  exit 1
fi

if [[ -z "${SARVAM_API_KEY:-}" ]] && [[ ! -f "${HOME}/.sarvam/credentials" ]]; then
  echo "note: SARVAM_API_KEY not set — Voice Playground and runtime MCP tools need a key"
fi

echo "sarvam-mcp environment ready"
