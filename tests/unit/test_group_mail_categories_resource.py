"""Unit tests for GroupMailCategoriesResource.

Tests CRUD operations for group mail categories endpoint.
"""

import pytest
from pytest_httpx import HTTPXMock

from upsales.http import HTTPClient
from upsales.models.group_mail_categories import GroupMailCategory
from upsales.resources.group_mail_categories import GroupMailCategoriesResource


class TestGroupMailCategoriesResourceCRUD:
    """Test CRUD operations for GroupMailCategoriesResource."""

    @pytest.fixture
    def sample_data(self):
        """Sample group mail category data for testing."""
        return {
            "id": 1,
            "title": "Newsletter Category",
            "description": "Monthly newsletters",
            "active": 1,
            "languages": ["en", "sv"],
            "relatedMailCampaigns": [101, 102, 103],
        }

    @pytest.fixture
    def sample_list_response(self, sample_data):
        """Sample list response."""
        return {
            "error": None,
            "metadata": {"total": 2, "limit": 100, "offset": 0},
            "data": [
                sample_data,
                {**sample_data, "id": 2, "title": "Promotional Category"},
            ],
        }

    @pytest.mark.asyncio
    async def test_create(self, httpx_mock: HTTPXMock, sample_data):
        """Test creating a group mail category."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/groupMailCategories",
            method="POST",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = GroupMailCategoriesResource(http)
            result = await resource.create(
                title="Newsletter Category",
                description="Monthly newsletters",
                active=1,
                languages=["en", "sv"],
            )

            assert isinstance(result, GroupMailCategory)
            assert result.id == 1
            assert result.title == "Newsletter Category"
            assert result.description == "Monthly newsletters"
            assert result.active == 1
            assert result.languages == ["en", "sv"]

    @pytest.mark.asyncio
    async def test_get(self, httpx_mock: HTTPXMock, sample_data):
        """Test getting a single group mail category."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/groupMailCategories/1",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = GroupMailCategoriesResource(http)
            result = await resource.get(1)

            assert isinstance(result, GroupMailCategory)
            assert result.id == 1
            assert result.title == "Newsletter Category"

    @pytest.mark.asyncio
    async def test_list(self, httpx_mock: HTTPXMock, sample_list_response):
        """Test listing group mail categories with pagination."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/groupMailCategories?limit=10&offset=0",
            json=sample_list_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = GroupMailCategoriesResource(http)
            result = await resource.list(limit=10)

            assert isinstance(result, list)
            assert len(result) == 2
            assert all(isinstance(item, GroupMailCategory) for item in result)

    @pytest.mark.asyncio
    async def test_update(self, httpx_mock: HTTPXMock, sample_data):
        """Test updating a group mail category."""
        updated_data = {**sample_data, "title": "Updated Category"}
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/groupMailCategories/1",
            method="PUT",
            json={"error": None, "data": updated_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = GroupMailCategoriesResource(http)
            result = await resource.update(1, title="Updated Category")

            assert isinstance(result, GroupMailCategory)
            assert result.id == 1
            assert result.title == "Updated Category"

    @pytest.mark.asyncio
    async def test_delete(self, httpx_mock: HTTPXMock):
        """Test deleting a group mail category."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/groupMailCategories/1",
            method="DELETE",
            json={"error": None, "data": {}},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = GroupMailCategoriesResource(http)
            await resource.delete(1)

            # No exception means success

    @pytest.mark.asyncio
    async def test_get_active(self, httpx_mock: HTTPXMock, sample_data):
        """Test getting active categories."""
        # list_all makes paginated requests - use 100 items to trigger pagination
        page1_data = [{**sample_data, "id": i, "title": f"Category {i}"} for i in range(1, 101)]
        page2_data = [{**sample_data, "id": i, "title": f"Category {i}"} for i in range(101, 151)]

        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/groupMailCategories?active=1&limit=100&offset=0",
            json={
                "error": None,
                "metadata": {"total": 150, "limit": 100, "offset": 0},
                "data": page1_data,
            },
        )
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/groupMailCategories?active=1&limit=100&offset=100",
            json={
                "error": None,
                "metadata": {"total": 150, "limit": 100, "offset": 100},
                "data": page2_data,
            },
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = GroupMailCategoriesResource(http)
            result = await resource.get_active()

            assert isinstance(result, list)
            assert len(result) == 150
            assert all(isinstance(item, GroupMailCategory) for item in result)


class TestGroupMailCategoryModel:
    """Test GroupMailCategory model features."""

    def test_is_active_property(self):
        """Test is_active computed property."""
        category = GroupMailCategory(
            id=1,
            title="Test Category",
            active=1,
        )
        assert category.is_active is True

        inactive_category = GroupMailCategory(
            id=2,
            title="Inactive Category",
            active=0,
        )
        assert inactive_category.is_active is False

    def test_frozen_fields(self):
        """Test that frozen fields cannot be modified."""
        category = GroupMailCategory(
            id=1,
            title="Test Category",
            active=1,
        )

        # Attempt to modify frozen field should raise ValidationError
        with pytest.raises(Exception):  # Pydantic raises validation error
            category.id = 999

    def test_default_values(self):
        """Test default values for optional fields."""
        category = GroupMailCategory(
            id=1,
            title="Test Category",
        )
        assert category.description is None
        assert category.active == 1
        assert category.languages == []
        assert category.relatedMailCampaigns == []

    @pytest.mark.asyncio
    async def test_edit_method(self, httpx_mock: HTTPXMock):
        """Test model edit method."""
        from upsales import Upsales

        updated_data = {
            "id": 1,
            "title": "Updated Title",
            "description": "Updated description",
            "active": 1,
            "languages": ["en"],
            "relatedMailCampaigns": [],
        }

        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/groupMailCategories/1",
            method="PUT",
            json={"error": None, "data": updated_data},
        )

        async with Upsales(token="test_token") as upsales:
            category = GroupMailCategory(
                id=1,
                title="Old Title",
                description="Old description",
                active=1,
                _client=upsales,
            )

            updated = await category.edit(title="Updated Title", description="Updated description")
            assert updated.title == "Updated Title"
            assert updated.description == "Updated description"
