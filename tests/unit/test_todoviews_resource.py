"""
Unit tests for TodoViewsResource.

Note: TodoViews endpoint is different from standard CRUD resources:
- Returns list of predefined view configurations (34 items)
- Read-only (no create/update/delete, no ID field)
- Used for filtering activities by time period and type

Tests cover:
- list() - Get all todo views
- get_by_name() - Find view by name
- get_by_group() - Get views for time period
- get_by_type() - Get views for activity type
- get_available_groups() - Get all group names
- get_available_types() - Get all type names
- TodoView computed fields
"""

import pytest
from pytest_httpx import HTTPXMock

from upsales.http import HTTPClient
from upsales.models.todoViews import TodoView
from upsales.resources.todoViews import TodoViewsResource


class TestTodoViewsResource:
    """Test TodoViewsResource operations."""

    @pytest.fixture
    def sample_views(self):
        """Sample todo views data for testing."""
        return [
            {"name": "all", "group": "open", "type": "all"},
            {"name": "appointmentsAll", "group": "open", "type": "appointments"},
            {"name": "todosAll", "group": "open", "type": "todos"},
            {"name": "phonecallsAll", "group": "open", "type": "phonecalls"},
            {"name": "allToday", "group": "today", "type": "all"},
            {"name": "appointmentsToday", "group": "today", "type": "appointments"},
            {"name": "todosToday", "group": "today", "type": "todos"},
            {"name": "phonecallsToday", "group": "today", "type": "phonecalls"},
            {"name": "allLate", "group": "late", "type": "all"},
            {"name": "appointmentsLate", "group": "late", "type": "appointments"},
            {"name": "todosLate", "group": "late", "type": "todos"},
            {"name": "phonecallsLate", "group": "late", "type": "phonecalls"},
            {"name": "allCompletedToday", "group": "completedToday", "type": "all"},
            {"name": "hotLeads", "group": "leads", "type": "hot"},
            {"name": "coldCallLeads", "group": "leads", "type": "coldcall"},
        ]

    @pytest.mark.asyncio
    async def test_list_success(self, httpx_mock: HTTPXMock, sample_views):
        """Test listing all todo views."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/todoViews",
            json={"error": None, "data": sample_views},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = TodoViewsResource(http)
            views = await resource.list()

            assert len(views) == len(sample_views)
            assert all(isinstance(v, TodoView) for v in views)
            assert views[0].name == "all"
            assert views[0].group == "open"
            assert views[0].type == "all"

    @pytest.mark.asyncio
    async def test_get_by_name_found(self, resource, httpx_mock: HTTPXMock, sample_views):
        """Test finding view by name when it exists."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/todoViews",
            json={"error": None, "data": sample_views},
        )

        view = await resource.get_by_name("allToday")

        assert view is not None
        assert view.name == "allToday"
        assert view.group == "today"
        assert view.type == "all"

    @pytest.mark.asyncio
    async def test_get_by_name_not_found(self, resource, httpx_mock: HTTPXMock, sample_views):
        """Test finding view by name when it doesn't exist."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/todoViews",
            json={"error": None, "data": sample_views},
        )

        view = await resource.get_by_name("nonexistent")

        assert view is None

    @pytest.mark.asyncio
    async def test_get_by_group(self, resource, httpx_mock: HTTPXMock, sample_views):
        """Test getting views by time period group."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/todoViews",
            json={"error": None, "data": sample_views},
        )

        views = await resource.get_by_group("today")

        assert len(views) == 4
        assert all(v.group == "today" for v in views)
        assert {v.type for v in views} == {"all", "appointments", "todos", "phonecalls"}

    @pytest.mark.asyncio
    async def test_get_by_group_empty(self, resource, httpx_mock: HTTPXMock, sample_views):
        """Test getting views by group with no matches."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/todoViews",
            json={"error": None, "data": sample_views},
        )

        views = await resource.get_by_group("nonexistent")

        assert len(views) == 0

    @pytest.mark.asyncio
    async def test_get_by_type(self, resource, httpx_mock: HTTPXMock, sample_views):
        """Test getting views by activity type."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/todoViews",
            json={"error": None, "data": sample_views},
        )

        views = await resource.get_by_type("appointments")

        assert len(views) == 3
        assert all(v.type == "appointments" for v in views)
        assert {v.group for v in views} == {"open", "today", "late"}

    @pytest.mark.asyncio
    async def test_get_by_type_empty(self, resource, httpx_mock: HTTPXMock, sample_views):
        """Test getting views by type with no matches."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/todoViews",
            json={"error": None, "data": sample_views},
        )

        views = await resource.get_by_type("nonexistent")

        assert len(views) == 0

    @pytest.mark.asyncio
    async def test_get_available_groups(self, resource, httpx_mock: HTTPXMock, sample_views):
        """Test getting list of available groups."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/todoViews",
            json={"error": None, "data": sample_views},
        )

        groups = await resource.get_available_groups()

        assert len(groups) > 0
        assert "open" in groups
        assert "today" in groups
        assert "late" in groups
        assert "completedToday" in groups
        assert "leads" in groups
        # Should be sorted
        assert groups == sorted(groups)

    @pytest.mark.asyncio
    async def test_get_available_types(self, resource, httpx_mock: HTTPXMock, sample_views):
        """Test getting list of available types."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/todoViews",
            json={"error": None, "data": sample_views},
        )

        types = await resource.get_available_types()

        assert len(types) > 0
        assert "all" in types
        assert "appointments" in types
        assert "todos" in types
        assert "phonecalls" in types
        # Should be sorted
        assert types == sorted(types)


class TestTodoViewModel:
    """Test TodoView model computed fields."""

    def test_is_all_types(self):
        """Test is_all_types computed field."""
        view = TodoView(name="allToday", group="today", type="all")
        assert view.is_all_types is True

        view = TodoView(name="appointmentsToday", group="today", type="appointments")
        assert view.is_all_types is False

    def test_is_appointments(self):
        """Test is_appointments computed field."""
        view = TodoView(name="appointmentsToday", group="today", type="appointments")
        assert view.is_appointments is True

        view = TodoView(name="todosToday", group="today", type="todos")
        assert view.is_appointments is False

    def test_is_todos(self):
        """Test is_todos computed field."""
        view = TodoView(name="todosToday", group="today", type="todos")
        assert view.is_todos is True

        view = TodoView(name="phonecallsToday", group="today", type="phonecalls")
        assert view.is_todos is False

    def test_is_phonecalls(self):
        """Test is_phonecalls computed field."""
        view = TodoView(name="phonecallsToday", group="today", type="phonecalls")
        assert view.is_phonecalls is True

        view = TodoView(name="todosToday", group="today", type="todos")
        assert view.is_phonecalls is False

    def test_is_today_filter(self):
        """Test is_today_filter computed field."""
        view = TodoView(name="allToday", group="today", type="all")
        assert view.is_today_filter is True

        view = TodoView(name="allLate", group="late", type="all")
        assert view.is_today_filter is False

    def test_is_late_filter(self):
        """Test is_late_filter computed field."""
        view = TodoView(name="allLate", group="late", type="all")
        assert view.is_late_filter is True

        view = TodoView(name="allToday", group="today", type="all")
        assert view.is_late_filter is False

    def test_is_completed_filter(self):
        """Test is_completed_filter computed field."""
        view = TodoView(name="allCompletedToday", group="completedToday", type="all")
        assert view.is_completed_filter is True

        view = TodoView(name="allToday", group="today", type="all")
        assert view.is_completed_filter is False

    def test_is_leads_filter(self):
        """Test is_leads_filter computed field."""
        view = TodoView(name="hotLeads", group="leads", type="hot")
        assert view.is_leads_filter is True

        view = TodoView(name="allToday", group="today", type="all")
        assert view.is_leads_filter is False

    def test_display_name(self):
        """Test display_name computed field."""
        view = TodoView(name="allToday", group="today", type="all")
        assert view.display_name == "All Today"

        view = TodoView(name="appointmentsWeek", group="week", type="appointments")
        assert view.display_name == "Appointments Week"

        view = TodoView(name="todosLate", group="late", type="todos")
        assert view.display_name == "Todos Late"

        view = TodoView(name="hotLeads", group="leads", type="hot")
        assert view.display_name == "Hot Leads"
