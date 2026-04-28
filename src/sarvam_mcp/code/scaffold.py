"""``sarvam_code_*`` scaffold tools — write working Sarvam-using projects to disk.

Three tools:
  - sarvam_code_list_scaffolds — discover available templates
  - sarvam_code_scaffold       — copy a template tree to a target dir, with vars
  - sarvam_code_setup_env      — write .env / .env.example + .gitignore touchups

Templates live in ``src/sarvam_mcp/code/templates/<name>/`` with a
``template.json`` manifest that declares variables and metadata.
"""

from __future__ import annotations

import contextlib
import json
import re
import shutil
from importlib.resources import as_file, files
from pathlib import Path
from typing import Any, Literal

from fastmcp import FastMCP
from pydantic import Field

# Regex used to expand ${VAR} placeholders inside template files.
_VAR_RE = re.compile(r"\$\{([A-Z_][A-Z0-9_]*)\}")

# Files we never copy from a template (build/vcs artifacts).
_SKIP_NAMES = {".DS_Store", "__pycache__", ".git", "node_modules", ".next"}


def _templates_root() -> Path:
    """Locate the bundled templates directory (works in dev + installed wheel)."""
    # importlib.resources locates the package data even after pip install.
    pkg_dir = files("sarvam_mcp.code")
    with as_file(pkg_dir / "templates") as p:
        # Cast to a regular Path; the templates aren't inside a zip in our setup.
        return Path(p)


def _load_manifest(template_dir: Path) -> dict[str, Any]:
    manifest_path = template_dir / "template.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"template.json missing in {template_dir}")
    return json.loads(manifest_path.read_text())


def _list_templates() -> list[dict[str, Any]]:
    root = _templates_root()
    if not root.exists():
        return []
    out: list[dict[str, Any]] = []
    for child in sorted(root.iterdir()):
        if not child.is_dir() or child.name.startswith("_"):
            continue
        try:
            manifest = _load_manifest(child)
        except FileNotFoundError:
            continue
        out.append(
            {
                "name": child.name,
                "title": manifest.get("title", child.name),
                "description": manifest.get("description", ""),
                "stack": manifest.get("stack", []),
                "uses_apis": manifest.get("uses_apis", []),
                "options": manifest.get("options", {}),
                "file_count": _count_files(child),
            }
        )
    return out


def _count_files(d: Path) -> int:
    return sum(
        1
        for p in d.rglob("*")
        if p.is_file() and p.name not in _SKIP_NAMES and "template.json" not in p.parts
    )


def _expand_vars(text: str, vars: dict[str, str]) -> str:
    def repl(m: re.Match[str]) -> str:
        return vars.get(m.group(1), m.group(0))
    return _VAR_RE.sub(repl, text)


def _copy_template(
    src_dir: Path,
    dest_dir: Path,
    vars: dict[str, str],
) -> tuple[list[str], list[str]]:
    """Copy template tree → dest with ${VAR} expansion. Returns (created, skipped)."""
    created: list[str] = []
    skipped: list[str] = []
    for src in src_dir.rglob("*"):
        # Skip the manifest itself + ignored names + any directory components.
        if src.name in _SKIP_NAMES:
            continue
        if src.name == "template.json" and src.parent == src_dir:
            continue
        if any(part in _SKIP_NAMES for part in src.relative_to(src_dir).parts):
            continue
        rel = src.relative_to(src_dir)
        # Expand ${VAR} in path components too (for filenames like ${PROJECT_NAME}.py).
        rel_expanded = Path(*[_expand_vars(part, vars) for part in rel.parts])
        target = dest_dir / rel_expanded
        if src.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue
        if target.exists():
            skipped.append(str(target))
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        # Read as text; if it's binary, fall back to raw copy.
        try:
            content = src.read_text()
            target.write_text(_expand_vars(content, vars))
        except UnicodeDecodeError:
            shutil.copyfile(src, target)
        created.append(str(target))
    return created, skipped


# ---- Tool registrations ---------------------------------------------------


TemplateName = Literal["simple-tts-cli", "python-voice-bot", "nextjs-translator"]


