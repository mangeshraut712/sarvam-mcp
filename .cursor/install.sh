#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

# Install uv if not already present (stable toolchain for Python deps).
if ! command -v uv &>/dev/null; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi
export PATH="${HOME}/.local/bin:${PATH}"

# Python MCP server — editable install with dev dependencies.
if [[ ! -d .venv ]]; then
  uv venv --python 3.12
fi
# shellcheck disable=SC1091
source .venv/bin/activate
uv pip install -e ".[dev]"

# Next.js analytics dashboard.
(cd web && npm ci)
