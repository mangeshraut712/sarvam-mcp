"""Tests for ``resolve_file_input`` (path / base64 / URL exclusive)."""

from __future__ import annotations

import base64
from pathlib import Path

import pytest

from sarvam_mcp.tools._common import resolve_file_input

PAYLOAD = b"sarvam-fixture-bytes"


async def test_resolve_file_path_yields_existing_file(tmp_path: Path):
    src = tmp_path / "clip.wav"
    src.write_bytes(PAYLOAD)
    async with resolve_file_input(file_path=str(src)) as path:
        assert path == src
        assert path.read_bytes() == PAYLOAD
    assert src.exists()


async def test_resolve_file_base64_writes_temp_then_cleans_up():
    encoded = base64.b64encode(PAYLOAD).decode()
    async with resolve_file_input(file_base64=encoded, filename="clip.wav") as path:
        assert path.suffix == ".wav"
        assert path.read_bytes() == PAYLOAD
        tmp = path
    assert not tmp.exists()


async def test_resolve_file_rejects_missing_and_multiple_sources():
    with pytest.raises(ValueError, match="exactly one"):
        async with resolve_file_input():
            pass
    with pytest.raises(ValueError, match="exactly one"):
        async with resolve_file_input(file_path="a", file_base64="b"):
            pass
