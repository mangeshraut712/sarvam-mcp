#!/usr/bin/env bash
# Local / agent verification loop. CI python and web jobs run the same commands.
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"

if [[ -x "$root/.venv/bin/pytest" ]]; then
  "$root/.venv/bin/pytest" -q
  "$root/.venv/bin/ruff" check .
else
  pytest -q
  ruff check .
fi

(cd "$root/web" && npx tsc --noEmit)
