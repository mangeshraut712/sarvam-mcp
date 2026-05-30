"""Auth provider tests."""

from __future__ import annotations

import pytest

from sarvam_mcp.auth import StaticKeyProvider, current_auth, set_auth
from sarvam_mcp.auth.context import _current


async def test_static_provider_emits_bearer_header():
    provider = StaticKeyProvider("test_jwt_token_1234")
    headers = await provider.headers()
    assert headers == {"Authorization": "Bearer test_jwt_token_1234"}


async def test_static_provider_principal_redacts_secret():
    provider = StaticKeyProvider("test_jwt_token_1234")
    assert provider.principal == "jwt:****1234"
    assert "token" not in provider.principal


async def test_static_provider_ignores_scope_argument():
    provider = StaticKeyProvider("test_jwt_token_1234")
    base = await provider.headers()
    scoped = await provider.headers(scope="flow:run")
    assert base == scoped


def test_empty_token_rejected():
    with pytest.raises(ValueError):
        StaticKeyProvider("")


def test_current_auth_raises_when_unset():
    token = _current.set(None)
    try:
        with pytest.raises(RuntimeError, match="Not authenticated"):
            current_auth()
    finally:
        _current.reset(token)


def test_set_and_get_round_trip():
    provider = StaticKeyProvider("test_jwt_other")
    set_auth(provider)
    assert current_auth() is provider
