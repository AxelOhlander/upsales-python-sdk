"""Tests for UserInvitesResource custom methods.

Tests endpoint-specific methods beyond base CRUD operations.

Coverage target: 85%+
"""

import pytest
from pytest_httpx import HTTPXMock

from upsales.http import HTTPClient
from upsales.models.user_invites import UserInvite
from upsales.resources.user_invites import UserInvitesResource


class TestUserInvitesResourceCustomMethods:
    """Test custom methods specific to UserInvitesResource."""

    @pytest.fixture
    def sample_invite(self):
        """Sample user invite data."""
        return {
            "id": "invite-uuid-123",
            "name": "John Doe",
            "email": "john@example.com",
            "administrator": 0,
            "export": 0,
            "language": "en",
            "role": None,
            "killDate": "2025-12-31",
            "custom": [],
            "active": 1,
            "ghost": 0,
            "crm": 1,
            "support": 0,
        }

    @pytest.mark.asyncio
    async def test_get_by_email_found(self, httpx_mock: HTTPXMock, sample_invite):
        """Test get_by_email() finds user invite by email address."""
        # get_by_email calls list_all() which fetches all invites then filters
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/userInvites?limit=100&offset=0",
            json={
                "error": None,
                "data": [
                    sample_invite,
                    {**sample_invite, "id": "invite-uuid-456", "email": "other@example.com"},
                ],
            },
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UserInvitesResource(http)
            result = await resource.get_by_email("john@example.com")

            assert isinstance(result, UserInvite)
            assert result.email == "john@example.com"
            assert result.id == "invite-uuid-123"

    @pytest.mark.asyncio
    async def test_get_by_email_not_found(self, httpx_mock: HTTPXMock, sample_invite):
        """Test get_by_email() returns None when invite not found."""
        # get_by_email calls list_all() which fetches all invites
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/userInvites?limit=100&offset=0",
            json={
                "error": None,
                "data": [
                    {**sample_invite, "email": "other@example.com"},
                ],
            },
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UserInvitesResource(http)
            result = await resource.get_by_email("notfound@example.com")

            assert result is None

    @pytest.mark.asyncio
    async def test_get_by_email_case_insensitive(self, httpx_mock: HTTPXMock, sample_invite):
        """Test get_by_email() is case insensitive."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/userInvites?limit=100&offset=0",
            json={
                "error": None,
                "data": [sample_invite],
            },
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UserInvitesResource(http)
            result = await resource.get_by_email("JOHN@EXAMPLE.COM")

            assert result is not None
            assert result.email == "john@example.com"


class TestUserInviteModel:
    """Test UserInvite model computed fields and methods."""

    @pytest.fixture
    def sample_invite_data(self):
        """Sample invite data for model testing."""
        return {
            "id": "invite-uuid-123",
            "name": "John Doe",
            "email": "john@example.com",
            "administrator": 1,
            "export": 1,
            "active": 1,
            "ghost": 0,
            "crm": 1,
            "support": 1,
            "custom": [{"fieldId": 1, "value": "Test"}],
        }

    def test_is_admin_property(self, sample_invite_data):
        """Test is_admin computed property."""
        invite = UserInvite(**sample_invite_data)
        assert invite.is_admin is True

        invite_non_admin = UserInvite(**{**sample_invite_data, "administrator": 0})
        assert invite_non_admin.is_admin is False

    def test_is_active_property(self, sample_invite_data):
        """Test is_active computed property."""
        invite = UserInvite(**sample_invite_data)
        assert invite.is_active is True

        invite_inactive = UserInvite(**{**sample_invite_data, "active": 0})
        assert invite_inactive.is_active is False

    def test_has_crm_access_property(self, sample_invite_data):
        """Test has_crm_access computed property."""
        invite = UserInvite(**sample_invite_data)
        assert invite.has_crm_access is True

        invite_no_crm = UserInvite(**{**sample_invite_data, "crm": 0})
        assert invite_no_crm.has_crm_access is False

    def test_has_support_access_property(self, sample_invite_data):
        """Test has_support_access computed property."""
        invite = UserInvite(**sample_invite_data)
        assert invite.has_support_access is True

        invite_no_support = UserInvite(**{**sample_invite_data, "support": 0})
        assert invite_no_support.has_support_access is False

    def test_custom_fields_property(self, sample_invite_data):
        """Test custom_fields computed property."""
        invite = UserInvite(**sample_invite_data)
        assert invite.custom_fields.get(1) == "Test"

    def test_frozen_fields(self, sample_invite_data):
        """Test that frozen fields cannot be modified."""
        invite = UserInvite(**sample_invite_data)

        # ID should be frozen
        with pytest.raises(Exception):  # Pydantic raises ValidationError
            invite.id = "new-id"

        # killDate should be frozen
        with pytest.raises(Exception):
            invite.killDate = "2026-01-01"

    def test_email_validation(self, sample_invite_data):
        """Test email field validation."""
        # Valid email
        invite = UserInvite(**sample_invite_data)
        assert invite.email == "john@example.com"

        # Invalid email should raise validation error
        invalid_data = {**sample_invite_data, "email": "not-an-email"}
        with pytest.raises(Exception):  # Pydantic ValidationError
            UserInvite(**invalid_data)


# Coverage check
# Run: uv run pytest tests/unit/test_user_invites_resource.py -v --cov=upsales/resources/user_invites.py --cov-report=term-missing
