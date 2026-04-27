#!/usr/bin/env bash
# Sarvam MCP — 1-click installer
# Served at https://mcp.sarvam.ai/install
#
# Usage:
#   curl -fsSL https://mcp.sarvam.ai/install | bash
#   curl -fsSL https://mcp.sarvam.ai/install | bash -s -- --client cursor
#   SARVAM_API_KEY=sk_... curl -fsSL https://mcp.sarvam.ai/install | bash
#
# What it does:
#   1. Ensures `uv` is installed (uses official installer if missing).
#   2. Pre-warms `uvx sarvam-mcp` so the first tool call isn't slow.
#   3. Detects every supported MCP client on this machine.
#   4. Adds (or updates) the `sarvam` server entry in each client's
#      MCP config JSON, with idempotent merging.
#   5. Prints a summary of what was wired up.
#
# Supported clients (auto-detected):
#   • Claude Desktop  (~/Library/Application Support/Claude/claude_desktop_config.json)
#   • Claude Code     (`claude mcp add` if the CLI is on PATH)
#   • Cursor          (~/.cursor/mcp.json)
#   • Windsurf        (~/.codeium/windsurf/mcp_config.json)
#   • Zed             (~/.config/zed/settings.json -- context_servers)
#
# The script never overwrites unrelated MCP servers — it only edits the
# `sarvam` entry. Existing servers are preserved.

set -euo pipefail

# ----- args -----------------------------------------------------------------
ONLY_CLIENT=""
DRY_RUN=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --client)        ONLY_CLIENT="$2"; shift 2 ;;
    --dry-run)       DRY_RUN=1; shift ;;
    --help|-h)
      sed -n '2,30p' "$0" | sed 's/^# \{0,1\}//'
      exit 0 ;;
    *) echo "unknown arg: $1" >&2; exit 1 ;;
  esac
done

# ----- styling --------------------------------------------------------------
if [[ -t 1 ]]; then
  BOLD="\033[1m"; DIM="\033[2m"; OK="\033[32m"; WARN="\033[33m"; ERR="\033[31m"; NC="\033[0m"
else
  BOLD=""; DIM=""; OK=""; WARN=""; ERR=""; NC=""
fi
say()   { printf "%b\n" "$*"; }
note()  { say "${DIM}$*${NC}"; }
done_() { say "${OK}✓${NC} $*"; }
warn()  { say "${WARN}!${NC} $*"; }
fail()  { say "${ERR}✗${NC} $*"; exit 1; }

say "${BOLD}Sarvam MCP installer${NC}"
note "Repo: https://github.com/sarvamai/sarvam-mcp"
echo

# ----- step 1: ensure uv ----------------------------------------------------
if command -v uv >/dev/null 2>&1; then
  done_ "uv already installed ($(uv --version))"
else
  warn "uv not found — installing via the official script…"
  curl -fsSL https://astral.sh/uv/install.sh | sh
  # The installer puts uv in $HOME/.local/bin or $HOME/.cargo/bin
  export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
  command -v uv >/dev/null 2>&1 || fail "uv install failed; install manually from https://docs.astral.sh/uv/"
  done_ "uv installed"
fi

# ----- step 2: pre-warm uvx sarvam-mcp --------------------------------------
note "Pre-fetching sarvam-mcp into uvx cache…"
if [[ "$DRY_RUN" -eq 0 ]]; then
  # Until published to PyPI, install from the GitHub repo. After publish,
  # this becomes `uv tool install sarvam-mcp`.
  uv tool install --force "git+https://github.com/sarvamai/sarvam-mcp.git" >/dev/null 2>&1 \
    || warn "Could not pre-install from GitHub (private repo?). Skipping pre-fetch — uvx will fetch on first run."
fi
done_ "sarvam-mcp ready"

# ----- step 3: locate clients -----------------------------------------------
HOME_DIR="${HOME:-$HOME}"
case "$(uname -s)" in
  Darwin)
    CLAUDE_DESKTOP_CFG="$HOME_DIR/Library/Application Support/Claude/claude_desktop_config.json" ;;
  Linux)
    CLAUDE_DESKTOP_CFG="${XDG_CONFIG_HOME:-$HOME_DIR/.config}/Claude/claude_desktop_config.json" ;;
  *)
    CLAUDE_DESKTOP_CFG="" ;;
esac
CURSOR_CFG="$HOME_DIR/.cursor/mcp.json"
WINDSURF_CFG="$HOME_DIR/.codeium/windsurf/mcp_config.json"
ZED_CFG="$HOME_DIR/.config/zed/settings.json"

# ----- step 4: build the JSON snippet --------------------------------------
SARVAM_BIN="$(command -v sarvam-mcp || echo "uvx sarvam-mcp")"

