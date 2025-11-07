"""
Unit tests for ProjectsResource.

Tests CRUD operations and custom methods for projects endpoint.
"""

import pytest
from pytest_httpx import HTTPXMock

from upsales.http import HTTPClient
from upsales.models.projects import Project
from upsales.resources.projects import ProjectsResource


class TestProjectsResourceCRUD:
    """Test CRUD operations for ProjectsResource."""

    @pytest.fixture
    def sample_data(self):
        """Sample project data for testing."""
        return {
            "id": 1,
            "name": "Q1 Campaign",
            "startDate": "2025-01-01",
            "endDate": "2025-03-31",
            "quota": 1000,
            "notes": "First quarter marketing campaign",
            "active": 1,
            "isCallList": False,
            "userEditable": True,
            "userRemovable": True,
            "regDate": "2025-01-01T00:00:00Z",
            "users": [{"id": 1, "name": "John Doe", "email": "john@example.com"}],
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
                {**sample_data, "id": 2, "name": "Q2 Campaign", "quota": 1500},
            ],
        }

    @pytest.mark.asyncio
    async def test_create(self, httpx_mock: HTTPXMock, sample_data):
        """Test creating a project."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/projects",
            method="POST",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ProjectsResource(http)
            result = await resource.create(
                name="Q1 Campaign",
                startDate="2025-01-01",
                quota=1000,
                active=1,
            )

            assert isinstance(result, Project)
            assert result.id == 1
            assert result.name == "Q1 Campaign"
            assert result.quota == 1000
            assert result.is_active

    @pytest.mark.asyncio
    async def test_get(self, httpx_mock: HTTPXMock, sample_data):
        """Test getting a single project."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/projects/1",
            json={"error": None, "data": sample_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ProjectsResource(http)
            result = await resource.get(1)

            assert isinstance(result, Project)
            assert result.id == 1
            assert result.name == "Q1 Campaign"
            assert result.is_active
            assert result.has_users

    @pytest.mark.asyncio
    async def test_list(self, httpx_mock: HTTPXMock, sample_list_response):
        """Test listing projects with pagination."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/projects?limit=10&offset=0",
            json=sample_list_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ProjectsResource(http)
            results = await resource.list(limit=10, offset=0)

            assert len(results) == 2
            assert all(isinstance(r, Project) for r in results)
            assert results[0].name == "Q1 Campaign"
            assert results[1].name == "Q2 Campaign"

    @pytest.mark.asyncio
    async def test_list_all(self, httpx_mock: HTTPXMock, sample_list_response):
        """Test list_all with auto-pagination."""
        # First page
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/projects?limit=100&offset=0",
            json=sample_list_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ProjectsResource(http)
            results = await resource.list_all()

            assert len(results) == 2
            assert all(isinstance(r, Project) for r in results)

    @pytest.mark.asyncio
    async def test_update(self, httpx_mock: HTTPXMock, sample_data):
        """Test updating a project."""
        updated_data = {**sample_data, "name": "Q1 Marketing", "quota": 1200}

        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/projects/1",
            method="PUT",
            json={"error": None, "data": updated_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ProjectsResource(http)
            result = await resource.update(1, name="Q1 Marketing", quota=1200)

            assert isinstance(result, Project)
            assert result.id == 1
            assert result.name == "Q1 Marketing"
            assert result.quota == 1200

    @pytest.mark.asyncio
    async def test_delete(self, httpx_mock: HTTPXMock):
        """Test deleting a project."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/projects/1",
            method="DELETE",
            json={"error": None, "data": {"success": True}},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ProjectsResource(http)
            result = await resource.delete(1)

            assert isinstance(result, dict)
            assert result == {"error": None, "data": {"success": True}}

    @pytest.mark.asyncio
    async def test_search(self, httpx_mock: HTTPXMock, sample_data):
        """Test search with filters."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/projects?active=1&limit=100&offset=0",
            json={"error": None, "data": [sample_data]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ProjectsResource(http)
            results = await resource.search(active=1)

            assert len(results) == 1
            assert results[0].is_active


class TestProjectsResourceCustomMethods:
    """Test custom methods specific to ProjectsResource."""

    @pytest.fixture
    def sample_active_project(self):
        """Sample active project data."""
        return {
            "id": 1,
            "name": "Active Campaign",
            "startDate": "2025-01-01",
            "endDate": "2025-03-31",
            "quota": 1000,
            "notes": None,
            "active": 1,
            "isCallList": False,
            "userEditable": True,
            "userRemovable": True,
            "regDate": "2025-01-01T00:00:00Z",
            "users": [],
            "custom": [],
        }

    @pytest.fixture
    def sample_inactive_project(self):
        """Sample inactive project data."""
        return {
            "id": 2,
            "name": "Archived Campaign",
            "startDate": "2024-01-01",
            "endDate": "2024-03-31",
            "quota": 500,
            "notes": None,
            "active": 0,
            "isCallList": False,
            "userEditable": True,
            "userRemovable": True,
            "regDate": "2024-01-01T00:00:00Z",
            "users": [],
            "custom": [],
        }

    @pytest.fixture
    def sample_call_list(self):
        """Sample call list project data."""
        return {
            "id": 3,
            "name": "Cold Calling List",
            "startDate": "2025-01-01",
            "endDate": None,
            "quota": 100,
            "notes": None,
            "active": 1,
            "isCallList": True,
            "userEditable": True,
            "userRemovable": True,
            "regDate": "2025-01-01T00:00:00Z",
            "users": [],
            "custom": [],
        }

    @pytest.mark.asyncio
    async def test_get_active(self, httpx_mock: HTTPXMock, sample_active_project):
        """Test get_active() returns active projects."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/projects?active=1&limit=100&offset=0",
            json={"error": None, "data": [sample_active_project]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ProjectsResource(http)
            results = await resource.get_active()

            assert len(results) == 1
            assert results[0].is_active
            assert results[0].name == "Active Campaign"

    @pytest.mark.asyncio
    async def test_get_inactive(self, httpx_mock: HTTPXMock, sample_inactive_project):
        """Test get_inactive() returns inactive projects."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/projects?active=0&limit=100&offset=0",
            json={"error": None, "data": [sample_inactive_project]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ProjectsResource(http)
            results = await resource.get_inactive()

            assert len(results) == 1
            assert not results[0].is_active
            assert results[0].name == "Archived Campaign"

    @pytest.mark.asyncio
    async def test_get_by_user(self, httpx_mock: HTTPXMock):
        """Test get_by_user() filters projects by user."""
        project_with_user = {
            "id": 1,
            "name": "User Project",
            "startDate": "2025-01-01",
            "endDate": None,
            "quota": 1000,
            "notes": None,
            "active": 1,
            "isCallList": False,
            "userEditable": True,
            "userRemovable": True,
            "regDate": "2025-01-01T00:00:00Z",
            "users": [{"id": 123, "name": "John Doe", "email": "john@example.com"}],
            "custom": [],
        }

        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/projects?limit=100&offset=0&users.id=123",
            json={"error": None, "data": [project_with_user]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ProjectsResource(http)
            results = await resource.get_by_user(123)

            assert len(results) == 1
            assert results[0].has_users
            assert any(u.id == 123 for u in results[0].users)

    @pytest.mark.asyncio
    async def test_get_call_lists(self, httpx_mock: HTTPXMock, sample_call_list):
        """Test get_call_lists() returns projects marked as call lists."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/projects?isCallList=true&limit=100&offset=0",
            json={"error": None, "data": [sample_call_list]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = ProjectsResource(http)
            results = await resource.get_call_lists()

            assert len(results) == 1
            assert results[0].isCallList
            assert results[0].name == "Cold Calling List"


class TestProjectModelMethods:
    """Test Project model instance methods."""

    @pytest.mark.asyncio
    async def test_project_computed_fields(self):
        """Test computed fields on Project model."""
        project = Project(
            id=1,
            name="Test Project",
            startDate="2025-01-01",
            endDate="2025-03-31",
            quota=1000,
            active=1,
            isCallList=False,
            userEditable=True,
            userRemovable=True,
            regDate="2025-01-01T00:00:00Z",
            users=[{"id": 1, "name": "John", "email": "john@example.com"}],
            custom=[],
        )

        assert project.is_active is True
        assert project.has_users is True
        assert project.custom_fields is not None

    @pytest.mark.asyncio
    async def test_project_inactive(self):
        """Test inactive project computed field."""
        project = Project(
            id=2,
            name="Inactive Project",
            startDate="2024-01-01",
            endDate="2024-03-31",
            quota=500,
            active=0,
            isCallList=False,
            userEditable=True,
            userRemovable=True,
            regDate="2024-01-01T00:00:00Z",
            users=[],
            custom=[],
        )

        assert project.is_active is False
        assert project.has_users is False

    @pytest.mark.asyncio
    async def test_project_custom_fields_access(self):
        """Test custom fields access via computed field."""
        project = Project(
            id=1,
            name="Test Project",
            startDate="2025-01-01",
            quota=1000,
            active=1,
            isCallList=False,
            userEditable=True,
            userRemovable=True,
            regDate="2025-01-01T00:00:00Z",
            users=[],
            custom=[{"fieldId": 11, "value": "Test Value"}],
        )

        assert project.custom_fields[11] == "Test Value"
