"""
Integration tests for authentication with HTTPClient.

Tests automatic token refresh flow.
"""

import pytest
from pytest_httpx import HTTPXMock

from upsales.auth import AuthenticationManager
from upsales.exceptions import AuthenticationError
from upsales.http import HTTPClient


@pytest.mark.asyncio
async def test_http_client_with_auth_manager(httpx_mock: HTTPXMock):
    """Test HTTPClient with auth manager."""
    auth = AuthenticationManager(
        token="test_token",
        email="user@email.com",
        password="password",
        enable_fallback=True,
    )

    async with HTTPClient(
        token="test_token",
        auth_manager=auth,
    ) as client:
        # Mock successful request
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users/1",
            json={
                "error": None,
                "data": {"id": 1, "name": "Test User"},
            },
        )

        data = await client.get("/users/1")
        assert data["data"]["name"] == "Test User"


@pytest.mark.asyncio
async def test_automatic_token_refresh_on_401(httpx_mock: HTTPXMock):
    """Test that 401 triggers automatic token refresh."""
    auth = AuthenticationManager(
        token="expired_token",
        email="user@email.com",
        password="password",
        enable_fallback=True,
    )

    async with HTTPClient(
        token="expired_token",
        auth_manager=auth,
    ) as client:
        # First request: 401 (token expired)
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users/1",
            status_code=401,
            text="Unauthorized",
        )

        # Session endpoint: returns new token
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/session/",
            method="POST",
            json={
                "data": {
                    "token": "new_token",
                    "isTwoFactorAuth": False,
                }
            },
        )

        # Retry with new token: success
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users/1",
            json={
                "error": None,
                "data": {"id": 1, "name": "Test User"},
            },
        )

        # Make request - should auto-refresh and succeed
        data = await client.get("/users/1")

        assert data["data"]["name"] == "Test User"
        assert client.token == "new_token"
        assert auth.token == "new_token"


@pytest.mark.asyncio
async def test_no_automatic_refresh_without_fallback(httpx_mock: HTTPXMock):
    """Test that 401 raises error when fallback disabled."""
    auth = AuthenticationManager(
        token="expired_token",
        enable_fallback=False,  # Disabled
    )

    async with HTTPClient(
        token="expired_token",
        auth_manager=auth,
    ) as client:
        # Mock 401 response
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users/1",
            status_code=401,
            text="Unauthorized",
        )

        # Should raise AuthenticationError without attempting refresh
        with pytest.raises(AuthenticationError, match="Authentication failed"):
            await client.get("/users/1")


@pytest.mark.asyncio
async def test_no_automatic_refresh_without_credentials(httpx_mock: HTTPXMock):
    """Test that 401 raises error when credentials missing."""
    auth = AuthenticationManager(
        token="expired_token",
        enable_fallback=True,  # Enabled but no credentials
    )

    async with HTTPClient(
        token="expired_token",
        auth_manager=auth,
    ) as client:
        # Mock 401 response
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users/1",
            status_code=401,
            text="Unauthorized",
        )

        # Should raise AuthenticationError without attempting refresh
        with pytest.raises(AuthenticationError, match="Authentication failed"):
            await client.get("/users/1")


@pytest.mark.asyncio
async def test_refresh_only_attempted_once(httpx_mock: HTTPXMock):
    """Test that refresh is only attempted once per request."""
    auth = AuthenticationManager(
        token="expired_token",
        email="user@email.com",
        password="password",
        enable_fallback=True,
    )

    async with HTTPClient(
        token="expired_token",
        auth_manager=auth,
    ) as client:
        # First request: 401
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users/1",
            status_code=401,
        )

        # Refresh: returns new token
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/session/",
            method="POST",
            json={"data": {"token": "new_token", "isTwoFactorAuth": False}},
        )

        # Retry: also 401 (new token also invalid)
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users/1",
            status_code=401,
        )

        # Should raise after one refresh attempt
        with pytest.raises(AuthenticationError, match="even after token refresh"):
            await client.get("/users/1")

        # Verify refresh was only called once
        requests = httpx_mock.get_requests(url="https://power.upsales.com/api/v2/session/")
        assert len(requests) == 1


@pytest.mark.asyncio
async def test_refresh_flag_resets_on_success(httpx_mock: HTTPXMock):
    """Test that refresh flag resets after successful request."""
    auth = AuthenticationManager(
        token="expired_token",
        email="user@email.com",
        password="password",
        enable_fallback=True,
    )

    async with HTTPClient(
        token="expired_token",
        auth_manager=auth,
    ) as client:
        # First request: 401
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users/1",
            status_code=401,
        )

        # Refresh
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/session/",
            method="POST",
            json={"data": {"token": "new_token", "isTwoFactorAuth": False}},
        )

        # Retry: success
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users/1",
            json={"error": None, "data": {"id": 1, "name": "Test"}},
        )

        # Should succeed
        data = await client.get("/users/1")
        assert data["data"]["name"] == "Test"

        # Flag should be reset - second request should allow refresh
        assert client._auth_refresh_attempted is False


@pytest.mark.asyncio
async def test_http_client_without_auth_manager(httpx_mock: HTTPXMock):
    """Test HTTPClient without auth manager (no automatic refresh)."""
    async with HTTPClient(token="test_token") as client:
        # Mock 401 response
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users/1",
            status_code=401,
            text="Unauthorized",
        )

        # Should raise without attempting refresh
        with pytest.raises(AuthenticationError, match="Authentication failed"):
            await client.get("/users/1")


@pytest.mark.asyncio
async def test_token_updated_in_http_client(httpx_mock: HTTPXMock):
    """Test that token is updated in HTTPClient after refresh."""
    auth = AuthenticationManager(
        token="old_token",
        email="user@email.com",
        password="password",
        enable_fallback=True,
    )

    async with HTTPClient(
        token="old_token",
        auth_manager=auth,
    ) as client:
        assert client.token == "old_token"

        # Mock 401
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users/1",
            status_code=401,
        )

        # Mock refresh
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/session/",
            method="POST",
            json={"data": {"token": "refreshed_token", "isTwoFactorAuth": False}},
        )

        # Mock success with new token
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users/1",
            json={"error": None, "data": {"id": 1}},
        )

        await client.get("/users/1")

        # Tokens should be updated
        assert client.token == "refreshed_token"
        assert auth.token == "refreshed_token"
