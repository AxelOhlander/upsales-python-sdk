"""
Unit tests for RolesResource.

Tests CRUD operations and custom methods for roles endpoint.
"""

import pytest
from pytest_httpx import HTTPXMock

from upsales.http import HTTPClient
from upsales.models.roles import Role
from upsales.resources.roles import RolesResource


class TestRolesResourceCRUD:
    """Test CRUD operations for RolesResource."""

    @pytest.fixture
    def sample_data(self):
        """Sample role data for testing."""
        return {
            "id": 1,
            "name": "Sales Manager",
            "description": "Manages sales team",
            "defaultCurrency": "USD",
            "defaultSalesboardId": 10,
            "template": 1,
            "hasDiscount": True,
            "parent": None,
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
                    "name": "Sales Rep",
                    "hasDiscount": False,
                    "parent": {"id": 1, "name": "Sales Manager"},
                },
            ],
        }

    @pytest.mark.asyncio
    async def test_create(self, httpx_mock: HTTPXMock, sample_data):
        """Test creating a role."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/roles",
            method="POST",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = RolesResource(http)
            result = await resource.create(
                name="Sales Manager",
                description="Manages sales team",
                defaultCurrency="USD",
                template=1,
            )

            assert isinstance(result, Role)
            assert result.id == 1
            assert result.name == "Sales Manager"
            assert result.defaultCurrency == "USD"
            assert result.can_discount

    @pytest.mark.asyncio
    async def test_get(self, httpx_mock: HTTPXMock, sample_data):
        """Test getting a single role."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/roles/1",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = RolesResource(http)
            result = await resource.get(1)

            assert isinstance(result, Role)
            assert result.id == 1
            assert result.name == "Sales Manager"
            assert result.can_discount
            assert not result.has_parent

    @pytest.mark.asyncio
    async def test_list(self, httpx_mock: HTTPXMock, sample_list_response):
        """Test listing roles with pagination."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/roles?limit=10&offset=0",
            json=sample_list_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = RolesResource(http)
            results = await resource.list(limit=10, offset=0)

            assert len(results) == 2
            assert all(isinstance(r, Role) for r in results)
            assert results[0].name == "Sales Manager"
            assert results[1].name == "Sales Rep"

    @pytest.mark.asyncio
    async def test_list_all(self, httpx_mock: HTTPXMock, sample_list_response):
        """Test list_all with auto-pagination."""
        # First page
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/roles?limit=100&offset=0",
            json=sample_list_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = RolesResource(http)
            results = await resource.list_all()

            assert len(results) == 2
            assert all(isinstance(r, Role) for r in results)

    @pytest.mark.asyncio
    async def test_update(self, httpx_mock: HTTPXMock, sample_data):
        """Test updating a role."""
        updated_data = {**sample_data, "name": "Senior Sales Manager", "hasDiscount": False}

        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/roles/1",
            method="PUT",
            json={"error": None, "data": updated_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = RolesResource(http)
            result = await resource.update(1, name="Senior Sales Manager", hasDiscount=False)

            assert isinstance(result, Role)
            assert result.id == 1
            assert result.name == "Senior Sales Manager"
            assert not result.can_discount

    @pytest.mark.asyncio
    async def test_delete(self, httpx_mock: HTTPXMock):
        """Test deleting a role."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/roles/1",
            method="DELETE",
            json={"error": None, "data": {"success": True}},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = RolesResource(http)
            result = await resource.delete(1)

            assert isinstance(result, dict)
            assert result == {"error": None, "data": {"success": True}}

    @pytest.mark.asyncio
    async def test_bulk_update(self, httpx_mock: HTTPXMock, sample_data):
        """Test bulk update operation."""
        # Mock responses for each update
        for i in [1, 2, 3]:
            httpx_mock.add_response(
                url=f"https://power.upsales.com/api/v2/roles/{i}",
                method="PUT",
                json={"error": None, "data": {**sample_data, "id": i, "hasDiscount": False}},
            )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = RolesResource(http)
            results = await resource.bulk_update(
                ids=[1, 2, 3],
                data={"hasDiscount": False},
            )

            assert len(results) == 3
            assert all(isinstance(item, Role) for item in results)
            assert all(not r.can_discount for r in results)

    @pytest.mark.asyncio
    async def test_bulk_delete(self, httpx_mock: HTTPXMock):
        """Test bulk delete operation."""
        # Mock responses for each delete
        for i in [1, 2, 3]:
            httpx_mock.add_response(
                url=f"https://power.upsales.com/api/v2/roles/{i}",
                method="DELETE",
                json={"error": None, "data": {"success": True}},
            )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = RolesResource(http)
            results = await resource.bulk_delete(ids=[1, 2, 3])

            assert len(results) == 3


