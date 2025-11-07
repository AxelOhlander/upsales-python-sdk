"""
Tests for authentication module.

Tests token refresh and fallback authentication.
"""

import pytest
from pytest_httpx import HTTPXMock

from upsales.auth import AuthenticationManager


def test_auth_manager_creation():
    """Test creating authentication manager."""
    auth = AuthenticationManager(
        token="test_token",
        email="user@email.com",
        password="password",
        enable_fallback=True,
    )

    assert auth.token == "test_token"
    assert auth.email == "user@email.com"
    assert auth.password == "password"
    assert auth.enable_fallback is True


def test_auth_manager_without_fallback():
    """Test auth manager without fallback enabled."""
    auth = AuthenticationManager(
        token="test_token",
        enable_fallback=False,
    )

    assert auth.enable_fallback is False
    assert not auth.should_retry_with_refresh()


def test_should_retry_with_refresh():
    """Test should_retry_with_refresh logic."""
    # With fallback enabled and credentials
    auth = AuthenticationManager(
        token="test",
        email="user@email.com",
        password="password",
        enable_fallback=True,
    )
    assert auth.should_retry_with_refresh() is True

    # Without fallback enabled
    auth = AuthenticationManager(
        token="test",
        email="user@email.com",
        password="password",
        enable_fallback=False,
    )
    assert auth.should_retry_with_refresh() is False

    # Without email
    auth = AuthenticationManager(
        token="test",
        password="password",
        enable_fallback=True,
    )
    assert auth.should_retry_with_refresh() is False

    # Without password
    auth = AuthenticationManager(
        token="test",
        email="user@email.com",
        enable_fallback=True,
    )
    assert auth.should_retry_with_refresh() is False


@pytest.mark.asyncio
async def test_refresh_token_success(httpx_mock: HTTPXMock):
    """Test successful token refresh."""
    auth = AuthenticationManager(
        token="old_token",
        email="user@email.com",
        password="password",
        enable_fallback=True,
        base_url="https://power.upsales.com/api/v2",
    )

    # Mock successful login response
    httpx_mock.add_response(
        url="https://power.upsales.com/api/v2/session/",
        method="POST",
        json={
            "data": {
                "token": "new_token",
                "isTwoFactorAuth": False,
            }
        },
        status_code=200,
    )

    new_token = await auth.refresh_token()

    assert new_token == "new_token"
    assert auth.token == "new_token"


@pytest.mark.asyncio
async def test_refresh_token_invalid_credentials(httpx_mock: HTTPXMock):
    """Test token refresh with invalid credentials."""
    auth = AuthenticationManager(
        token="old_token",
        email="user@email.com",
        password="wrong_password",
        enable_fallback=True,
    )

    # Mock 401 response
    httpx_mock.add_response(
        url="https://power.upsales.com/api/v2/session/",
        method="POST",
        status_code=401,
        text="Unauthorized",
    )

    with pytest.raises(RuntimeError, match="Invalid email or password"):
        await auth.refresh_token()


@pytest.mark.asyncio
async def test_refresh_token_without_credentials():
    """Test token refresh without email/password."""
    auth = AuthenticationManager(
        token="old_token",
        enable_fallback=True,
    )

    with pytest.raises(ValueError, match="Email and password required"):
        await auth.refresh_token()


@pytest.mark.asyncio
async def test_refresh_token_server_error(httpx_mock: HTTPXMock):
    """Test token refresh with server error."""
    auth = AuthenticationManager(
        token="old_token",
        email="user@email.com",
        password="password",
        enable_fallback=True,
    )

    # Mock 500 response
    httpx_mock.add_response(
        url="https://power.upsales.com/api/v2/session/",
        method="POST",
        status_code=500,
        text="Internal Server Error",
    )

    with pytest.raises(RuntimeError, match="Token refresh failed with status 500"):
        await auth.refresh_token()


@pytest.mark.asyncio
async def test_refresh_token_request_body(httpx_mock: HTTPXMock):
    """Test that refresh token sends correct request body."""
    auth = AuthenticationManager(
        token="old_token",
        email="user@email.com",
        password="my_password",
        enable_fallback=True,
    )

    # Mock response and capture request
    httpx_mock.add_response(
        url="https://power.upsales.com/api/v2/session/",
        method="POST",
        json={"data": {"token": "new_token", "isTwoFactorAuth": False}},
    )

    await auth.refresh_token()

    # Check request was made with correct body
    request = httpx_mock.get_request()
    assert request is not None
    assert request.method == "POST"

    # Parse JSON body
    import json

    body = json.loads(request.content)
    assert body == {
        "email": "user@email.com",
        "password": "my_password",
        "samlBypass": None,
    }


def test_get_token():
    """Test getting current token."""
    auth = AuthenticationManager(token="test_token")
    assert auth.get_token() == "test_token"


def test_repr():
    """Test string representation."""
    auth = AuthenticationManager(
        token="test",
        enable_fallback=True,
    )
    assert "with fallback" in repr(auth)

    auth = AuthenticationManager(
        token="test",
        enable_fallback=False,
    )
    assert "no fallback" in repr(auth)


@pytest.mark.asyncio
async def test_refresh_token_concurrent_requests(httpx_mock: HTTPXMock):
    """Test that concurrent refresh attempts use lock properly."""
    auth = AuthenticationManager(
        token="old_token",
        email="user@email.com",
        password="password",
        enable_fallback=True,
    )

    # Mock response (will be called twice if lock doesn't work)
    httpx_mock.add_response(
        url="https://power.upsales.com/api/v2/session/",
        method="POST",
        json={"data": {"token": "new_token", "isTwoFactorAuth": False}},
    )

    # Make concurrent refresh requests
    import asyncio

    results = await asyncio.gather(
        auth.refresh_token(),
        auth.refresh_token(),
    )

    # Both should return same token
    assert results[0] == "new_token"
    assert results[1] == "new_token"

    # Lock should ensure only one request was made
    requests = httpx_mock.get_requests()
    assert len(requests) == 1


@pytest.mark.asyncio
async def test_refresh_token_updates_auth_manager_token(httpx_mock: HTTPXMock):
    """Test that refresh updates the auth manager's token."""
    auth = AuthenticationManager(
        token="old_token",
        email="user@email.com",
        password="password",
        enable_fallback=True,
    )

    httpx_mock.add_response(
        url="https://power.upsales.com/api/v2/session/",
        method="POST",
        json={"data": {"token": "refreshed_token", "isTwoFactorAuth": False}},
    )

    assert auth.token == "old_token"

    new_token = await auth.refresh_token()

    assert new_token == "refreshed_token"
    assert auth.token == "refreshed_token"
    assert auth.get_token() == "refreshed_token"
