"""Scaffolder writes templates correctly with var substitution."""

from __future__ import annotations

from pathlib import Path

import pytest

from sarvam_mcp.code.scaffold import (
    _copy_template,
    _list_templates,
    _templates_root,
)


def test_three_templates_ship():
    names = {t["name"] for t in _list_templates()}
    assert {"simple-tts-cli", "python-voice-bot", "nextjs-translator"} <= names


def test_template_manifests_have_required_fields():
    for tmpl in _list_templates():
        for field in ("name", "title", "description", "stack", "uses_apis"):
            assert tmpl.get(field) is not None, f"{tmpl['name']} missing {field}"


@pytest.mark.parametrize("name", ["simple-tts-cli", "python-voice-bot"])
def test_scaffold_writes_files_and_substitutes_vars(name: str, tmp_path: Path):
    src = _templates_root() / name
    dest = tmp_path / "demo"
    dest.mkdir()
    created, _ = _copy_template(
        src,
        dest,
        {"PROJECT_NAME": "demo-app", "DEFAULT_LANGUAGE": "hi-IN", "DEFAULT_SPEAKER": "priya", "REPLY_LANGUAGE": "hi-IN"},
    )
    assert created, "expected files to be written"

    # README should mention the project name we passed.
    readme = (dest / "README.md").read_text()
    assert "demo-app" in readme

    # No raw ${VAR} placeholders should leak into output.
    for path in dest.rglob("*"):
        if path.is_file():
            try:
                text = path.read_text()
            except UnicodeDecodeError:
                continue
            assert "${" not in text, f"unsubstituted placeholder in {path}"


def test_scaffold_does_not_overwrite_existing(tmp_path: Path):
    src = _templates_root() / "simple-tts-cli"
    dest = tmp_path / "demo"
    dest.mkdir()
    (dest / "README.md").write_text("hand-written, do not touch")

    created, skipped = _copy_template(src, dest, {"PROJECT_NAME": "demo"})
    assert any("README.md" in s for s in skipped), "README.md should have been skipped"
    assert (dest / "README.md").read_text() == "hand-written, do not touch"
