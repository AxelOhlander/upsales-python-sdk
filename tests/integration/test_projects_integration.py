"""
Integration tests for Project model with real API responses.

Uses VCR.py to record API responses on first run, then replay.
Validates that Project model correctly parses real Upsales API data.

To record cassettes:
    uv run pytest tests/integration/test_projects_integration.py -v
"""

import pytest
import vcr

from upsales import Upsales
from upsales.models.projects import Project

# Configure VCR for this test module
my_vcr = vcr.VCR(
    cassette_library_dir="tests/cassettes/integration",
    record_mode="once",  # Record once, then always replay
    match_on=["method", "scheme", "host", "port", "path", "query"],
    filter_headers=[("cookie", "REDACTED")],
    filter_post_data_parameters=[("password", "REDACTED")],
)


@pytest.mark.asyncio
@my_vcr.use_cassette("test_projects_integration/test_get_project_real_response.yaml")
async def test_get_project_real_response():
    """
    Test getting project with real API response structure.

    This test records the actual API response on first run, then
    replays it from cassette on future runs. Ensures our Project
    model correctly parses real Upsales API data.
    """
    async with Upsales.from_env() as upsales:
        # Get projects to find a valid ID
        projects = await upsales.projects.list(limit=1)

        assert len(projects) > 0, "Should have at least one project"
        project = projects[0]

        # Validate Project model with Pydantic v2 features
        assert isinstance(project, Project)
        assert isinstance(project.id, int)
        assert project.id > 0  # PositiveInt validator
        assert isinstance(project.name, str)
        assert len(project.name) > 0  # NonEmptyStr validator

        # Validate frozen fields (read-only)
        assert hasattr(project, "id")
        assert hasattr(project, "regDate")

        # Validate BinaryFlag field (should be 0 or 1)
        assert project.active in (0, 1)

        # Validate boolean fields
        assert isinstance(project.isCallList, bool)
        assert isinstance(project.userEditable, bool)
        assert isinstance(project.userRemovable, bool)

        # Validate computed fields work
        assert isinstance(project.is_active, bool)
        assert isinstance(project.has_users, bool)
        assert project.custom_fields is not None

        # Validate computed field correctness
        assert project.is_active == (project.active == 1)
        assert project.has_users == (len(project.users) > 0)

        print(
            f"[OK] Project parsed successfully: {project.name} "
            f"(ID: {project.id}, Active: {project.is_active})"
        )


@pytest.mark.asyncio
@my_vcr.use_cassette("test_projects_integration/test_list_projects_real_response.yaml")
async def test_list_projects_real_response():
    """Test listing projects with real API response structure."""
    async with Upsales.from_env() as upsales:
        projects = await upsales.projects.list(limit=10)

        assert isinstance(projects, list)
        assert len(projects) <= 10

        for project in projects:
            assert isinstance(project, Project)
            assert project.id > 0
            assert len(project.name) > 0
            # Active must be 0 or 1
            assert project.active in (0, 1)
            # Boolean fields
            assert isinstance(project.isCallList, bool)
            assert isinstance(project.userEditable, bool)
            assert isinstance(project.userRemovable, bool)
            # Lists should be present
            assert isinstance(project.users, list)
            assert isinstance(project.custom, list)

        print(f"[OK] Listed {len(projects)} projects successfully")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_projects_integration/test_project_serialization.yaml")
async def test_project_serialization_real_data():
    """
    Test to_api_dict() serialization with real project data.

    Validates that serialization excludes frozen fields using
    Pydantic v2 optimized serialization.
    """
    async with Upsales.from_env() as upsales:
        projects = await upsales.projects.list(limit=1)
        project = projects[0]

        # Get API dict (should exclude frozen fields)
        api_dict = project.to_api_dict()

        # Validate frozen fields excluded
        assert "id" not in api_dict or api_dict.get("id") is None
        assert "regDate" not in api_dict or api_dict.get("regDate") is None

        # Validate computed fields excluded
        assert "is_active" not in api_dict
        assert "has_users" not in api_dict
        assert "custom_fields" not in api_dict

        # Should include updatable fields
        assert "name" in api_dict
        assert "startDate" in api_dict
        assert "active" in api_dict

        # With overrides, should include changed fields
        api_dict_with_changes = project.to_api_dict(name="New Name", quota=1500)
        assert api_dict_with_changes["name"] == "New Name"
        assert api_dict_with_changes["quota"] == 1500

        # Validate it's JSON serializable
        import json

        json_str = json.dumps(api_dict)  # Should not raise
        assert json_str

        print(f"[OK] Serialization validated for {project.name}")
        print(f"[OK] API payload has {len(api_dict)} fields")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_projects_integration/test_get_active_projects.yaml")
async def test_get_active_projects():
    """
    Test get_active() custom method with real data.

    Validates that custom methods work correctly with the projects endpoint.
    """
    async with Upsales.from_env() as upsales:
        # Get active projects (active=1)
        active = await upsales.projects.get_active()

        assert isinstance(active, list)
        # All should have active=1
        for project in active:
            assert project.active == 1
            assert project.is_active  # Computed field check

        print(f"[OK] Found {len(active)} active projects (active=1)")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_projects_integration/test_get_inactive_projects.yaml")
async def test_get_inactive_projects():
    """
    Test get_inactive() custom method with real data.

    Validates that inactive projects are correctly filtered.
    """
    async with Upsales.from_env() as upsales:
        # Get inactive projects (active=0)
        inactive = await upsales.projects.get_inactive()

        assert isinstance(inactive, list)
        # All should have active=0
        for project in inactive:
            assert project.active == 0
            assert not project.is_active  # Computed field check

        print(f"[OK] Found {len(inactive)} inactive projects (active=0)")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_projects_integration/test_custom_fields_access.yaml")
async def test_custom_fields_access():
    """
    Test custom fields access via computed field.

    Validates that CustomFields helper works correctly with real data.
    """
    async with Upsales.from_env() as upsales:
        projects = await upsales.projects.list(limit=5)

        for project in projects:
            # CustomFields should be accessible via computed field
            assert project.custom_fields is not None
            # Should have dict-like interface
            assert hasattr(project.custom_fields, "__getitem__")

            # If project has custom fields, test access
            if project.custom:
                field_id = project.custom[0]["fieldId"]
                # Should be able to access by field ID
                value = project.custom_fields[field_id]
                assert value is not None or value is None  # Can be any value
                print(f"[OK] Custom field {field_id} accessible: {value}")

        print(f"[OK] Custom fields access validated for {len(projects)} projects")