# Use Python (always present on macOS/Linux) to do safe JSON merging.
merge_into() {
  local label="$1" path="$2"
  local dir; dir="$(dirname "$path")"

  if [[ "$DRY_RUN" -eq 1 ]]; then
    note "would update: $path  ($label)"
    return 0
  fi

  mkdir -p "$dir"
  python3 - "$path" <<'PY'
import json, os, sys
path = sys.argv[1]
existing = {}
if os.path.exists(path):
    try:
        with open(path) as fh:
            existing = json.load(fh) or {}
    except Exception:
        existing = {}

servers = existing.setdefault("mcpServers", {})

# Use the absolute uvx-installed binary if available, falling back to uvx.
import shutil
binary = shutil.which("sarvam-mcp")
if binary:
    entry = {"command": binary}
else:
    entry = {"command": "uvx", "args": ["sarvam-mcp"]}

# Carry over any existing env block so we don't clobber a key the user already set.
prev = servers.get("sarvam") or {}
if isinstance(prev.get("env"), dict):
    entry["env"] = prev["env"]

# Carry over BASE_PATH if set previously.
servers["sarvam"] = entry

with open(path, "w") as fh:
    json.dump(existing, fh, indent=2)
print(f"  wrote {path}")
PY
  done_ "$label  →  $path"
}

ANY_INSTALLED=0

# Claude Desktop
if [[ -z "$ONLY_CLIENT" || "$ONLY_CLIENT" == "claude-desktop" ]]; then
  if [[ -n "$CLAUDE_DESKTOP_CFG" && -d "$(dirname "$CLAUDE_DESKTOP_CFG")" ]]; then
    merge_into "Claude Desktop" "$CLAUDE_DESKTOP_CFG"
    ANY_INSTALLED=1
  else
    note "Claude Desktop not detected"
  fi
fi

# Claude Code (CLI)
if [[ -z "$ONLY_CLIENT" || "$ONLY_CLIENT" == "claude-code" ]]; then
  if command -v claude >/dev/null 2>&1; then
    if [[ "$DRY_RUN" -eq 1 ]]; then
      note "would run: claude mcp add sarvam -- $SARVAM_BIN"
    else
      claude mcp add sarvam -- $SARVAM_BIN >/dev/null 2>&1 \
        || claude mcp remove sarvam >/dev/null 2>&1 && claude mcp add sarvam -- $SARVAM_BIN >/dev/null 2>&1 \
        || warn "claude mcp add failed — you can run manually: claude mcp add sarvam -- $SARVAM_BIN"
      done_ "Claude Code  →  added via \`claude mcp add\`"
    fi
    ANY_INSTALLED=1
  else
    note "Claude Code (claude CLI) not detected"
  fi
fi

# Cursor
if [[ -z "$ONLY_CLIENT" || "$ONLY_CLIENT" == "cursor" ]]; then
  if [[ -d "$HOME_DIR/.cursor" || -d "/Applications/Cursor.app" ]]; then
    merge_into "Cursor" "$CURSOR_CFG"
    ANY_INSTALLED=1
  else
    note "Cursor not detected"
  fi
fi

# Windsurf
if [[ -z "$ONLY_CLIENT" || "$ONLY_CLIENT" == "windsurf" ]]; then
  if [[ -d "$HOME_DIR/.codeium" || -d "/Applications/Windsurf.app" ]]; then
    merge_into "Windsurf" "$WINDSURF_CFG"
    ANY_INSTALLED=1
  else
    note "Windsurf not detected"
  fi
fi

# Zed
if [[ -z "$ONLY_CLIENT" || "$ONLY_CLIENT" == "zed" ]]; then
  if [[ -f "$ZED_CFG" || -d "/Applications/Zed.app" ]]; then
    note "Zed config file is JSONC — please add the snippet manually:"
    cat <<EOF
    "context_servers": {
      "sarvam": { "command": { "path": "$SARVAM_BIN", "args": [] } }
    }
EOF
    ANY_INSTALLED=1
  else
    note "Zed not detected"
  fi
fi

# ----- step 5: optional API key -------------------------------------------
if [[ -n "${SARVAM_API_KEY:-}" ]]; then
  if [[ "$DRY_RUN" -eq 0 ]]; then
    mkdir -p "$HOME_DIR/.sarvam"
    printf "# Sarvam credentials — written by mcp.sarvam.ai install script\napi_key = %s\n" "$SARVAM_API_KEY" \
      > "$HOME_DIR/.sarvam/credentials"
    chmod 600 "$HOME_DIR/.sarvam/credentials"
  fi
  done_ "API key saved to ~/.sarvam/credentials  (mode 0600)"
else
  note "No SARVAM_API_KEY provided — Cursor/Claude will prompt you for it on the first tool call."
  note "You can also run \`sarvam-mcp init\` anytime to set it up interactively."
fi

# ----- step 6: summary -----------------------------------------------------
echo
if [[ "$ANY_INSTALLED" -eq 0 ]]; then
  warn "No MCP-aware clients detected on this machine."
  warn "Install Cursor / Claude Desktop / Windsurf / Zed and re-run this script."
  exit 0
fi

say "${BOLD}Done.${NC} Restart your MCP client (Cursor / Claude Desktop / etc.)"
say "and try saying:  ${DIM}\"Translate hello to Hindi.\"${NC}"
echo
say "${DIM}Get an API key:  https://dashboard.sarvam.ai${NC}"
say "${DIM}Source code:     https://github.com/sarvamai/sarvam-mcp${NC}"
