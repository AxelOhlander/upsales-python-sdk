"""Unit tests for StandardCreative resource manager."""

import pytest
from pytest_httpx import HTTPXMock

from upsales.http import HTTPClient
from upsales.models.standard_creative import PartialStandardCreative, StandardCreative
from upsales.resources.standard_creative import StandardCreativeResource


class TestStandardCreativeResource:
    """Test suite for StandardCreativeResource."""

    @pytest.fixture
    def sample_data(self):
        """Sample creative data for testing."""
        return {
            "id": 1,
            "name": "Welcome Email",
            "subject": "Welcome to our platform!",
            "body": "<p>Hello and welcome!</p>",
            "active": 1,
        }

    @pytest.fixture
    def sample_list_response(self, sample_data):
        """Sample list response."""
        return {
            "error": None,
            "metadata": {"total": 2, "limit": 100, "offset": 0},
            "data": [
                sample_data,
                {**sample_data, "id": 2, "name": "Follow-up Email"},
            ],
        }

    @pytest.mark.asyncio
    async def test_get(self, httpx_mock: HTTPXMock, sample_data):
        """Test getting a single creative."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/standardCreative/1",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = StandardCreativeResource(http)
            result = await resource.get(1)

            assert isinstance(result, StandardCreative)
            assert result.id == 1
            assert result.name == "Welcome Email"
            assert result.subject == "Welcome to our platform!"
            assert result.is_active is True

    @pytest.mark.asyncio
    async def test_list(self, httpx_mock: HTTPXMock, sample_list_response):
        """Test listing creatives."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/standardCreative?limit=10&offset=0",
            json=sample_list_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = StandardCreativeResource(http)
            result = await resource.list(limit=10)

            assert isinstance(result, list)
            assert len(result) == 2
            assert all(isinstance(r, StandardCreative) for r in result)
            assert result[0].name == "Welcome Email"
            assert result[1].name == "Follow-up Email"

    @pytest.mark.asyncio
    async def test_list_all(self, httpx_mock: HTTPXMock, sample_list_response):
        """Test listing all creatives with auto-pagination."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/standardCreative?limit=100&offset=0",
            json=sample_list_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = StandardCreativeResource(http)
            result = await resource.list_all()

            assert isinstance(result, list)
            assert len(result) == 2
            assert result[0].name == "Welcome Email"


class TestStandardCreativeModel:
    """Test suite for StandardCreative model."""

    def test_model_creation(self):
        """Test creating a StandardCreative instance."""
        creative = StandardCreative(
            id=1,
            name="Welcome Email",
            subject="Welcome to our platform!",
            body="<p>Hello and welcome!</p>",
            active=1,
        )

        assert creative.id == 1
        assert creative.name == "Welcome Email"
        assert creative.subject == "Welcome to our platform!"
        assert creative.body == "<p>Hello and welcome!</p>"
        assert creative.active == 1

    def test_is_active_property(self):
        """Test is_active computed property."""
        active = StandardCreative(id=1, name="Active", subject="Test", body="<p>Test</p>", active=1)
        inactive = StandardCreative(
            id=2, name="Inactive", subject="Test", body="<p>Test</p>", active=0
        )

        assert active.is_active is True
        assert inactive.is_active is False

    def test_frozen_fields(self):
        """Test that id is frozen and cannot be modified."""
        creative = StandardCreative(id=1, name="Test", subject="Test", body="<p>Test</p>", active=1)

        with pytest.raises(ValueError, match="frozen"):
            creative.id = 999

    def test_optional_fields(self):
        """Test model with optional fields as None."""
        creative = StandardCreative(id=1, name="Test", subject=None, body=None, active=1)

        assert creative.subject is None
        assert creative.body is None


class TestPartialStandardCreative:
    """Test suite for PartialStandardCreative model."""

    def test_partial_creation(self):
        """Test creating a PartialStandardCreative instance."""
        partial = PartialStandardCreative(id=1, name="Welcome Email")

        assert partial.id == 1
        assert partial.name == "Welcome Email"

    @pytest.mark.asyncio
    async def test_fetch_full(self):
        """Test fetch_full method exists and has correct signature."""
        partial = PartialStandardCreative(id=1, name="Welcome Email")

        # Test that the method exists
        assert hasattr(partial, "fetch_full")
        assert callable(partial.fetch_full)

        # Test it raises error when no client
        with pytest.raises(RuntimeError, match="No client available"):
            await partial.fetch_full()

    @pytest.mark.asyncio
    async def test_fetch_full_no_client(self):
        """Test fetch_full raises error when no client available."""
        partial = PartialStandardCreative(id=1, name="Test")

        with pytest.raises(RuntimeError, match="No client available"):
            await partial.fetch_full()
