"""
Unit tests for PagesResource.

Tests GET (list/get) and PUT (update) operations for pages endpoint.
Note: Pages endpoint does not support CREATE or DELETE operations.
"""

import pytest
from pytest_httpx import HTTPXMock

from upsales.http import HTTPClient
from upsales.models.pages import Page, PartialPage
from upsales.resources.pages import PagesResource


class TestPagesResourceCRUD:
    """Test CRUD operations for PagesResource."""

    @pytest.fixture
    def sample_data(self):
        """Sample page data for testing."""
        return {
            "id": 1,
            "name": "Product Landing Page",
            "url": "https://example.com/products",
            "state": "active",
            "lastUpdateDate": "2024-01-15",
            "pageImpression": 1250,
            "score": 85,
            "hide": 0,
            "keywords": ["product", "landing", "campaign"],
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
                    "name": "Services Page",
                    "url": "https://example.com/services",
                    "pageImpression": 890,
                },
            ],
        }

    @pytest.mark.asyncio
    async def test_get(self, httpx_mock: HTTPXMock, sample_data):
        """Test getting a single page."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/pages/1",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = PagesResource(http)
            result = await resource.get(1)

            assert isinstance(result, Page)
            assert result.id == 1
            assert result.name == "Product Landing Page"
            assert result.url == "https://example.com/products"
            assert result.pageImpression == 1250
            assert result.hide == 0

    @pytest.mark.asyncio
    async def test_list(self, httpx_mock: HTTPXMock, sample_list_response):
        """Test listing pages with pagination."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/pages?limit=10&offset=0",
            json=sample_list_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = PagesResource(http)
            results = await resource.list(limit=10, offset=0)

            assert len(results) == 2
            assert all(isinstance(p, Page) for p in results)
            assert results[0].name == "Product Landing Page"
            assert results[1].name == "Services Page"

    @pytest.mark.asyncio
    async def test_list_all(self, httpx_mock: HTTPXMock, sample_data):
        """Test listing all pages with auto-pagination."""
        # First batch
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/pages?limit=100&offset=0",
            json={
                "error": None,
                "metadata": {"total": 150, "limit": 100, "offset": 0},
                "data": [sample_data] * 100,
            },
        )
        # Second batch
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/pages?limit=100&offset=100",
            json={
                "error": None,
                "metadata": {"total": 150, "limit": 100, "offset": 100},
                "data": [sample_data] * 50,
            },
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = PagesResource(http)
            results = await resource.list_all()

            assert len(results) == 150
            assert all(isinstance(p, Page) for p in results)

    @pytest.mark.asyncio
    async def test_update(self, httpx_mock: HTTPXMock, sample_data):
        """Test updating a page."""
        updated_data = {**sample_data, "name": "Updated Page", "hide": 1}
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/pages/1",
            method="PUT",
            json={"error": None, "data": updated_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = PagesResource(http)
            result = await resource.update(1, name="Updated Page", hide=1)

            assert isinstance(result, Page)
            assert result.name == "Updated Page"
            assert result.hide == 1

    @pytest.mark.asyncio
    async def test_search(self, httpx_mock: HTTPXMock, sample_data):
        """Test searching pages."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/pages?limit=100&offset=0&hide=0",
            json={
                "error": None,
                "metadata": {"total": 1, "limit": 100, "offset": 0},
                "data": [sample_data],
            },
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = PagesResource(http)
            results = await resource.search(hide=0)

            assert len(results) == 1
            assert results[0].hide == 0


class TestPageModel:
    """Test Page model functionality."""

    @pytest.fixture
    def sample_page_data(self):
        """Sample page data."""
        return {
            "id": 1,
            "name": "Test Page",
            "url": "https://example.com/test",
            "state": "active",
            "lastUpdateDate": "2024-01-15",
            "pageImpression": 500,
            "score": 75,
            "hide": 0,
            "keywords": ["test", "page"],
        }

    def test_page_creation(self, sample_page_data):
        """Test creating a Page instance."""
        page = Page(**sample_page_data)

        assert page.id == 1
        assert page.name == "Test Page"
        assert page.url == "https://example.com/test"
        assert page.pageImpression == 500
        assert page.hide == 0

    def test_computed_properties(self, sample_page_data):
        """Test computed properties."""
        # Test visible page
        page = Page(**sample_page_data)
        assert page.is_visible is True
        assert page.is_hidden is False

        # Test hidden page
        page_hidden = Page(**{**sample_page_data, "hide": 1})
        assert page_hidden.is_visible is False
        assert page_hidden.is_hidden is True

    def test_frozen_fields(self, sample_page_data):
        """Test that frozen fields cannot be modified."""
        page = Page(**sample_page_data)

        # Frozen fields should raise ValidationError when modified
        with pytest.raises(Exception):  # Pydantic ValidationError
            page.id = 999

        with pytest.raises(Exception):
            page.pageImpression = 9999

    def test_binary_flag_validation(self, sample_page_data):
        """Test BinaryFlag validator for hide field."""
        # Valid values (0 and 1)
        page = Page(**sample_page_data)
        assert page.hide == 0

        page2 = Page(**{**sample_page_data, "hide": 1})
        assert page2.hide == 1

        # Invalid value should raise error
        with pytest.raises(Exception):
            Page(**{**sample_page_data, "hide": 2})


class TestPartialPageModel:
    """Test PartialPage model functionality."""

    @pytest.fixture
    def sample_partial_data(self):
        """Sample partial page data."""
        return {
            "id": 1,
            "name": "Test Page",
        }

    @pytest.fixture
    def sample_full_data(self):
        """Sample full page data for fetch_full tests."""
        return {
            "id": 1,
            "name": "Test Page",
            "url": "https://example.com/test",
            "state": "active",
            "lastUpdateDate": "2024-01-15",
            "pageImpression": 500,
            "score": 75,
            "hide": 0,
            "keywords": ["test"],
        }

    def test_partial_creation(self, sample_partial_data):
        """Test creating a PartialPage instance."""
        partial = PartialPage(**sample_partial_data)

        assert partial.id == 1
        assert partial.name == "Test Page"


class TestPageUpdateFields:
    """Test PageUpdateFields TypedDict."""

    def test_type_dict_structure(self):
        """Test that PageUpdateFields is properly defined."""
        from upsales.models.pages import PageUpdateFields

        # Should be able to create with any combination of fields
        fields: PageUpdateFields = {
            "name": "Test",
            "url": "https://example.com",
            "hide": 1,
        }

        assert fields["name"] == "Test"
        assert fields["url"] == "https://example.com"
        assert fields["hide"] == 1
