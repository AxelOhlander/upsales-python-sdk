"""
Integration tests for TodoViews model with real API responses.

Uses VCR.py to record API responses on first run, then replay them.
Validates that our Pydantic v2 models correctly parse real API data.

To record cassettes:
    uv run pytest tests/integration/test_todoviews_integration.py -v

To re-record (delete cassette first):
    rm tests/cassettes/integration/test_todoviews_integration/*.yaml
    uv run pytest tests/integration/test_todoviews_integration.py -v
"""

import pytest
import vcr

from upsales import Upsales
from upsales.models.todo_views import TodoView

# Configure VCR for these tests
my_vcr = vcr.VCR(
    cassette_library_dir="tests/cassettes/integration",
    record_mode="once",  # Record once, then always replay
    match_on=["method", "scheme", "host", "port", "path"],
    filter_headers=[
        ("cookie", "REDACTED"),
        ("authorization", "REDACTED"),
    ],
    filter_post_data_parameters=[
        ("password", "REDACTED"),
    ],
)


@pytest.mark.asyncio
@my_vcr.use_cassette("test_todoviews_integration/test_list_todoviews_real_response.yaml")
async def test_list_todoviews_real_response():
    """
    Test listing todo views with real API response structure.

    This test records the actual API response on first run, then
    replays it from cassette on future runs. This ensures our TodoView
    model correctly parses real Upsales API data.

    Cassette: tests/cassettes/integration/test_todoviews_integration/test_list_todoviews_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        # Get all todo views (or replay from cassette)
        views = await upsales.todo_views.list()

        # Validate we got a list
        assert isinstance(views, list)
        assert len(views) > 0, "Should have at least one todo view"

        # Should have 34 predefined views
        assert len(views) == 34, "Upsales should return 34 predefined todo views"

        # Validate all are TodoView objects
        assert all(isinstance(v, TodoView) for v in views)

        # Validate fields on each view
        for view in views:
            assert isinstance(view.name, str)
            assert view.name  # Should not be empty
            assert isinstance(view.group, str)
            assert view.group  # Should not be empty
            assert isinstance(view.type, str)
            assert view.type  # Should not be empty

        # Validate computed fields work
        for view in views:
            assert isinstance(view.is_all_types, bool)
            assert isinstance(view.is_appointments, bool)
            assert isinstance(view.is_todos, bool)
            assert isinstance(view.is_phonecalls, bool)
            assert isinstance(view.is_today_filter, bool)
            assert isinstance(view.is_late_filter, bool)
            assert isinstance(view.is_completed_filter, bool)
            assert isinstance(view.is_leads_filter, bool)
            assert isinstance(view.display_name, str)
            assert view.display_name  # Should not be empty

        print(f"[OK] TodoViews parsed successfully: {len(views)} views")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_todoviews_integration/test_get_by_name_real_response.yaml")
async def test_get_by_name_real_response():
    """
    Test getting todo view by name with real API response.

    Validates that view lookup by name works correctly.

    Cassette: tests/cassettes/integration/test_todoviews_integration/test_get_by_name_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        # Get specific view by name (or replay from cassette)
        view = await upsales.todo_views.get_by_name("allToday")

        assert view is not None, "Should find 'allToday' view"
        assert isinstance(view, TodoView)
        assert view.name == "allToday"
        assert view.group == "today"
        assert view.type == "all"

        # Validate computed fields
        assert view.is_all_types is True
        assert view.is_today_filter is True
        assert view.display_name == "All Today"

        print(f"[OK] Found view: {view.name} ({view.display_name})")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_todoviews_integration/test_get_by_group_real_response.yaml")
