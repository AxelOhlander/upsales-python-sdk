"""Unit tests for AdCreatives resource."""

from unittest.mock import AsyncMock

import pytest

from upsales.models.ad_creatives import AdCreative, PartialAdCreative
from upsales.resources.ad_creatives import AdCreativesResource


@pytest.fixture
def ad_creatives_resource(mock_http_client):
    """Create AdCreativesResource with mock HTTP client."""
    return AdCreativesResource(mock_http_client)


@pytest.fixture
def sample_ad_creative_data():
    """Sample ad creative data from API."""
    return {
        "id": 123,
        "name": "Banner 300x250",
        "type": "image",
        "width": 300,
        "height": 250,
        "url": "https://example.com/banner.jpg",
        "fileId": 456,
        "formatId": 789,
        "sampleImageUrl": "https://example.com/preview.jpg",
        "state": "active",
        "impressions": 10000,
        "clicks": 250,
    }


@pytest.fixture
def sample_partial_ad_creative_data():
    """Sample partial ad creative data."""
    return {
        "id": 123,
        "name": "Banner 300x250",
        "type": "image",
    }


class TestAdCreativesResource:
    """Tests for AdCreativesResource."""

    async def test_get_ad_creative(
        self, ad_creatives_resource, mock_http_client, sample_ad_creative_data
    ):
        """Test getting a single ad creative."""
        mock_http_client.get = AsyncMock(return_value={"data": sample_ad_creative_data})

        creative = await ad_creatives_resource.get(123)

        assert isinstance(creative, AdCreative)
        assert creative.id == 123
        assert creative.name == "Banner 300x250"
        assert creative.type == "image"
        assert creative.width == 300
        assert creative.height == 250
        assert creative.url == "https://example.com/banner.jpg"
        assert creative.impressions == 10000
        assert creative.clicks == 250

    async def test_list_ad_creatives(
        self, ad_creatives_resource, mock_http_client, sample_ad_creative_data
    ):
        """Test listing ad creatives."""
        mock_http_client.get = AsyncMock(return_value={"data": [sample_ad_creative_data]})

        creatives = await ad_creatives_resource.list()

        assert len(creatives) == 1
        assert isinstance(creatives[0], AdCreative)
        assert creatives[0].id == 123

    async def test_create_ad_creative(
        self, ad_creatives_resource, mock_http_client, sample_ad_creative_data
    ):
        """Test creating an ad creative."""
        mock_http_client.post = AsyncMock(return_value={"data": sample_ad_creative_data})

        creative = await ad_creatives_resource.create(
            name="New Banner",
            type="image",
            width=300,
            height=250,
            url="https://example.com/new.jpg",
        )

        assert isinstance(creative, AdCreative)
        assert creative.id == 123
        mock_http_client.post.assert_called_once()

    async def test_update_ad_creative(
        self, ad_creatives_resource, mock_http_client, sample_ad_creative_data
    ):
        """Test updating an ad creative."""
        updated_data = sample_ad_creative_data.copy()
        updated_data["name"] = "Updated Banner"
        mock_http_client.put = AsyncMock(return_value={"data": updated_data})

        creative = await ad_creatives_resource.update(123, name="Updated Banner")

        assert isinstance(creative, AdCreative)
        assert creative.name == "Updated Banner"
        mock_http_client.put.assert_called_once()

    async def test_delete_ad_creative(self, ad_creatives_resource, mock_http_client):
        """Test deleting an ad creative."""
        mock_http_client.delete = AsyncMock(return_value=None)

        await ad_creatives_resource.delete(123)

        mock_http_client.delete.assert_called_once_with("/adCreatives/123")

    async def test_get_by_type(
        self, ad_creatives_resource, mock_http_client, sample_ad_creative_data
    ):
        """Test getting ad creatives by type."""
        mock_http_client.get = AsyncMock(return_value={"data": [sample_ad_creative_data]})

        creatives = await ad_creatives_resource.get_by_type("image")

        assert len(creatives) == 1
        assert creatives[0].type == "image"


