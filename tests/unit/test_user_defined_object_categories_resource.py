"""Unit tests for UserDefinedObjectCategoriesResource.

Tests CRUD operations for the user defined object categories endpoint.
Note that all operations require a 'nr' parameter (1-4) to specify the variant.
"""

import pytest
from pytest_httpx import HTTPXMock

from upsales.http import HTTPClient
from upsales.models.user_defined_object_categories import UserDefinedObjectCategory
from upsales.resources.user_defined_object_categories import (
    UserDefinedObjectCategoriesResource,
)


class TestUserDefinedObjectCategoriesResourceCRUD:
    """Test CRUD operations for UserDefinedObjectCategoriesResource."""

    @pytest.fixture
    def sample_data(self):
        """Sample category data for testing."""
        return {
            "id": 1,
            "name": "Priority Customers",
            "categoryTypeId": 5,
        }

    @pytest.fixture
    def sample_list_response(self, sample_data):
        """Sample list response."""
        return {
            "error": None,
            "metadata": {"total": 3, "limit": 100, "offset": 0},
            "data": [
                sample_data,
                {**sample_data, "id": 2, "name": "VIP Customers", "categoryTypeId": 6},
                {**sample_data, "id": 3, "name": "Standard Customers", "categoryTypeId": 7},
            ],
        }

    @pytest.mark.asyncio
    async def test_create(self, httpx_mock: HTTPXMock, sample_data):
        """Test creating a category."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/userDefinedObjectCategories/1",
            method="POST",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UserDefinedObjectCategoriesResource(http)
            result = await resource.create(nr=1, name="Priority Customers", categoryTypeId=5)

            assert isinstance(result, UserDefinedObjectCategory)
            assert result.id == 1
            assert result.name == "Priority Customers"
            assert result.categoryTypeId == 5

    @pytest.mark.asyncio
    async def test_create_invalid_nr(self, httpx_mock: HTTPXMock):
        """Test creating with invalid nr raises ValueError."""
        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UserDefinedObjectCategoriesResource(http)
            with pytest.raises(ValueError, match="nr must be 1, 2, 3, or 4"):
                await resource.create(nr=5, name="Test", categoryTypeId=1)

    @pytest.mark.asyncio
    async def test_get(self, httpx_mock: HTTPXMock, sample_data):
        """Test getting a single category."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/userDefinedObjectCategories/1/1",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UserDefinedObjectCategoriesResource(http)
            result = await resource.get(1, nr=1)

            assert isinstance(result, UserDefinedObjectCategory)
            assert result.id == 1
            assert result.name == "Priority Customers"
            assert result.categoryTypeId == 5

    @pytest.mark.asyncio
    async def test_get_invalid_nr(self, httpx_mock: HTTPXMock):
        """Test getting with invalid nr raises ValueError."""
        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UserDefinedObjectCategoriesResource(http)
            with pytest.raises(ValueError, match="nr must be 1, 2, 3, or 4"):
                await resource.get(1, nr=0)

    @pytest.mark.asyncio
    async def test_list(self, httpx_mock: HTTPXMock, sample_list_response):
        """Test listing categories with pagination."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/userDefinedObjectCategories/1?limit=10&offset=0",
            json=sample_list_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UserDefinedObjectCategoriesResource(http)
            results = await resource.list(nr=1, limit=10, offset=0)

            assert isinstance(results, list)
            assert len(results) == 3
            assert all(isinstance(item, UserDefinedObjectCategory) for item in results)

    @pytest.mark.asyncio
    async def test_list_invalid_nr(self, httpx_mock: HTTPXMock):
        """Test listing with invalid nr raises ValueError."""
        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UserDefinedObjectCategoriesResource(http)
            with pytest.raises(ValueError, match="nr must be 1, 2, 3, or 4"):
                await resource.list(nr=10)

    @pytest.mark.asyncio
    async def test_list_all_single_page(self, httpx_mock: HTTPXMock, sample_data):
        """Test list_all with single page of results."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/userDefinedObjectCategories/1?limit=100&offset=0",
            json={
                "error": None,
                "metadata": {"total": 1, "limit": 100, "offset": 0},
                "data": [sample_data],
            },
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UserDefinedObjectCategoriesResource(http)
            results = await resource.list_all(nr=1)

            assert len(results) == 1
            assert len(httpx_mock.get_requests()) == 1

    @pytest.mark.asyncio
    async def test_list_all_multi_page(self, httpx_mock: HTTPXMock, sample_data):
        """Test list_all with multiple pages."""
        # Page 1: full batch (100 items triggers next page)
        page1_data = [sample_data] * 100
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/userDefinedObjectCategories/2?limit=100&offset=0",
            json={"error": None, "data": page1_data},
        )
        # Page 2: partial batch (last page)
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/userDefinedObjectCategories/2?limit=100&offset=100",
            json={"error": None, "data": [sample_data, sample_data]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UserDefinedObjectCategoriesResource(http)
            results = await resource.list_all(nr=2)

            assert len(results) == 102
            assert len(httpx_mock.get_requests()) == 2

    @pytest.mark.asyncio
    async def test_update(self, httpx_mock: HTTPXMock, sample_data):
        """Test updating a category."""
        updated_data = {**sample_data, "name": "Updated VIP Customers"}
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/userDefinedObjectCategories/1/1",
            method="PUT",
            json={"error": None, "data": updated_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UserDefinedObjectCategoriesResource(http)
            result = await resource.update(1, nr=1, name="Updated VIP Customers")

            assert isinstance(result, UserDefinedObjectCategory)
            assert result.name == "Updated VIP Customers"

    @pytest.mark.asyncio
    async def test_update_invalid_nr(self, httpx_mock: HTTPXMock):
        """Test updating with invalid nr raises ValueError."""
        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UserDefinedObjectCategoriesResource(http)
            with pytest.raises(ValueError, match="nr must be 1, 2, 3, or 4"):
                await resource.update(1, nr=100, name="Test")

    @pytest.mark.asyncio
    async def test_delete(self, httpx_mock: HTTPXMock):
        """Test deleting a category."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/userDefinedObjectCategories/1/1",
            method="DELETE",
            json={"error": None, "data": None},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UserDefinedObjectCategoriesResource(http)
            await resource.delete(1, nr=1)

            requests = httpx_mock.get_requests()
            assert len(requests) == 1
            assert requests[0].method == "DELETE"

    @pytest.mark.asyncio
    async def test_delete_invalid_nr(self, httpx_mock: HTTPXMock):
        """Test deleting with invalid nr raises ValueError."""
        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = UserDefinedObjectCategoriesResource(http)
            with pytest.raises(ValueError, match="nr must be 1, 2, 3, or 4"):
                await resource.delete(1, nr=-1)


class TestUserDefinedObjectCategoryModel:
    """Test UserDefinedObjectCategory model validation."""

    def test_model_validation(self):
        """Test creating a valid model instance."""
        category = UserDefinedObjectCategory(id=1, name="Priority Customers", categoryTypeId=5)

        assert category.id == 1
        assert category.name == "Priority Customers"
        assert category.categoryTypeId == 5

    def test_name_max_length_validation(self):
        """Test name max length validation."""
        with pytest.raises(ValueError, match="name must not exceed 64 characters"):
            UserDefinedObjectCategory(
                id=1,
                name="A" * 65,
                categoryTypeId=5,  # 65 characters
            )

    def test_name_empty_validation(self):
        """Test empty name validation."""
        with pytest.raises(ValueError):
            UserDefinedObjectCategory(id=1, name="", categoryTypeId=5)

    def test_name_whitespace_stripping(self):
        """Test that name whitespace is stripped."""
        category = UserDefinedObjectCategory(id=1, name="  Test Category  ", categoryTypeId=5)
        assert category.name == "Test Category"

    def test_id_positive_validation(self):
        """Test that id must be positive."""
        with pytest.raises(ValueError):
            UserDefinedObjectCategory(id=-1, name="Test", categoryTypeId=5)

    def test_category_type_id_positive_validation(self):
        """Test that categoryTypeId must be positive."""
        with pytest.raises(ValueError):
            UserDefinedObjectCategory(id=1, name="Test", categoryTypeId=-1)