async def test_get_by_group_real_response():
    """
    Test getting todo views by group with real API response.

    Validates that filtering by time period group works correctly.

    Cassette: tests/cassettes/integration/test_todoviews_integration/test_get_by_group_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        # Get views for "today" group (or replay from cassette)
        views = await upsales.todo_views.get_by_group("today")

        assert isinstance(views, list)
        assert len(views) > 0, "Should find views for 'today' group"
        assert len(views) == 4, (
            "Should have 4 views for 'today' (all, appointments, todos, phonecalls)"
        )

        # All should be in "today" group
        assert all(v.group == "today" for v in views)

        # Should have one of each type
        types = {v.type for v in views}
        assert types == {"all", "appointments", "todos", "phonecalls"}

        # Validate computed fields
        assert all(v.is_today_filter for v in views)

        print(f"[OK] Found {len(views)} views for group 'today'")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_todoviews_integration/test_get_by_type_real_response.yaml")
async def test_get_by_type_real_response():
    """
    Test getting todo views by type with real API response.

    Validates that filtering by activity type works correctly.

    Cassette: tests/cassettes/integration/test_todoviews_integration/test_get_by_type_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        # Get views for "appointments" type (or replay from cassette)
        views = await upsales.todo_views.get_by_type("appointments")

        assert isinstance(views, list)
        assert len(views) > 0, "Should find views for 'appointments' type"

        # All should be "appointments" type
        assert all(v.type == "appointments" for v in views)

        # Validate computed fields
        assert all(v.is_appointments for v in views)
        assert all(not v.is_todos for v in views)
        assert all(not v.is_phonecalls for v in views)

        # Should have views from different time periods
        groups = {v.group for v in views}
        assert len(groups) > 1, "Should have appointments views from multiple time periods"

        print(f"[OK] Found {len(views)} views for type 'appointments'")


@pytest.mark.asyncio
@my_vcr.use_cassette(
    "test_todoviews_integration/test_available_groups_and_types_real_response.yaml"
)
async def test_available_groups_and_types_real_response():
    """
    Test getting available groups and types with real API response.

    Validates that group and type enumeration works correctly.

    Cassette: tests/cassettes/integration/test_todoviews_integration/test_available_groups_and_types_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        # Get available groups (or replay from cassette)
        groups = await upsales.todo_views.get_available_groups()

        assert isinstance(groups, list)
        assert len(groups) > 0
        # Should be sorted
        assert groups == sorted(groups)
        # Check for expected groups
        expected_groups = [
            "open",
            "today",
            "tomorrow",
            "week",
            "nextweek",
            "late",
            "noDate",
            "completedToday",
            "leads",
        ]
        for group in expected_groups:
            assert group in groups, f"Expected group '{group}' not found"

        print(f"[OK] Available groups: {groups}")

        # Get available types
        types = await upsales.todo_views.get_available_types()

        assert isinstance(types, list)
        assert len(types) > 0
        # Should be sorted
        assert types == sorted(types)
        # Check for expected types
        expected_types = ["all", "appointments", "todos", "phonecalls"]
        for typ in expected_types:
            assert typ in types, f"Expected type '{typ}' not found"

        print(f"[OK] Available types: {types}")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_todoviews_integration/test_specific_views_validation.yaml")
async def test_specific_views_validation():
    """
    Test validation of specific common views.

    Validates that commonly used views exist and have correct properties.

    Cassette: tests/cassettes/integration/test_todoviews_integration/test_specific_views_validation.yaml
    """
    async with Upsales.from_env() as upsales:
        # Test "allToday" view
        all_today = await upsales.todo_views.get_by_name("allToday")
        assert all_today is not None
        assert all_today.group == "today"
        assert all_today.type == "all"
        assert all_today.is_today_filter is True
        assert all_today.is_all_types is True

        # Test "appointmentsLate" view
        appts_late = await upsales.todo_views.get_by_name("appointmentsLate")
        assert appts_late is not None
        assert appts_late.group == "late"
        assert appts_late.type == "appointments"
        assert appts_late.is_late_filter is True
        assert appts_late.is_appointments is True

        # Test "todosNoDate" view
        todos_nodate = await upsales.todo_views.get_by_name("todosNoDate")
        assert todos_nodate is not None
        assert todos_nodate.group == "noDate"
        assert todos_nodate.type == "todos"
        assert todos_nodate.is_todos is True

        # Test "hotLeads" view
        hot_leads = await upsales.todo_views.get_by_name("hotLeads")
        assert hot_leads is not None
        assert hot_leads.group == "leads"
        assert hot_leads.type == "hot"
        assert hot_leads.is_leads_filter is True

        # Test "allCompletedToday" view
        completed = await upsales.todo_views.get_by_name("allCompletedToday")
        assert completed is not None
        assert completed.group == "completedToday"
        assert completed.type == "all"
        assert completed.is_completed_filter is True
        assert completed.is_all_types is True

        print("[OK] All specific views validated successfully")
