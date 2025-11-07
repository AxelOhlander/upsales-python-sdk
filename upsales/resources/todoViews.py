"""
TodoViews resource manager for Upsales API.

Manages /api/v2/todoViews endpoint operations.

IMPORTANT: TodoViews endpoint is read-only and returns a list of predefined
view configurations. These views are used in the Upsales UI to filter activities
(todos, appointments, phone calls) by time period and type.

This endpoint has no CRUD operations - it only supports listing all views.
No ID field exists, and views cannot be created, updated, or deleted via API.

This resource manager provides:
- list(): Get all predefined todo views (34 views)
- get_by_name(): Find view by name identifier
- get_by_group(): Get views for specific time period
- get_by_type(): Get views for specific activity type

Standard operations like create(), update(), delete(), get(id) are not applicable.
"""

from __future__ import annotations

import builtins
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from upsales.http import HTTPClient

from upsales.models.todoViews import TodoView


class TodoViewsResource:
    """
    Resource manager for /api/v2/todoViews endpoint.

    Note: Unlike most resources, todoViews is read-only with no ID field
    and no CRUD operations. It returns a fixed list of 34 predefined view
    configurations used in the Upsales UI.

    Args:
        http: HTTP client instance for making API requests.

    Attributes:
        _http: HTTP client for API requests.
        _endpoint: API endpoint path (/todoViews).

    Example:
        >>> async with Upsales.from_env() as upsales:
        ...     # Get all todo views
        ...     views = await upsales.todo_views.list()
        ...     print(f"Total views: {len(views)}")
        ...
        ...     # Find specific view
        ...     today_view = await upsales.todo_views.get_by_name('allToday')
        ...     print(f"View: {today_view.display_name}")
        ...
        ...     # Get views by time period
        ...     today_views = await upsales.todo_views.get_by_group('today')
        ...     for view in today_views:
        ...         print(f"- {view.display_name}")
        ...
        ...     # Get views by activity type
        ...     appt_views = await upsales.todo_views.get_by_type('appointments')
        ...     print(f"Found {len(appt_views)} appointment views")
    """

    def __init__(self, http: HTTPClient) -> None:
        """
        Initialize todoViews resource manager.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/todoViews"

    async def list(self) -> list[TodoView]:
        """
        Get all predefined todo views.

        Returns all 34 predefined view configurations used in the Upsales UI
        for filtering activities by time period and type.

        Returns:
            List of all TodoView configurations (34 items).

        Raises:
            UpsalesError: If API request fails.

        Example:
            >>> views = await upsales.todo_views.list()
            >>> len(views)
            34
            >>> views[0].name
            'all'
            >>> views[0].group
            'open'
            >>> views[0].type
            'all'
        """
        response = await self._http.get(self._endpoint)
        # Extract data array from response wrapper
        data_list = response.get("data", [])
        return [TodoView(**item, _client=self._http._upsales_client) for item in data_list]

    async def get_by_name(self, name: str) -> TodoView | None:
        """
        Find todo view by name identifier.

        Searches for a view with the exact name match. Name is case-sensitive.

        Args:
            name: View identifier (e.g., 'allToday', 'appointmentsWeek', 'todosLate').

        Returns:
            TodoView if found, None otherwise.

        Raises:
            UpsalesError: If API request fails.

        Example:
            >>> # Get today's view
            >>> view = await upsales.todo_views.get_by_name('allToday')
            >>> view.group
            'today'
            >>> view.type
            'all'
            >>>
            >>> # Get late appointments view
            >>> late_appts = await upsales.todo_views.get_by_name('appointmentsLate')
            >>> late_appts.is_late_filter
            True
        """
        views = await self.list()
        return next((v for v in views if v.name == name), None)

    async def get_by_group(self, group: str) -> builtins.list[TodoView]:
        """
        Get all views for a specific time period group.

        Valid groups:
            - 'open': All open activities
            - 'today': Activities due today
            - 'tomorrow': Activities due tomorrow
            - 'week': Activities this week
            - 'nextweek': Activities next week
            - 'leads': Lead-related activities
            - 'late': Overdue activities
            - 'noDate': Activities with no due date
            - 'completedToday': Activities completed today

        Args:
            group: Time period group name (case-sensitive).

        Returns:
            List of views matching the group (usually 4 views per group:
            all, appointments, todos, phonecalls).

        Raises:
            UpsalesError: If API request fails.

        Example:
            >>> # Get all today's views
            >>> today_views = await upsales.todo_views.get_by_group('today')
            >>> [v.name for v in today_views]
            ['allToday', 'appointmentsToday', 'todosToday', 'phonecallsToday']
            >>>
            >>> # Get overdue views
            >>> late_views = await upsales.todo_views.get_by_group('late')
            >>> all(v.is_late_filter for v in late_views)
            True
        """
        views = await self.list()
        return [v for v in views if v.group == group]

    async def get_by_type(self, activity_type: str) -> builtins.list[TodoView]:
        """
        Get all views for a specific activity type.

        Valid types:
            - 'all': All activity types
            - 'appointments': Appointments only
            - 'todos': Todos only
            - 'phonecalls': Phone calls only
            - 'coldcall': Cold call leads
            - 'hot': Hot leads

        Args:
            activity_type: Activity type filter (case-sensitive).

        Returns:
            List of views matching the activity type (usually 9-11 views
            per type, covering different time periods).

        Raises:
            UpsalesError: If API request fails.

        Example:
            >>> # Get all appointment views
            >>> appt_views = await upsales.todo_views.get_by_type('appointments')
            >>> [v.name for v in appt_views]
            ['appointmentsAll', 'appointmentsToday', 'appointmentsTomorrow', ...]
            >>>
            >>> # Get all 'all types' views
            >>> all_views = await upsales.todo_views.get_by_type('all')
            >>> all(v.is_all_types for v in all_views)
            True
        """
        views = await self.list()
        return [v for v in views if v.type == activity_type]

    async def get_available_groups(self) -> builtins.list[str]:
        """
        Get list of all available time period groups.

        Returns unique group names found in the view configurations.

        Returns:
            List of unique group names (e.g., ['open', 'today', 'tomorrow', ...]).

        Raises:
            UpsalesError: If API request fails.

        Example:
            >>> groups = await upsales.todo_views.get_available_groups()
            >>> 'today' in groups
            True
            >>> 'late' in groups
            True
        """
        views = await self.list()
        return sorted({v.group for v in views})

    async def get_available_types(self) -> builtins.list[str]:
        """
        Get list of all available activity types.

        Returns unique type names found in the view configurations.

        Returns:
            List of unique type names (e.g., ['all', 'appointments', 'todos', ...]).

        Raises:
            UpsalesError: If API request fails.

        Example:
            >>> types = await upsales.todo_views.get_available_types()
            >>> 'appointments' in types
            True
            >>> 'todos' in types
            True
        """
        views = await self.list()
        return sorted({v.type for v in views})
