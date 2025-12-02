"""Unit tests for MarketRejectlist resource."""

import pytest
from pytest_httpx import HTTPXMock

from upsales.http import HTTPClient
from upsales.models.market_rejectlist import MarketRejectlist, PartialMarketRejectlist
from upsales.resources.market_rejectlist import MarketRejectlistsResource


class TestMarketRejectlistsResource:
    """Test MarketRejectlistsResource CRUD operations."""

    @pytest.fixture
    def sample_data(self):
        """Sample market rejectlist entry data."""
        return {
            "id": 1,
            "name": "ACME Corp",
            "dunsNo": "123456789",
            "organisationId": "ORG123",
            "clientId": 456,
        }

    @pytest.fixture
    def sample_list_response(self, sample_data):
        """Sample list response."""
        return {
            "error": None,
            "metadata": {"total": 2, "limit": 100, "offset": 0},
            "data": [
                sample_data,
                {
                    "id": 2,
                    "name": "Widgets Inc",
                    "dunsNo": None,
                    "organisationId": "ORG456",
                    "clientId": None,
                },
            ],
        }

    @pytest.mark.asyncio
    async def test_get(self, httpx_mock: HTTPXMock, sample_data):
        """Test getting a single rejectlist entry."""
        httpx_mock.add_response(
            method="GET",
            url="https://power.upsales.com/api/v2/marketRejectlist/1",
            json={"data": sample_data, "error": None},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = MarketRejectlistsResource(http)
            entry = await resource.get(1)

            assert isinstance(entry, MarketRejectlist)
            assert entry.id == 1
            assert entry.name == "ACME Corp"
            assert entry.dunsNo == "123456789"
            assert entry.organisationId == "ORG123"
            assert entry.clientId == 456

    @pytest.mark.asyncio
    async def test_list(self, httpx_mock: HTTPXMock, sample_list_response):
        """Test listing rejectlist entries with pagination."""
        httpx_mock.add_response(
            method="GET",
            url="https://power.upsales.com/api/v2/marketRejectlist?limit=10&offset=0",
            json=sample_list_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = MarketRejectlistsResource(http)
            entries = await resource.list(limit=10, offset=0)

            assert len(entries) == 2
            assert all(isinstance(e, MarketRejectlist) for e in entries)
            assert entries[0].name == "ACME Corp"
            assert entries[1].name == "Widgets Inc"

    @pytest.mark.asyncio
    async def test_create(self, httpx_mock: HTTPXMock, sample_data):
        """Test creating a new rejectlist entry."""
        httpx_mock.add_response(
            method="POST",
            url="https://power.upsales.com/api/v2/marketRejectlist",
            json={"data": sample_data, "error": None},
            status_code=201,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = MarketRejectlistsResource(http)
            entry = await resource.create(
                name="ACME Corp", dunsNo="123456789", organisationId="ORG123", clientId=456
            )

            assert isinstance(entry, MarketRejectlist)
            assert entry.id == 1
            assert entry.name == "ACME Corp"

    @pytest.mark.asyncio
    async def test_update(self, httpx_mock: HTTPXMock, sample_data):
        """Test updating a rejectlist entry."""
        updated_data = {**sample_data, "name": "Updated Corp"}
        httpx_mock.add_response(
            method="PUT",
            url="https://power.upsales.com/api/v2/marketRejectlist/1",
            json={"data": updated_data, "error": None},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = MarketRejectlistsResource(http)
            entry = await resource.update(1, name="Updated Corp")

            assert isinstance(entry, MarketRejectlist)
            assert entry.name == "Updated Corp"

    @pytest.mark.asyncio
    async def test_delete(self, httpx_mock: HTTPXMock):
        """Test deleting a rejectlist entry."""
        httpx_mock.add_response(
            method="DELETE",
            url="https://power.upsales.com/api/v2/marketRejectlist/1",
            json={"data": None, "error": None},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = MarketRejectlistsResource(http)
            await resource.delete(1)

            # No exception means success


class TestMarketRejectlistModel:
    """Test MarketRejectlist model."""

    @pytest.fixture
    def sample_data(self):
        """Sample market rejectlist entry data."""
        return {
            "id": 1,
            "name": "ACME Corp",
            "dunsNo": "123456789",
            "organisationId": "ORG123",
            "clientId": 456,
        }

    def test_model_creation(self, sample_data):
        """Test creating a MarketRejectlist model instance."""
        entry = MarketRejectlist(**sample_data)

        assert entry.id == 1
        assert entry.name == "ACME Corp"
        assert entry.dunsNo == "123456789"
        assert entry.organisationId == "ORG123"
        assert entry.clientId == 456

    def test_has_identifier_property(self):
        """Test has_identifier computed property."""
        entry_with_name = MarketRejectlist(id=1, name="Test")
        assert entry_with_name.has_identifier is True

        entry_with_duns = MarketRejectlist(id=2, dunsNo="123456789")
        assert entry_with_duns.has_identifier is True

        entry_with_org_id = MarketRejectlist(id=3, organisationId="ORG123")
        assert entry_with_org_id.has_identifier is True

        entry_with_client_id = MarketRejectlist(id=4, clientId=456)
        assert entry_with_client_id.has_identifier is True

        entry_empty = MarketRejectlist(id=5)
        assert entry_empty.has_identifier is False

    def test_frozen_fields(self, sample_data):
        """Test that frozen fields cannot be modified."""
        entry = MarketRejectlist(**sample_data)

        with pytest.raises(ValueError, match="frozen"):
            entry.id = 999

    # Note: edit() and delete() methods require full Upsales client setup
    # These are tested in integration tests


class TestPartialMarketRejectlist:
    """Test PartialMarketRejectlist model."""

    @pytest.fixture
    def sample_data(self):
        """Sample full market rejectlist entry data."""
        return {
            "id": 1,
            "name": "ACME Corp",
            "dunsNo": "123456789",
            "organisationId": "ORG123",
            "clientId": 456,
        }

    def test_partial_model_creation(self):
        """Test creating a PartialMarketRejectlist instance."""
        partial = PartialMarketRejectlist(id=1, name="ACME Corp")

        assert partial.id == 1
        assert partial.name == "ACME Corp"

    # Note: fetch_full(), edit(), and delete() methods require full Upsales client setup
    # These are tested in integration tests
