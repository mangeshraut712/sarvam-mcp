"""Auth provider tests."""

from __future__ import annotations

import pytest

from sarvam_mcp.auth import StaticKeyProvider, current_auth, set_auth
from sarvam_mcp.auth.context import _current
from sarvam_mcp.auth.oauth import FlowAuthNotConfiguredError, OAuthProvider


async def test_static_provider_emits_subscription_header():
    provider = StaticKeyProvider("sk_test_abcd1234")
    headers = await provider.headers()
    assert headers == {"api-subscription-key": "sk_test_abcd1234"}


async def test_static_provider_principal_redacts_secret():
    provider = StaticKeyProvider("sk_test_abcd1234")
    assert provider.principal == "api-key:****1234"
    assert "abcd" not in provider.principal


async def test_static_provider_ignores_scope_argument():
    provider = StaticKeyProvider("sk_test_abcd1234")
    base = await provider.headers()
    scoped = await provider.headers(scope="flow:run")
    assert base == scoped


def test_empty_key_rejected():
    with pytest.raises(ValueError):
        StaticKeyProvider("")


async def test_oauth_provider_emits_bearer_header():
    provider = OAuthProvider("at_xyz", principal_id="om@sarvam.ai")
    headers = await provider.headers()
    assert headers == {"Authorization": "Bearer at_xyz"}
    assert provider.principal == "user:om@sarvam.ai"


async def test_oauth_refresh_blocked_in_v1():
    provider = OAuthProvider("at_xyz", principal_id="om@sarvam.ai")
    with pytest.raises(FlowAuthNotConfiguredError):
        await provider.refresh()


def test_current_auth_raises_when_unset():
    # Override conftest's autouse fixture by clearing the ContextVar.
    token = _current.set(None)
    try:
        with pytest.raises(RuntimeError, match="No AuthProvider"):
            current_auth()
    finally:
        _current.reset(token)


def test_set_and_get_round_trip():
    provider = StaticKeyProvider("sk_test_other")
    set_auth(provider)
    assert current_auth() is provider