class TestRolesResourceCustomMethods:
    """Test custom methods specific to RolesResource."""

    @pytest.fixture
    def sample_roles(self):
        """Sample roles for custom method testing."""
        return [
            {
                "id": 1,
                "name": "Sales Manager",
                "description": "Manages sales team",
                "defaultCurrency": "USD",
                "template": 1,
                "hasDiscount": True,
                "parent": None,
                "defaultSalesboardId": None,
            },
            {
                "id": 2,
                "name": "Sales Rep",
                "description": "Sales representative",
                "defaultCurrency": "USD",
                "template": 1,
                "hasDiscount": False,
                "parent": {"id": 1, "name": "Sales Manager"},
                "defaultSalesboardId": None,
            },
            {
                "id": 3,
                "name": "Account Manager",
                "description": "Manages accounts",
                "defaultCurrency": "EUR",
                "template": 2,
                "hasDiscount": True,
                "parent": None,
                "defaultSalesboardId": None,
            },
        ]

    @pytest.mark.asyncio
    async def test_get_by_name(self, httpx_mock: HTTPXMock, sample_roles):
        """Test get_by_name() custom method."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/roles?limit=100&offset=0",
            json={"error": None, "data": sample_roles},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = RolesResource(http)
            result = await resource.get_by_name("Sales Manager")

            assert result is not None
            assert isinstance(result, Role)
            assert result.id == 1
            assert result.name == "Sales Manager"

    @pytest.mark.asyncio
    async def test_get_by_name_not_found(self, httpx_mock: HTTPXMock, sample_roles):
        """Test get_by_name() when role not found."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/roles?limit=100&offset=0",
            json={"error": None, "data": sample_roles},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = RolesResource(http)
            result = await resource.get_by_name("Nonexistent Role")

            assert result is None

    @pytest.mark.asyncio
    async def test_get_with_discounts(self, httpx_mock: HTTPXMock, sample_roles):
        """Test get_with_discounts() custom method."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/roles?limit=100&offset=0",
            json={"error": None, "data": sample_roles},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = RolesResource(http)
            results = await resource.get_with_discounts()

            assert len(results) == 2
            assert all(isinstance(r, Role) for r in results)
            assert all(r.can_discount for r in results)
            assert results[0].name == "Sales Manager"
            assert results[1].name == "Account Manager"

    @pytest.mark.asyncio
    async def test_get_by_currency(self, httpx_mock: HTTPXMock, sample_roles):
        """Test get_by_currency() custom method."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/roles?limit=100&offset=0",
            json={"error": None, "data": sample_roles},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = RolesResource(http)
            results = await resource.get_by_currency("USD")

            assert len(results) == 2
            assert all(isinstance(r, Role) for r in results)
            assert all(r.defaultCurrency == "USD" for r in results)
            assert results[0].name == "Sales Manager"
            assert results[1].name == "Sales Rep"

    @pytest.mark.asyncio
    async def test_get_top_level(self, httpx_mock: HTTPXMock, sample_roles):
        """Test get_top_level() custom method."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/roles?limit=100&offset=0",
            json={"error": None, "data": sample_roles},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = RolesResource(http)
            results = await resource.get_top_level()

            assert len(results) == 2
            assert all(isinstance(r, Role) for r in results)
            assert all(not r.has_parent for r in results)
            assert results[0].name == "Sales Manager"
            assert results[1].name == "Account Manager"
