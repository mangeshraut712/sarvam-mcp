"""Live catalog check — GET /v1/models is unmetered and returns HTTP 200 on this key."""

from __future__ import annotations

import os

import pytest

from sarvam_mcp.auth import StaticKeyProvider, set_auth
from sarvam_mcp.http import SarvamClient

pytestmark = pytest.mark.skipif(
    not os.environ.get("SARVAM_API_KEY"),
    reason="SARVAM_API_KEY not set",
)


async def test_live_models_catalog_returns_200() -> None:
    key = os.environ["SARVAM_API_KEY"]
    set_auth(StaticKeyProvider(key))
    client = SarvamClient("https://api.sarvam.ai")
    try:
        payload, metrics = await client.get_json("/v1/models")
    finally:
        await client.aclose()

    assert metrics.status_code == 200
    ids = {item["id"] for item in payload["data"]}
    assert "sarvam-105b" in ids
    assert "sarvam-105b-conversations" in ids
