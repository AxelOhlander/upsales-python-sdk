"""
Unit tests for ProjectPlanPrioritiesResource.

Tests CRUD operations and custom methods for the projectPlanPriority endpoint.
"""

import pytest
from pytest_httpx import HTTPXMock

from upsales.http import HTTPClient
from upsales.models.project_plan_priority import ProjectPlanPriority
from upsales.resources.project_plan_priority import ProjectPlanPrioritiesResource


class TestProjectPlanPrioritiesResourceCRUD:
    """Test CRUD operations for ProjectPlanPrioritiesResource."""

    @pytest.fixture
    def sample_data(self):
        """Sample priority data for testing."""
        return {
            "id": 1,
            "name": "Låg",
            "category": "LOW",
            "isDefault": True,
        }

    @pytest.fixture
    def sample_list_response(self, sample_data):
        """Sample list response with multiple priorities."""
        return {
            "error": None,
            "metadata": {"total": 3, "limit": 1000, "offset": 0},
            "data": [
                sample_data,
                {"id": 2, "name": "Medel", "category": "MEDIUM", "isDefault": True},
                {"id": 3, "name": "Hög", "category": "HIGH", "isDefault": True},
            ],
        }

    @pytest.mark.asyncio
    async def test_create(self, httpx_mock: HTTPXMock, sample_data):
        """Test creating a priority."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/projectPlanPriority",
            method="POST",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ProjectPlanPrioritiesResource(http)
            result = await resource.create(name="Låg", category="LOW", isDefault=True)

            assert isinstance(result, ProjectPlanPriority)
            assert result.id == 1
            assert result.name == "Låg"
            assert result.category == "LOW"
            assert result.is_default

    @pytest.mark.asyncio
    async def test_get(self, httpx_mock: HTTPXMock, sample_data):
        """Test getting a single priority."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/projectPlanPriority/1",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ProjectPlanPrioritiesResource(http)
            result = await resource.get(1)

            assert isinstance(result, ProjectPlanPriority)
            assert result.id == 1
            assert result.name == "Låg"
            assert result.is_low

    @pytest.mark.asyncio
    async def test_list(self, httpx_mock: HTTPXMock, sample_list_response):
        """Test listing priorities."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/projectPlanPriority?limit=100&offset=0",
            json=sample_list_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ProjectPlanPrioritiesResource(http)
            results = await resource.list(limit=100, offset=0)

            assert len(results) == 3
            assert all(isinstance(r, ProjectPlanPriority) for r in results)
            assert results[0].category == "LOW"
            assert results[1].category == "MEDIUM"
            assert results[2].category == "HIGH"

    @pytest.mark.asyncio
    async def test_update(self, httpx_mock: HTTPXMock, sample_data):
        """Test updating a priority."""
        updated_data = {**sample_data, "name": "Low Priority"}
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/projectPlanPriority/1",
            method="PUT",
            json={"error": None, "data": updated_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ProjectPlanPrioritiesResource(http)
            result = await resource.update(1, name="Low Priority")

            assert isinstance(result, ProjectPlanPriority)
            assert result.id == 1
            assert result.name == "Low Priority"

    @pytest.mark.asyncio
    async def test_delete(self, httpx_mock: HTTPXMock):
        """Test deleting a priority."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/projectPlanPriority/1",
            method="DELETE",
            json={"error": None, "data": None},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ProjectPlanPrioritiesResource(http)
            await resource.delete(1)
            # If no exception, test passes


