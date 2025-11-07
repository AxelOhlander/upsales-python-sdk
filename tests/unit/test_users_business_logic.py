"""
Tests for Users business logic (API keys, user types, etc.).

Tests the ghost/active flag combinations and helper methods.
"""

import pytest
from pytest_httpx import HTTPXMock

from upsales.http import HTTPClient
from upsales.models.user import User
from upsales.resources.users import UsersResource


def test_user_type_active_regular_user():
    """Test user_type for active regular user."""
    user = User(
        id=1,
        name="John",
        email="john@example.com",
        active=1,
        ghost=0,
        regDate="2025-01-01",
        custom=[],
    )

    assert user.user_type == "active"
    assert user.is_active is True
    assert user.is_api_key is False


def test_user_type_api_key():
    """Test user_type for API key."""
    api_user = User(
        id=2,
        name="API Key",
        email="api@service.com",
        active=1,
        ghost=1,  # API key marker
        regDate="2025-01-01",
        custom=[],
    )

    assert api_user.user_type == "api_key"
    assert api_user.is_active is True  # Technically active
    assert api_user.is_api_key is True


def test_user_type_inactive():
    """Test user_type for inactive user."""
    inactive = User(
        id=3,
        name="Inactive",
        email="inactive@example.com",
        active=0,
        ghost=0,
        regDate="2025-01-01",
        custom=[],
    )

    assert inactive.user_type == "inactive"
    assert inactive.is_active is False
    assert inactive.is_api_key is False


def test_user_type_invalid_state():
    """Test user_type for invalid state (inactive API key)."""
    invalid = User(
        id=4,
        name="Invalid",
        email="invalid@example.com",
        active=0,
        ghost=1,  # Ghost but not active (shouldn't exist)
        regDate="2025-01-01",
        custom=[],
    )

    assert invalid.user_type == "invalid"
    assert invalid.is_active is False
    assert invalid.is_api_key is False  # Not active, so not a valid API key


# Integration tests for get_active()
@pytest.mark.asyncio
async def test_get_active_excludes_api_keys_by_default(httpx_mock: HTTPXMock):
    """Test get_active() excludes API keys by default."""
    sample_users = [
        {
            "id": 1,
            "name": "Regular User",
            "email": "user@example.com",
            "active": 1,
            "ghost": 0,
            "administrator": 0,
            "regDate": "2025-01-01",
            "custom": [],
        }
    ]

    httpx_mock.add_response(
        url="https://power.upsales.com/api/v2/users?active=1&ghost=0&limit=100&offset=0",
        json={"error": None, "data": sample_users},
    )

    async with HTTPClient(token="test_token", auth_manager=None) as http:
        resource = UsersResource(http)
        users = await resource.get_active()  # Default: exclude API keys

        assert len(users) == 1
        assert users[0].ghost == 0  # Only regular users

        # Verify correct query params
        request = httpx_mock.get_requests()[0]
        assert "active=1" in str(request.url)
        assert "ghost=0" in str(request.url)


@pytest.mark.asyncio
async def test_get_active_includes_api_keys_when_requested(httpx_mock: HTTPXMock):
    """Test get_active(include_api_keys=True) includes API keys."""
    sample_users = [
        {
            "id": 1,
            "name": "Regular User",
            "email": "user@example.com",
            "active": 1,
            "ghost": 0,
            "administrator": 0,
            "regDate": "2025-01-01",
            "custom": [],
        },
        {
            "id": 2,
            "name": "API Key",
            "email": "api@service.com",
            "active": 1,
            "ghost": 1,  # API key
            "administrator": 0,
            "regDate": "2025-01-01",
            "custom": [],
        },
    ]

    httpx_mock.add_response(
        url="https://power.upsales.com/api/v2/users?active=1&limit=100&offset=0",
        json={"error": None, "data": sample_users},
    )

    async with HTTPClient(token="test_token", auth_manager=None) as http:
        resource = UsersResource(http)
        users = await resource.get_active(include_api_keys=True)

        assert len(users) == 2
        # Includes both ghost=0 and ghost=1
        assert any(u.ghost == 0 for u in users)  # Regular user
        assert any(u.ghost == 1 for u in users)  # API key

        # Verify query params (no ghost filter)
        request = httpx_mock.get_requests()[0]
        assert "active=1" in str(request.url)
        assert "ghost" not in str(request.url)  # Not filtered


# Coverage check
# Run: uv run pytest tests/unit/test_users_business_logic.py -v --cov=upsales/models/user.py --cov=upsales/resources/users.py
