"""
Unit tests for ApikeysResource.

Tests CRUD operations and custom methods for the API keys endpoint.
"""

import pytest
from pytest_httpx import HTTPXMock

from upsales.http import HTTPClient
from upsales.models.api_keys import ApiKey
from upsales.resources.api_keys import ApikeysResource


class TestApikeysResourceCRUD:
    """Test CRUD operations for ApikeysResource."""

    @pytest.fixture
    def sample_data(self):
        """Sample API key data for testing."""
        return {
            "id": 1,
            "name": "Production API Key",
            "active": True,
        }

    @pytest.fixture
    def sample_list_response(self, sample_data):
        """Sample list response."""
        return {
            "error": None,
            "metadata": {"total": 3, "limit": 100, "offset": 0},
            "data": [
                sample_data,
                {**sample_data, "id": 2, "name": "Test API Key", "active": False},
                {**sample_data, "id": 3, "name": "Development API Key", "active": True},
            ],
        }

    @pytest.mark.asyncio
    async def test_create(self, httpx_mock: HTTPXMock, sample_data):
        """Test creating an API key."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/apiKeys",
            method="POST",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ApikeysResource(http)
            result = await resource.create(name="Production API Key", active=True)

            assert isinstance(result, ApiKey)
            assert result.id == 1
            assert result.name == "Production API Key"
            assert result.is_active

    @pytest.mark.asyncio
    async def test_get(self, httpx_mock: HTTPXMock, sample_data):
        """Test getting a single API key."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/apiKeys/1",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ApikeysResource(http)
            result = await resource.get(1)

            assert isinstance(result, ApiKey)
            assert result.id == 1
            assert result.name == "Production API Key"
            assert result.is_active

    @pytest.mark.asyncio
    async def test_list(self, httpx_mock: HTTPXMock, sample_list_response):
        """Test listing API keys with pagination."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/apiKeys?limit=10&offset=0",
            json=sample_list_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ApikeysResource(http)
            results = await resource.list(limit=10, offset=0)

            assert isinstance(results, list)
            assert len(results) == 3
            assert all(isinstance(item, ApiKey) for item in results)

    @pytest.mark.asyncio
    async def test_list_all_single_page(self, httpx_mock: HTTPXMock, sample_data):
        """Test list_all with single page of results."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/apiKeys?limit=100&offset=0",
            json={
                "error": None,
                "metadata": {"total": 1, "limit": 100, "offset": 0},
                "data": [sample_data],
            },
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ApikeysResource(http)
            results = await resource.list_all()

            assert len(results) == 1
            assert len(httpx_mock.get_requests()) == 1

    @pytest.mark.asyncio
    async def test_list_all_multi_page(self, httpx_mock: HTTPXMock, sample_data):
        """Test list_all with multiple pages."""
        # Page 1: full batch
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/apiKeys?limit=2&offset=0",
            json={"error": None, "data": [sample_data, sample_data]},
        )
        # Page 2: partial batch (last page)
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/apiKeys?limit=2&offset=2",
            json={"error": None, "data": [sample_data]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ApikeysResource(http)
            results = await resource.list_all(batch_size=2)

            assert len(results) == 3
            assert len(httpx_mock.get_requests()) == 2

    @pytest.mark.asyncio
    async def test_update(self, httpx_mock: HTTPXMock, sample_data):
        """Test updating an API key."""
        updated_data = {**sample_data, "name": "Updated API Key"}
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/apiKeys/1",
            method="PUT",
            json={"error": None, "data": updated_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ApikeysResource(http)
            result = await resource.update(1, name="Updated API Key")

            assert isinstance(result, ApiKey)
            assert result.name == "Updated API Key"

    @pytest.mark.asyncio
    async def test_delete(self, httpx_mock: HTTPXMock):
        """Test deleting an API key."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/apiKeys/1",
            method="DELETE",
            json={"error": None, "data": {"success": True}},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ApikeysResource(http)
            await resource.delete(1)

            requests = httpx_mock.get_requests()
            assert len(requests) == 1
            assert requests[0].method == "DELETE"


class TestApikeysResourceCustomMethods:
    """Test custom methods for ApikeysResource."""

    @pytest.fixture
    def sample_apikeys(self):
        """Sample API keys data."""
        return [
            {"id": 1, "name": "Production", "active": True},
            {"id": 2, "name": "Staging", "active": False},
            {"id": 3, "name": "Development", "active": True},
            {"id": 4, "name": "Testing", "active": False},
        ]

    @pytest.mark.asyncio
    async def test_get_active(self, httpx_mock: HTTPXMock, sample_apikeys):
        """Test getting all active API keys."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/apiKeys?limit=100&offset=0",
            json={"error": None, "data": sample_apikeys},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ApikeysResource(http)
            active = await resource.get_active()

            assert len(active) == 2  # Only active=True
            assert all(key.is_active for key in active)
            assert active[0].name == "Production"
            assert active[1].name == "Development"

    @pytest.mark.asyncio
    async def test_get_inactive(self, httpx_mock: HTTPXMock, sample_apikeys):
        """Test getting all inactive API keys."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/apiKeys?limit=100&offset=0",
            json={"error": None, "data": sample_apikeys},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ApikeysResource(http)
            inactive = await resource.get_inactive()

            assert len(inactive) == 2  # Only active=False
            assert all(not key.is_active for key in inactive)
            assert inactive[0].name == "Staging"
            assert inactive[1].name == "Testing"

    @pytest.mark.asyncio
    async def test_get_by_name(self, httpx_mock: HTTPXMock, sample_apikeys):
        """Test getting API key by name."""
        # Add two responses since we call list_all twice
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/apiKeys?limit=100&offset=0",
            json={"error": None, "data": sample_apikeys},
        )
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/apiKeys?limit=100&offset=0",
            json={"error": None, "data": sample_apikeys},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ApikeysResource(http)

            # Test exact match (case-insensitive)
            apikey = await resource.get_by_name("Production")
            assert apikey is not None
            assert apikey.name == "Production"

            # Test case-insensitive
            apikey = await resource.get_by_name("production")
            assert apikey is not None
            assert apikey.name == "Production"

    @pytest.mark.asyncio
    async def test_get_by_name_not_found(self, httpx_mock: HTTPXMock, sample_apikeys):
        """Test getting API key by name when not found."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/apiKeys?limit=100&offset=0",
            json={"error": None, "data": sample_apikeys},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ApikeysResource(http)
            apikey = await resource.get_by_name("Nonexistent Key")
            assert apikey is None
