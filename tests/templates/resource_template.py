"""
Template for testing resource managers.

INSTRUCTIONS:
1. Copy this file to tests/unit/test_{resource_name}_resource.py
2. Replace placeholders:
   - {ResourceName} → Resource class name (e.g., ContactsResource)
   - {ModelName} → Model class name (e.g., Contact)
   - {PartialModelName} → Partial model class (e.g., PartialContact)
   - {endpoint} → API endpoint (e.g., /contacts)
   - {resource_name} → Resource name in client (e.g., contacts)
3. Fill in sample_data with actual field values
4. Add tests for custom methods (if any)
5. Run: uv run pytest tests/unit/test_{resource_name}_resource.py -v

This template ensures complete CRUD coverage for all resources.
"""

import pytest
from pytest_httpx import HTTPXMock

from upsales import Upsales
from upsales.http import HTTPClient
# from upsales.models.{model_file} import {ModelName}, {PartialModelName}
# from upsales.resources.{resource_file} import {ResourceName}


class Test{ResourceName}CRUD:
    """Test CRUD operations for {ResourceName}."""

    @pytest.fixture
    def sample_data(self):
        """Sample {model_name} data for testing."""
        return {
            "id": 1,
            "name": "Test {ModelName}",
            # Add all required fields here
            # "active": 1,
            # "email": "test@example.com",
            # ...
        }

    @pytest.fixture
    def sample_list_response(self, sample_data):
        """Sample list response."""
        return {
            "error": None,
            "metadata": {"total": 2, "limit": 100, "offset": 0},
            "data": [
                sample_data,
                {**sample_data, "id": 2, "name": "Test {ModelName} 2"},
            ],
        }

    @pytest.mark.asyncio
    async def test_create(self, httpx_mock: HTTPXMock, sample_data):
        """Test creating a {model_name}."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/{endpoint}",
            method="POST",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            # resource = {ResourceName}(http)
            # result = await resource.create(name="Test {ModelName}")
            pass

            # assert isinstance(result, {ModelName})
            # assert result.id == 1
            # assert result.name == "Test {ModelName}"

    @pytest.mark.asyncio
    async def test_get(self, httpx_mock: HTTPXMock, sample_data):
        """Test getting a single {model_name}."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/{endpoint}/1",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            # resource = {ResourceName}(http)
            # result = await resource.get(1)
            pass

            # assert isinstance(result, {ModelName})
            # assert result.id == 1

    @pytest.mark.asyncio
    async def test_list(self, httpx_mock: HTTPXMock, sample_list_response):
        """Test listing {resource_name} with pagination."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/{endpoint}?limit=10&offset=0",
            json=sample_list_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            # resource = {ResourceName}(http)
            # results = await resource.list(limit=10, offset=0)
            pass

            # assert isinstance(results, list)
            # assert len(results) == 2
            # assert all(isinstance(item, {ModelName}) for item in results)

    @pytest.mark.asyncio
    async def test_list_all_single_page(self, httpx_mock: HTTPXMock, sample_data):
        """Test list_all with single page of results."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/{endpoint}?limit=100&offset=0",
            json={
                "error": None,
                "metadata": {"total": 50, "limit": 100, "offset": 0},
                "data": [sample_data],  # Less than batch_size
            },
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            # resource = {ResourceName}(http)
            # results = await resource.list_all()
            pass

            # assert len(results) == 1
            # Should only make 1 request since results < batch_size
            # assert len(httpx_mock.get_requests()) == 1

    @pytest.mark.asyncio
    async def test_list_all_multi_page(self, httpx_mock: HTTPXMock, sample_data):
        """Test list_all with multiple pages."""
        # Page 1: full batch
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/{endpoint}?limit=2&offset=0",
            json={"error": None, "data": [sample_data, sample_data]},
        )
        # Page 2: partial batch (last page)
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/{endpoint}?limit=2&offset=2",
            json={"error": None, "data": [sample_data]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            # resource = {ResourceName}(http)
            # results = await resource.list_all(batch_size=2)
            pass

            # assert len(results) == 3
            # assert len(httpx_mock.get_requests()) == 2

    @pytest.mark.asyncio
    async def test_search(self, httpx_mock: HTTPXMock, sample_data):
        """Test search with filters."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/{endpoint}?active=1&limit=100&offset=0",
            json={"error": None, "data": [sample_data]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            # resource = {ResourceName}(http)
            # results = await resource.search(active=1)
            pass

            # assert len(results) == 1

    @pytest.mark.asyncio
    async def test_update(self, httpx_mock: HTTPXMock, sample_data):
        """Test updating a {model_name}."""
        updated_data = {**sample_data, "name": "Updated Name"}
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/{endpoint}/1",
            method="PUT",
            json={"error": None, "data": updated_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            # resource = {ResourceName}(http)
            # result = await resource.update(1, name="Updated Name")
            pass

            # assert result.name == "Updated Name"

    @pytest.mark.asyncio
    async def test_delete(self, httpx_mock: HTTPXMock):
        """Test deleting a {model_name}."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/{endpoint}/1",
            method="DELETE",
            json={"error": None, "data": {"success": True}},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            # resource = {ResourceName}(http)
            # result = await resource.delete(1)
            pass

            # assert result.get("success") is True

    @pytest.mark.asyncio
    async def test_bulk_update(self, httpx_mock: HTTPXMock, sample_data):
        """Test bulk update operation."""
        # Mock responses for each update
        for i in [1, 2, 3]:
            httpx_mock.add_response(
                url=f"https://power.upsales.com/api/v2/{{endpoint}}/{i}",
                method="PUT",
                json={"error": None, "data": {**sample_data, "id": i}},
            )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            # resource = {ResourceName}(http)
            # results = await resource.bulk_update(
            #     ids=[1, 2, 3],
            #     data={"active": 0},
            # )
            pass

            # assert len(results) == 3
            # assert all(isinstance(item, {ModelName}) for item in results)

    @pytest.mark.asyncio
    async def test_bulk_delete(self, httpx_mock: HTTPXMock):
        """Test bulk delete operation."""
        # Mock responses for each delete
        for i in [1, 2, 3]:
            httpx_mock.add_response(
                url=f"https://power.upsales.com/api/v2/{{endpoint}}/{i}",
                method="DELETE",
                json={"error": None, "data": {"success": True}},
            )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            # resource = {ResourceName}(http)
            # results = await resource.bulk_delete(ids=[1, 2, 3])
            pass

            # assert len(results) == 3


# OPTIONAL: Add tests for custom methods
class Test{ResourceName}CustomMethods:
    """Test custom methods specific to {ResourceName}."""

    # Example:
    # @pytest.mark.asyncio
    # async def test_get_active(self, httpx_mock: HTTPXMock):
    #     """Test get_active() custom method."""
    #     httpx_mock.add_response(
    #         url="https://power.upsales.com/api/v2/{endpoint}?active=1&limit=100&offset=0",
    #         json={"error": None, "data": [...]},
    #     )
    #
    #     async with HTTPClient(token="test_token", auth_manager=None) as http:
    #         resource = {ResourceName}(http)
    #         results = await resource.get_active()
    #         assert all(item.active == 1 for item in results)

    pass


# Coverage target: 85%+ for all resource managers
# Run: uv run pytest tests/unit/test_{resource_name}_resource.py -v --cov=upsales/resources/{resource_name}.py
