"""
Unit tests for UserDefinedObject4Resource.

Tests CRUD operations for user-defined objects (slot 4) endpoint.
"""

import pytest
from pytest_httpx import HTTPXMock

from upsales.http import HTTPClient
from upsales.models.user_defined_object_4 import UserDefinedObject4
from upsales.resources.user_defined_object_4 import UserDefinedObject4Resource


class TestUserDefinedObject4ResourceCRUD:
    """Test CRUD operations for UserDefinedObject4Resource."""

    @pytest.fixture
    def sample_data(self):
        """Sample user-defined object data for testing."""
        return {
            "id": 1,
            "notes": "Main notes",
            "notes1": "Additional notes 1",
            "notes2": "Additional notes 2",
            "notes3": "Additional notes 3",
            "notes4": "Additional notes 4",
            "clientId": 10,
            "contactId": 20,
            "projectId": 30,
            "userId": 5,
            "roleId": 2,
            "regDate": "2025-01-01",
            "regTime": "10:00:00",
            "modDate": "2025-01-02",
            "modTime": "11:00:00",
            "custom": [{"fieldId": 11, "value": "test_value"}],
            "categories": [{"id": 1, "name": "Category 1"}],
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
                    **sample_data,
                    "id": 2,
                    "notes": "Second object",
                    "clientId": 15,
                },
            ],
        }

    @pytest.mark.asyncio
    async def test_create(self, httpx_mock: HTTPXMock, sample_data):
        """Test creating a user-defined object."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/userDefinedObjects/4",
            method="POST",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UserDefinedObject4Resource(http)
            result = await resource.create(
                notes="Main notes",
                clientId=10,
                userId=5,
            )

            assert isinstance(result, UserDefinedObject4)
            assert result.id == 1
            assert result.notes == "Main notes"
            assert result.clientId == 10
            assert result.userId == 5

    @pytest.mark.asyncio
    async def test_get(self, httpx_mock: HTTPXMock, sample_data):
        """Test getting a single user-defined object."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/userDefinedObjects/4/1",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UserDefinedObject4Resource(http)
            result = await resource.get(1)

            assert isinstance(result, UserDefinedObject4)
            assert result.id == 1
            assert result.notes == "Main notes"
            assert result.clientId == 10
            assert result.contactId == 20
            assert result.projectId == 30

    @pytest.mark.asyncio
    async def test_list(self, httpx_mock: HTTPXMock, sample_list_response):
        """Test listing user-defined objects with pagination."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/userDefinedObjects/4?limit=10&offset=0",
            json=sample_list_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UserDefinedObject4Resource(http)
            results = await resource.list(limit=10, offset=0)

            assert len(results) == 2
            assert all(isinstance(r, UserDefinedObject4) for r in results)
            assert results[0].notes == "Main notes"
            assert results[1].notes == "Second object"

    @pytest.mark.asyncio
    async def test_list_all(self, httpx_mock: HTTPXMock, sample_list_response):
        """Test list_all with auto-pagination."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/userDefinedObjects/4?limit=100&offset=0",
            json=sample_list_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UserDefinedObject4Resource(http)
            results = await resource.list_all()

            assert len(results) == 2
            assert all(isinstance(r, UserDefinedObject4) for r in results)

    @pytest.mark.asyncio
    async def test_update(self, httpx_mock: HTTPXMock, sample_data):
        """Test updating a user-defined object."""
        updated_data = {**sample_data, "notes": "Updated notes", "clientId": 25}

        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/userDefinedObjects/4/1",
            method="PUT",
            json={"error": None, "data": updated_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UserDefinedObject4Resource(http)
            result = await resource.update(1, notes="Updated notes", clientId=25)

            assert isinstance(result, UserDefinedObject4)
            assert result.id == 1
            assert result.notes == "Updated notes"
            assert result.clientId == 25

    @pytest.mark.asyncio
    async def test_delete(self, httpx_mock: HTTPXMock):
        """Test deleting a user-defined object."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/userDefinedObjects/4/1",
            method="DELETE",
            json={"error": None, "data": {"success": True}},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UserDefinedObject4Resource(http)
            result = await resource.delete(1)

            assert isinstance(result, dict)
            assert result == {"error": None, "data": {"success": True}}

    @pytest.mark.asyncio
    async def test_bulk_update(self, httpx_mock: HTTPXMock, sample_data):
        """Test bulk update operation."""
        for i in [1, 2, 3]:
            httpx_mock.add_response(
                url=f"https://power.upsales.com/api/v2/userDefinedObjects/4/{i}",
                method="PUT",
                json={"error": None, "data": {**sample_data, "id": i, "notes": "Bulk updated"}},
            )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UserDefinedObject4Resource(http)
            results = await resource.bulk_update(
                ids=[1, 2, 3],
                data={"notes": "Bulk updated"},
            )

            assert len(results) == 3
            assert all(isinstance(item, UserDefinedObject4) for item in results)
            assert all(r.notes == "Bulk updated" for r in results)

    @pytest.mark.asyncio
    async def test_bulk_delete(self, httpx_mock: HTTPXMock):
        """Test bulk delete operation."""
        for i in [1, 2, 3]:
            httpx_mock.add_response(
                url=f"https://power.upsales.com/api/v2/userDefinedObjects/4/{i}",
                method="DELETE",
                json={"error": None, "data": {"success": True}},
            )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UserDefinedObject4Resource(http)
            results = await resource.bulk_delete(ids=[1, 2, 3])

            assert len(results) == 3

    @pytest.mark.asyncio
    async def test_custom_fields_access(self, httpx_mock: HTTPXMock, sample_data):
        """Test accessing custom fields via computed field."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/userDefinedObjects/4/1",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UserDefinedObject4Resource(http)
            result = await resource.get(1)

            # Test accessing custom fields
            assert result.custom_fields.get(11) == "test_value"
            assert len(result.custom) == 1
            assert result.custom[0]["fieldId"] == 11
