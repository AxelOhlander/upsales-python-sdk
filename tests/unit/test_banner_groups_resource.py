"""Unit tests for BannerGroupsResource.

Tests CRUD operations for banner groups endpoint.
"""

import pytest
from pytest_httpx import HTTPXMock

from upsales.http import HTTPClient
from upsales.models.banner_groups import BannerGroup
from upsales.resources.banner_groups import BannerGroupsResource


class TestBannerGroupsResourceCRUD:
    """Test CRUD operations for BannerGroupsResource."""

    @pytest.fixture
    def sample_data(self):
        """Sample banner group data for testing."""
        return {
            "id": 1,
            "title": "Q4 Campaign",
            "regBy": {"id": 1, "name": "Admin"},
            "draft": False,
            "body": "Campaign body content",
            "landingPage": "https://example.com/campaign",
            "regDate": "2024-01-01",
            "modDate": "2024-01-02",
            "pages": "home,about",
            "formats": "banner,popup",
            "availableFormats": "banner,popup,sidebar",
            "brandId": 1,
            "custom": [],
        }

    @pytest.fixture
    def sample_list_response(self, sample_data):
        """Sample list response."""
        return {
            "error": None,
            "metadata": {"total": 2, "limit": 100, "offset": 0},
            "data": [
                sample_data,
                {**sample_data, "id": 2, "title": "Q1 Campaign"},
            ],
        }

    @pytest.mark.asyncio
    async def test_create(self, httpx_mock: HTTPXMock, sample_data):
        """Test creating a banner group."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/bannerGroups",
            method="POST",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = BannerGroupsResource(http)
            result = await resource.create(
                landingPage="https://example.com/campaign",
                title="Q4 Campaign",
                draft=False,
            )

            assert isinstance(result, BannerGroup)
            assert result.id == 1
            assert result.title == "Q4 Campaign"
            assert result.landingPage == "https://example.com/campaign"
            assert result.draft is False

    @pytest.mark.asyncio
    async def test_get(self, httpx_mock: HTTPXMock, sample_data):
        """Test getting a single banner group."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/bannerGroups/1",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = BannerGroupsResource(http)
            result = await resource.get(1)

            assert isinstance(result, BannerGroup)
            assert result.id == 1
            assert result.title == "Q4 Campaign"

    @pytest.mark.asyncio
    async def test_list(self, httpx_mock: HTTPXMock, sample_list_response):
        """Test listing banner groups with pagination."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/bannerGroups?limit=10&offset=0",
            json=sample_list_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = BannerGroupsResource(http)
            result = await resource.list(limit=10)

            assert isinstance(result, list)
            assert len(result) == 2
            assert all(isinstance(item, BannerGroup) for item in result)

    @pytest.mark.asyncio
    async def test_update(self, httpx_mock: HTTPXMock, sample_data):
        """Test updating a banner group."""
        updated_data = {**sample_data, "title": "Updated Campaign"}
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/bannerGroups/1",
            method="PUT",
            json={"error": None, "data": updated_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = BannerGroupsResource(http)
            result = await resource.update(1, title="Updated Campaign")

            assert isinstance(result, BannerGroup)
            assert result.id == 1
            assert result.title == "Updated Campaign"

    @pytest.mark.asyncio
    async def test_delete(self, httpx_mock: HTTPXMock):
        """Test deleting a banner group."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/bannerGroups/1",
            method="DELETE",
            json={"error": None, "data": {}},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = BannerGroupsResource(http)
            await resource.delete(1)

            # No exception means success


class TestBannerGroupModel:
    """Test BannerGroup model features."""

    def test_is_draft_property(self):
        """Test is_draft computed property."""
        banner = BannerGroup(
            id=1,
            title="Test",
            landingPage="https://example.com",
            draft=True,
        )
        assert banner.is_draft is True

        banner_published = BannerGroup(
            id=2,
            title="Test Published",
            landingPage="https://example.com",
            draft=False,
        )
        assert banner_published.is_draft is False

    def test_custom_fields_property(self):
        """Test custom_fields computed property."""
        banner = BannerGroup(
            id=1,
            title="Test",
            landingPage="https://example.com",
            custom=[{"fieldId": 11, "value": "test_value"}],
        )
        assert banner.custom_fields.get(11) == "test_value"

    @pytest.mark.asyncio
    async def test_edit_method(self, httpx_mock: HTTPXMock):
        """Test model edit method."""
        from upsales import Upsales

        updated_data = {
            "id": 1,
            "title": "Updated Title",
            "landingPage": "https://example.com",
            "draft": False,
            "custom": [],
        }

        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/bannerGroups/1",
            method="PUT",
            json={"error": None, "data": updated_data},
        )

        async with Upsales(token="test_token") as upsales:
            banner = BannerGroup(
                id=1,
                title="Old Title",
                landingPage="https://example.com",
                draft=True,
                _client=upsales,
            )

            updated = await banner.edit(title="Updated Title", draft=False)
            assert updated.title == "Updated Title"
            assert updated.draft is False
