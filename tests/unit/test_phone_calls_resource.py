"""
Unit tests for PhoneCallsResource.

Tests CRUD operations for phone call endpoint without making real API calls.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from upsales.http import HTTPClient
from upsales.models.phone_call import PartialPhoneCall, PhoneCall
from upsales.resources.phone_calls import PhoneCallsResource


@pytest.fixture
def mock_http():
    """Create mock HTTP client."""
    http = MagicMock(spec=HTTPClient)
    http.get = AsyncMock()
    http.post = AsyncMock()
    http.put = AsyncMock()
    http.delete = AsyncMock()
    http._upsales_client = None  # Mock the _upsales_client attribute
    return http


@pytest.fixture
def resource(mock_http):
    """Create PhoneCallsResource with mock HTTP client."""
    return PhoneCallsResource(mock_http)


@pytest.fixture
def sample_phone_call_data():
    """Sample phone call API response data."""
    return {
        "id": 1,
        "durationInS": 180,
        "user": {"id": 10, "name": "John Doe", "email": "john.doe@example.com"},
        "type": "Outbound",
        "conversationUrl": "https://recording.example.com/call123",
        "contact": {"id": 100, "name": "Jane Smith"},
        "date": "2025-01-15 10:30:00",
        "status": 1,
        "phoneNumber": "+1234567890",
        "related": [],
        "client": {"id": 50, "name": "Acme Corp"},
        "externalId": "ext-123",
    }


class TestPhoneCallsResource:
    """Test suite for PhoneCallsResource."""

    @pytest.mark.asyncio
    async def test_create_phone_call(self, resource, mock_http, sample_phone_call_data):
        """Test creating a phone call."""
        mock_http.post.return_value = {"data": sample_phone_call_data}

        result = await resource.create(
            user={"id": 10},
            contact={"id": 100},
            client={"id": 50},
            durationInS=180,
            phoneNumber="+1234567890",
        )

        assert isinstance(result, PhoneCall)
        assert result.id == 1
        assert result.durationInS == 180
        assert result.phoneNumber == "+1234567890"
        assert result.user.id == 10
        assert result.contact.id == 100
        assert result.client.id == 50

        mock_http.post.assert_called_once_with(
            "/phoneCall",
            user={"id": 10},
            contact={"id": 100},
            client={"id": 50},
            durationInS=180,
            phoneNumber="+1234567890",
        )

    @pytest.mark.asyncio
    async def test_get_phone_call(self, resource, mock_http, sample_phone_call_data):
        """Test getting a single phone call."""
        mock_http.get.return_value = {"data": sample_phone_call_data}

        result = await resource.get(1)

        assert isinstance(result, PhoneCall)
        assert result.id == 1
        assert result.durationInS == 180
        assert result.type == "Outbound"

        mock_http.get.assert_called_once_with("/phoneCall/1")

    @pytest.mark.asyncio
    async def test_list_phone_calls(self, resource, mock_http, sample_phone_call_data):
        """Test listing phone calls."""
        mock_http.get.return_value = {
            "data": [sample_phone_call_data],
            "metadata": {"total": 1, "limit": 100, "offset": 0},
        }

        results = await resource.list(limit=10)

        assert len(results) == 1
        assert isinstance(results[0], PhoneCall)
        assert results[0].id == 1

        mock_http.get.assert_called_once_with("/phoneCall", limit=10, offset=0)

    @pytest.mark.asyncio
    async def test_update_phone_call(self, resource, mock_http, sample_phone_call_data):
        """Test updating a phone call."""
        updated_data = {**sample_phone_call_data, "status": 2, "durationInS": 300}
        mock_http.put.return_value = {"data": updated_data}

        result = await resource.update(1, status=2, durationInS=300)

        assert isinstance(result, PhoneCall)
        assert result.id == 1
        assert result.status == 2
        assert result.durationInS == 300

        mock_http.put.assert_called_once_with("/phoneCall/1", status=2, durationInS=300)

    @pytest.mark.asyncio
    async def test_delete_phone_call(self, resource, mock_http):
        """Test deleting a phone call."""
        mock_http.delete.return_value = None

        await resource.delete(1)

        mock_http.delete.assert_called_once_with("/phoneCall/1")

    @pytest.mark.asyncio
    async def test_search_phone_calls(self, resource, mock_http, sample_phone_call_data):
        """Test searching phone calls."""
        mock_http.get.return_value = {
            "data": [sample_phone_call_data],
            "metadata": {"total": 1, "limit": 100, "offset": 0},
        }

        results = await resource.search(user__id=10)

        assert len(results) == 1
        assert results[0].user.id == 10

        mock_http.get.assert_called_once_with("/phoneCall", user__id=10, limit=100, offset=0)


class TestPhoneCallModel:
    """Test suite for PhoneCall model."""

    def test_phone_call_creation(self, sample_phone_call_data):
        """Test creating PhoneCall instance."""
        call = PhoneCall(**sample_phone_call_data)

        assert call.id == 1
        assert call.durationInS == 180
        assert call.phoneNumber == "+1234567890"
        assert call.type == "Outbound"
        assert call.status == 1
        assert call.conversationUrl == "https://recording.example.com/call123"
        assert call.externalId == "ext-123"

    def test_phone_call_frozen_id(self, sample_phone_call_data):
        """Test that ID is frozen (read-only)."""
        call = PhoneCall(**sample_phone_call_data)

        with pytest.raises(Exception):  # Pydantic will raise validation error
            call.id = 999

    def test_phone_call_defaults(self):
        """Test PhoneCall with default values."""
        call = PhoneCall(
            id=1,
            user={"id": 10, "name": "John", "email": "john.doe@example.com"},
            contact={"id": 100, "name": "Jane"},
            client={"id": 50, "name": "Acme"},
        )

        assert call.id == 1
        assert call.durationInS == 0
        assert call.phoneNumber == ""
        assert call.date == ""
        assert call.type == ""
        assert call.status == 0
        assert call.conversationUrl is None
        assert call.externalId == ""
        assert call.related == []


class TestPartialPhoneCallModel:
    """Test suite for PartialPhoneCall model."""

    def test_partial_phone_call_creation(self):
        """Test creating PartialPhoneCall instance."""
        partial = PartialPhoneCall(id=1)

        assert partial.id == 1

    @pytest.mark.asyncio
    async def test_fetch_full_no_client(self):
        """Test fetch_full raises error without client."""
        partial = PartialPhoneCall(id=1)

        with pytest.raises(RuntimeError, match="No client available"):
            await partial.fetch_full()

    @pytest.mark.asyncio
    async def test_edit_no_client(self):
        """Test edit raises error without client."""
        partial = PartialPhoneCall(id=1)

        with pytest.raises(RuntimeError, match="No client available"):
            await partial.edit(status=1)


class TestPhoneCallModelMethods:
    """Test suite for PhoneCall model methods."""

    @pytest.mark.asyncio
    async def test_edit_no_client(self, sample_phone_call_data):
        """Test edit raises error without client."""
        call = PhoneCall(**sample_phone_call_data)

        with pytest.raises(RuntimeError, match="No client available"):
            await call.edit(status=2)

    def test_to_api_dict_excludes_frozen_fields(self, sample_phone_call_data):
        """Test to_api_dict excludes frozen fields."""
        call = PhoneCall(**sample_phone_call_data)

        # Update some fields
        call.status = 2
        call.durationInS = 300

        api_dict = call.to_api_dict()

        # Should NOT include frozen id
        assert "id" not in api_dict

        # Should include updated fields
        assert api_dict["status"] == 2
        assert api_dict["durationInS"] == 300

    def test_to_api_dict_with_overrides(self, sample_phone_call_data):
        """Test to_api_dict with override parameters."""
        call = PhoneCall(**sample_phone_call_data)

        api_dict = call.to_api_dict(status=3, conversationUrl="https://new-url.com")

        assert api_dict["status"] == 3
        assert api_dict["conversationUrl"] == "https://new-url.com"
        assert "id" not in api_dict