class TestProjectPlanPrioritiesResourceCustomMethods:
    """Test custom methods for ProjectPlanPrioritiesResource."""

    @pytest.fixture
    def sample_list_response(self):
        """Sample list response with multiple priorities."""
        return {
            "error": None,
            "metadata": {"total": 5, "limit": 1000, "offset": 0},
            "data": [
                {"id": 1, "name": "Låg", "category": "LOW", "isDefault": True},
                {"id": 2, "name": "Medel", "category": "MEDIUM", "isDefault": True},
                {"id": 3, "name": "Hög", "category": "HIGH", "isDefault": True},
                {"id": 4, "name": "Custom Low", "category": "LOW", "isDefault": False},
                {"id": 5, "name": "Custom High", "category": "HIGH", "isDefault": False},
            ],
        }

    @pytest.mark.asyncio
    async def test_get_by_category(self, httpx_mock: HTTPXMock, sample_list_response):
        """Test getting priorities by category."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/projectPlanPriority?limit=100&offset=0",
            json=sample_list_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ProjectPlanPrioritiesResource(http)
            results = await resource.get_by_category("LOW")

            assert len(results) == 2
            assert all(p.category == "LOW" for p in results)
            assert results[0].name == "Låg"
            assert results[1].name == "Custom Low"

    @pytest.mark.asyncio
    async def test_get_defaults(self, httpx_mock: HTTPXMock, sample_list_response):
        """Test getting default priorities."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/projectPlanPriority?limit=100&offset=0",
            json=sample_list_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ProjectPlanPrioritiesResource(http)
            results = await resource.get_defaults()

            assert len(results) == 3
            assert all(p.is_default for p in results)

    @pytest.mark.asyncio
    async def test_get_by_name(self, httpx_mock: HTTPXMock, sample_list_response):
        """Test getting priority by name (case-insensitive)."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/projectPlanPriority?limit=100&offset=0",
            json=sample_list_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ProjectPlanPrioritiesResource(http)
            result = await resource.get_by_name("låg")  # Lowercase search

            assert result is not None
            assert result.name == "Låg"
            assert result.category == "LOW"

    @pytest.mark.asyncio
    async def test_get_by_name_not_found(self, httpx_mock: HTTPXMock, sample_list_response):
        """Test getting priority by name when not found."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/projectPlanPriority?limit=100&offset=0",
            json=sample_list_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ProjectPlanPrioritiesResource(http)
            result = await resource.get_by_name("Nonexistent")

            assert result is None

    @pytest.mark.asyncio
    async def test_get_low(self, httpx_mock: HTTPXMock, sample_list_response):
        """Test convenience method for getting low priorities."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/projectPlanPriority?limit=100&offset=0",
            json=sample_list_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ProjectPlanPrioritiesResource(http)
            results = await resource.get_low()

            assert len(results) == 2
            assert all(p.is_low for p in results)

    @pytest.mark.asyncio
    async def test_get_medium(self, httpx_mock: HTTPXMock, sample_list_response):
        """Test convenience method for getting medium priorities."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/projectPlanPriority?limit=100&offset=0",
            json=sample_list_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ProjectPlanPrioritiesResource(http)
            results = await resource.get_medium()

            assert len(results) == 1
            assert all(p.is_medium for p in results)

    @pytest.mark.asyncio
    async def test_get_high(self, httpx_mock: HTTPXMock, sample_list_response):
        """Test convenience method for getting high priorities."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/projectPlanPriority?limit=100&offset=0",
            json=sample_list_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ProjectPlanPrioritiesResource(http)
            results = await resource.get_high()

            assert len(results) == 2
            assert all(p.is_high for p in results)


class TestProjectPlanPriorityModel:
    """Test ProjectPlanPriority model computed fields."""

    def test_is_default(self):
        """Test is_default computed field."""
        priority = ProjectPlanPriority(id=1, name="Låg", category="LOW", isDefault=True)
        assert priority.is_default is True

        priority2 = ProjectPlanPriority(id=2, name="Custom", category="LOW", isDefault=False)
        assert priority2.is_default is False

    def test_is_low(self):
        """Test is_low computed field."""
        priority = ProjectPlanPriority(id=1, name="Låg", category="LOW", isDefault=True)
        assert priority.is_low is True
        assert priority.is_medium is False
        assert priority.is_high is False

    def test_is_medium(self):
        """Test is_medium computed field."""
        priority = ProjectPlanPriority(id=2, name="Medel", category="MEDIUM", isDefault=True)
        assert priority.is_medium is True
        assert priority.is_low is False
        assert priority.is_high is False

    def test_is_high(self):
        """Test is_high computed field."""
        priority = ProjectPlanPriority(id=3, name="Hög", category="HIGH", isDefault=True)
        assert priority.is_high is True
        assert priority.is_low is False
        assert priority.is_medium is False