def register(mcp: FastMCP) -> None:
    @mcp.tool(
        name="sarvam_code_list_scaffolds",
        description=(
            "Build-time tool — helps write code that uses Sarvam. For runtime actions, use sarvam_tools_* instead.\n\n"
            "List available Sarvam project scaffolds. Each template ships as "
            "a complete working starter project the agent can write to disk "
            "with `sarvam_code_scaffold`. Use this first to see what's "
            "available before scaffolding."
        ),
    )
    def sarvam_code_list_scaffolds() -> dict[str, Any]:
        templates = _list_templates()
        return {
            "scaffold_count": len(templates),
            "scaffolds": templates,
        }

    @mcp.tool(
        name="sarvam_code_scaffold",
        description=(
            "Build-time tool — helps write code that uses Sarvam. For runtime actions, use sarvam_tools_* instead.\n\n"
            "Write a working Sarvam-using starter project to disk. Picks a "
            "named template, copies it to `target_dir`, and substitutes "
            "any ${VAR} placeholders using `options`. After scaffolding, "
            "the agent should walk the dev through running it (npm install, "
            "pip install, etc.). Use `sarvam_code_list_scaffolds` first to "
            "see template names + required options."
        ),
    )
    def sarvam_code_scaffold(
        template: TemplateName = Field(description="Name of the scaffold to use."),
        target_dir: str = Field(
            description="Absolute path where the project will be written.",
        ),
        options: dict[str, str] = Field(
            default_factory=dict,
            description=(
                "Variable substitutions for the template. Keys must match "
                "those declared in the template's manifest (e.g. "
                "PROJECT_NAME, DEFAULT_LANGUAGE)."
            ),
        ),
    ) -> dict[str, Any]:
        src = _templates_root() / template
        if not src.exists():
            return {
                "success": False,
                "error": f"Unknown template '{template}'.",
                "available": [t["name"] for t in _list_templates()],
            }
        manifest = _load_manifest(src)
        # Apply defaults from manifest for any options the caller omits.
        full_vars = dict(manifest.get("defaults", {}))
        full_vars.update(options or {})
        # Sensible default for PROJECT_NAME if caller didn't pass one.
        full_vars.setdefault("PROJECT_NAME", Path(target_dir).expanduser().name)

        dest = Path(target_dir).expanduser().resolve()
        dest.mkdir(parents=True, exist_ok=True)
        created, skipped = _copy_template(src, dest, full_vars)

        return {
            "success": True,
            "template": template,
            "target_dir": str(dest),
            "files_created": len(created),
            "files_skipped_existing": len(skipped),
            "created": created,
            "skipped": skipped,
            "vars_applied": full_vars,
            "next_steps": manifest.get(
                "next_steps",
                ["Read the README.md inside the project for run instructions."],
            ),
        }

    @mcp.tool(
        name="sarvam_code_setup_env",
        description=(
            "Build-time tool — helps write code that uses Sarvam. For runtime actions, use sarvam_tools_* instead.\n\n"
            "Write `.env.example` (and `.env` if `api_key` is provided) into "
            "an existing project directory, and append `.env` to "
            "`.gitignore` if not already there. Run this AFTER scaffolding "
            "(or against an existing project) to wire up Sarvam credentials "
            "the conventional way."
        ),
    )
    def sarvam_code_setup_env(
        target_dir: str = Field(description="Absolute path to the project directory."),
        api_key: str | None = Field(
            default=None,
            description=(
                "If provided, writes a real .env with this value. Otherwise "
                "writes only .env.example so the dev fills it in."
            ),
        ),
    ) -> dict[str, Any]:
        target = Path(target_dir).expanduser().resolve()
        if not target.is_dir():
            return {"success": False, "error": f"Not a directory: {target}"}

        actions: list[str] = []
        # .env.example — always write/refresh.
        example = target / ".env.example"
        example_body = (
            "# Sarvam credentials — get one at https://dashboard.sarvam.ai\n"
            "SARVAM_API_KEY=sk_replace_me\n"
        )
        example.write_text(example_body)
        actions.append(f"wrote {example}")

        # .env — only if api_key was passed.
        if api_key:
            env_path = target / ".env"
            env_path.write_text(f"SARVAM_API_KEY={api_key}\n")
            actions.append(f"wrote {env_path} (mode 0600)")
            with contextlib.suppress(OSError):
                env_path.chmod(0o600)

        # .gitignore — append .env if missing.
        gi = target / ".gitignore"
        existing = gi.read_text() if gi.exists() else ""
        if ".env\n" not in existing and ".env" not in existing.split():
            with gi.open("a") as fh:
                if existing and not existing.endswith("\n"):
                    fh.write("\n")
                fh.write(".env\n")
            actions.append(f"appended .env to {gi}")
        else:
            actions.append(f"{gi} already excludes .env")

        return {
            "success": True,
            "target_dir": str(target),
            "actions": actions,
            "wrote_real_env": api_key is not None,
        }
