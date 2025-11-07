"""
Tests for UsersResource custom methods.

Tests endpoint-specific methods beyond base CRUD operations.

Coverage target: 85%+
"""

import pytest
from pytest_httpx import HTTPXMock

from upsales.http import HTTPClient
from upsales.models.user import User
from upsales.resources.users import UsersResource


class TestUsersResourceCustomMethods:
    """Test custom methods specific to UsersResource."""

    @pytest.fixture
    def sample_user(self):
        """Sample user data."""
        return {
            "id": 1,
            "name": "John Doe",
            "email": "john@example.com",
            "active": 1,
            "administrator": 1,
            "regDate": "2025-01-01",
            "custom": [],
        }

    @pytest.mark.asyncio
    async def test_get_by_email_found(self, httpx_mock: HTTPXMock, sample_user):
        """Test get_by_email() finds user by email address."""
        # get_by_email calls list_all() which fetches all users then filters
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users?limit=100&offset=0",
            json={
                "error": None,
                "data": [
                    sample_user,
                    {**sample_user, "id": 2, "email": "other@example.com"},
                ],
            },
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UsersResource(http)
            result = await resource.get_by_email("john@example.com")

            assert isinstance(result, User)
            assert result.email == "john@example.com"
            assert result.id == 1

    @pytest.mark.asyncio
    async def test_get_by_email_not_found(self, httpx_mock: HTTPXMock, sample_user):
        """Test get_by_email() returns None when user not found."""
        # get_by_email calls list_all() which fetches all users
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users?limit=100&offset=0",
            json={
                "error": None,
                "data": [
                    {**sample_user, "email": "other@example.com"},
                ],
            },
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UsersResource(http)
            result = await resource.get_by_email("notfound@example.com")

            assert result is None

    @pytest.mark.asyncio
    async def test_get_administrators(self, httpx_mock: HTTPXMock, sample_user):
        """Test get_administrators() returns only admin users."""
        admin_users = [
            {**sample_user, "id": 1, "administrator": 1},
            {**sample_user, "id": 2, "administrator": 1, "name": "Jane Admin"},
        ]

        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users?administrator=1&limit=100&offset=0",
            json={"error": None, "data": admin_users},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UsersResource(http)
            results = await resource.get_administrators()

            assert len(results) == 2
            assert all(isinstance(user, User) for user in results)
            assert all(user.administrator == 1 for user in results)
            assert all(user.is_admin for user in results)

    @pytest.mark.asyncio
    async def test_get_active(self, httpx_mock: HTTPXMock, sample_user):
        """Test get_active() returns only active users (excludes API keys by default)."""
        active_users = [
            {**sample_user, "id": 1, "active": 1, "ghost": 0},
            {**sample_user, "id": 2, "active": 1, "ghost": 0, "name": "Active User 2"},
            {**sample_user, "id": 3, "active": 1, "ghost": 0, "name": "Active User 3"},
        ]

        # Default behavior: excludes API keys (ghost=0)
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/users?active=1&ghost=0&limit=100&offset=0",
            json={"error": None, "data": active_users},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UsersResource(http)
            results = await resource.get_active()  # Default: exclude API keys

            assert len(results) == 3
            assert all(user.active == 1 for user in results)
            assert all(user.ghost == 0 for user in results)  # No API keys
            assert all(user.is_active for user in results)


# Coverage check
# Run: uv run pytest tests/unit/test_users_resource.py -v --cov=upsales/resources/users.py --cov-report=term-missing