class TestAdCreativeModel:
    """Tests for AdCreative model."""

    def test_ad_creative_initialization(self, sample_ad_creative_data):
        """Test AdCreative model initialization."""
        creative = AdCreative(**sample_ad_creative_data)

        assert creative.id == 123
        assert creative.name == "Banner 300x250"
        assert creative.type == "image"
        assert creative.width == 300
        assert creative.height == 250
        assert creative.impressions == 10000
        assert creative.clicks == 250

    def test_dimensions_property(self, sample_ad_creative_data):
        """Test dimensions computed field."""
        creative = AdCreative(**sample_ad_creative_data)

        assert creative.dimensions == "300x250"

    def test_click_through_rate_property(self, sample_ad_creative_data):
        """Test click_through_rate computed field."""
        creative = AdCreative(**sample_ad_creative_data)

        assert creative.click_through_rate == 2.5  # 250/10000 * 100

    def test_click_through_rate_no_impressions(self, sample_ad_creative_data):
        """Test click_through_rate when no impressions."""
        data = sample_ad_creative_data.copy()
        data["impressions"] = 0
        creative = AdCreative(**data)

        assert creative.click_through_rate is None

    def test_is_image_property(self, sample_ad_creative_data):
        """Test is_image computed field."""
        creative = AdCreative(**sample_ad_creative_data)

        assert creative.is_image is True

    def test_is_html5_property(self, sample_ad_creative_data):
        """Test is_html5 computed field."""
        creative = AdCreative(**sample_ad_creative_data)

        assert creative.is_html5 is False

    def test_html5_type(self, sample_ad_creative_data):
        """Test HTML5 creative type."""
        data = sample_ad_creative_data.copy()
        data["type"] = "html5"
        creative = AdCreative(**data)

        assert creative.is_html5 is True
        assert creative.is_image is False

    def test_frozen_fields(self, sample_ad_creative_data):
        """Test that frozen fields cannot be modified."""
        creative = AdCreative(**sample_ad_creative_data)

        with pytest.raises(Exception):
            creative.id = 999

    def test_edit_method_without_client(self, sample_ad_creative_data):
        """Test that edit raises error without client."""
        import asyncio

        creative = AdCreative(**sample_ad_creative_data)

        with pytest.raises(RuntimeError, match="No client available"):
            asyncio.run(creative.edit(name="Updated Name"))


class TestPartialAdCreativeModel:
    """Tests for PartialAdCreative model."""

    def test_partial_ad_creative_initialization(self, sample_partial_ad_creative_data):
        """Test PartialAdCreative initialization."""
        partial = PartialAdCreative(**sample_partial_ad_creative_data)

        assert partial.id == 123
        assert partial.name == "Banner 300x250"
        assert partial.type == "image"

    def test_fetch_full_without_client(self, sample_partial_ad_creative_data):
        """Test that fetch_full raises error without client."""
        import asyncio

        partial = PartialAdCreative(**sample_partial_ad_creative_data)

        with pytest.raises(RuntimeError, match="No client available"):
            asyncio.run(partial.fetch_full())

    def test_edit_from_partial_without_client(self, sample_partial_ad_creative_data):
        """Test that edit raises error without client."""
        import asyncio

        partial = PartialAdCreative(**sample_partial_ad_creative_data)

        with pytest.raises(RuntimeError, match="No client available"):
            asyncio.run(partial.edit(name="New Name"))


class TestAdCreativeValidation:
    """Tests for AdCreative field validation."""

    def test_required_fields(self):
        """Test that required fields are validated."""
        with pytest.raises(Exception):
            AdCreative(id=1)  # Missing required fields

    def test_type_literal(self, sample_ad_creative_data):
        """Test that type field only accepts valid values."""
        data = sample_ad_creative_data.copy()

        # Valid types
        for valid_type in ["image", "html5", "third_party_tag", "zip"]:
            data["type"] = valid_type
            creative = AdCreative(**data)
            assert creative.type == valid_type

    def test_positive_dimensions(self, sample_ad_creative_data):
        """Test that width and height must be positive."""
        data = sample_ad_creative_data.copy()

        # Width must be positive
        data["width"] = -1
        with pytest.raises(Exception):
            AdCreative(**data)

        # Height must be positive
        data["width"] = 300
        data["height"] = -1
        with pytest.raises(Exception):
            AdCreative(**data)

    def test_max_length_validation(self, sample_ad_creative_data):
        """Test max length validation for string fields."""
        data = sample_ad_creative_data.copy()

        # Name max length: 100
        data["name"] = "A" * 101
        with pytest.raises(Exception):
            AdCreative(**data)

        # URL max length: 255
        data["name"] = "Valid Name"
        data["url"] = "https://" + "a" * 250
        with pytest.raises(Exception):
            AdCreative(**data)
