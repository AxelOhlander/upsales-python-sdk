"""
Unit tests for ProjectplanstagesResource.

Tests all CRUD operations for the project_plan_stages endpoint.
"""

import pytest
from pytest_httpx import HTTPXMock

from upsales.http import HTTPClient
from upsales.models.project_plan_stages import ProjectPlanStage
from upsales.resources.project_plan_stages import ProjectplanstagesResource


class TestProjectplanstagesResourceCRUD:
    """Test CRUD operations for ProjectplanstagesResource."""

    @pytest.fixture
    def sample_data(self):
        """Sample projectplanstage data for testing."""
        return {
            "id": 1,
            "name": "Test Stage",
            "category": "TODO",
            "color": "#FCF0C0",
        }

    @pytest.fixture
    def sample_list_response(self, sample_data):
        """Sample list response."""
        return {
            "error": None,
            "metadata": {"total": 2, "limit": 100, "offset": 0},
            "data": [
                sample_data,
                {**sample_data, "id": 2, "name": "Test Stage 2"},
            ],
        }

    @pytest.mark.asyncio
    async def test_create(self, httpx_mock: HTTPXMock, sample_data):
        """Test creating a projectplanstage."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/projectPlanStages",
            method="POST",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ProjectplanstagesResource(http)
            result = await resource.create(name="Test Stage", category="TODO", color="#FCF0C0")

            assert isinstance(result, ProjectPlanStage)
            assert result.id == 1
            assert result.name == "Test Stage"

    @pytest.mark.asyncio
    async def test_get(self, httpx_mock: HTTPXMock, sample_data):
        """Test getting a single projectplanstage."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/projectPlanStages/1",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ProjectplanstagesResource(http)
            result = await resource.get(1)

            assert isinstance(result, ProjectPlanStage)
            assert result.id == 1

    @pytest.mark.asyncio
    async def test_list(self, httpx_mock: HTTPXMock, sample_list_response):
        """Test listing project_plan_stages with pagination."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/projectPlanStages?limit=10&offset=0",
            json=sample_list_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ProjectplanstagesResource(http)
            results = await resource.list(limit=10, offset=0)

            assert isinstance(results, list)
            assert len(results) == 2
            assert all(isinstance(item, ProjectPlanStage) for item in results)

    @pytest.mark.asyncio
    async def test_list_all_single_page(self, httpx_mock: HTTPXMock, sample_data):
        """Test list_all with single page of results."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/projectPlanStages?limit=100&offset=0",
            json={
                "error": None,
                "metadata": {"total": 50, "limit": 100, "offset": 0},
                "data": [sample_data],  # Less than batch_size
            },
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ProjectplanstagesResource(http)
            results = await resource.list_all()

            assert len(results) == 1
            # Should only make 1 request since results < batch_size
            assert len(httpx_mock.get_requests()) == 1

    @pytest.mark.asyncio
    async def test_list_all_multi_page(self, httpx_mock: HTTPXMock, sample_data):
        """Test list_all with multiple pages."""
        # Page 1: full batch
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/projectPlanStages?limit=2&offset=0",
            json={"error": None, "data": [sample_data, sample_data]},
        )
        # Page 2: partial batch (last page)
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/projectPlanStages?limit=2&offset=2",
            json={"error": None, "data": [sample_data]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ProjectplanstagesResource(http)
            results = await resource.list_all(batch_size=2)

            assert len(results) == 3
            assert len(httpx_mock.get_requests()) == 2

    @pytest.mark.asyncio
    async def test_search(self, httpx_mock: HTTPXMock, sample_data):
        """Test search with filters."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/projectPlanStages?category=TODO&limit=100&offset=0",
            json={"error": None, "data": [sample_data]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ProjectplanstagesResource(http)
            results = await resource.search(category="TODO")

            assert len(results) == 1

    @pytest.mark.asyncio
    async def test_update(self, httpx_mock: HTTPXMock, sample_data):
        """Test updating a projectplanstage."""
        updated_data = {**sample_data, "name": "Updated Name"}
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/projectPlanStages/1",
            method="PUT",
            json={"error": None, "data": updated_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ProjectplanstagesResource(http)
            result = await resource.update(1, name="Updated Name")

            assert result.name == "Updated Name"

    @pytest.mark.asyncio
    async def test_delete(self, httpx_mock: HTTPXMock):
        """Test deleting a projectplanstage."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/projectPlanStages/1",
            method="DELETE",
            json={"error": None, "data": {"success": True}},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ProjectplanstagesResource(http)
            result = await resource.delete(1)

            assert result["data"].get("success") is True

    @pytest.mark.asyncio
    async def test_bulk_update(self, httpx_mock: HTTPXMock, sample_data):
        """Test bulk update operation."""
        # Mock responses for each update
        for i in [1, 2, 3]:
            httpx_mock.add_response(
                url=f"https://power.upsales.com/api/v2/projectPlanStages/{i}",
                method="PUT",
                json={"error": None, "data": {**sample_data, "id": i}},
            )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ProjectplanstagesResource(http)
            results = await resource.bulk_update(
                ids=[1, 2, 3],
                data={"name": "Updated"},
            )

            assert len(results) == 3
            assert all(isinstance(item, ProjectPlanStage) for item in results)

    @pytest.mark.asyncio
    async def test_bulk_delete(self, httpx_mock: HTTPXMock):
        """Test bulk delete operation."""
        # Mock responses for each delete
        for i in [1, 2, 3]:
            httpx_mock.add_response(
                url=f"https://power.upsales.com/api/v2/projectPlanStages/{i}",
                method="DELETE",
                json={"error": None, "data": {"success": True}},
            )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ProjectplanstagesResource(http)
            results = await resource.bulk_delete(ids=[1, 2, 3])

            assert len(results) == 3
