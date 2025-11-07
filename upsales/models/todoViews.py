"""
TodoView models for Upsales API.

The /api/v2/todoViews endpoint returns predefined todo view filters
used in the Upsales UI for organizing activities (todos, appointments, phonecalls).

This is a read-only endpoint with no CRUD operations. The endpoint returns
34 predefined views grouped by time period (open, today, tomorrow, week, etc.)
and filtered by activity type (all, appointments, todos, phonecalls).

Example views:
    - 'allToday': All activities due today
    - 'appointmentsWeek': Appointments this week
    - 'todosLate': Overdue todos
    - 'phonecallsNoDate': Phone calls with no due date
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel as PydanticBase
from pydantic import ConfigDict, Field, computed_field

if TYPE_CHECKING:
    from upsales.client import Upsales

from upsales.validators import NonEmptyStr  # noqa: TC001


class TodoView(PydanticBase):
    """
    TodoView filter definition from /api/v2/todoViews.

    TodoViews are predefined filters for organizing activities in the Upsales UI.
    Each view has a name (identifier), group (time period), and type (activity filter).

    This is a read-only model with no ID field and no update operations.

    Attributes:
        name: View identifier (e.g., 'allToday', 'appointmentsWeek')
        group: Time period group (e.g., 'open', 'today', 'tomorrow', 'week',
               'nextweek', 'leads', 'late', 'noDate', 'completedToday')
        type: Activity type filter (e.g., 'all', 'appointments', 'todos',
              'phonecalls', 'coldcall', 'hot')

    Example:
        >>> async with Upsales.from_env() as upsales:
        ...     # Get all todo views
        ...     views = await upsales.todo_views.list()
        ...
        ...     # Find today's appointments view
        ...     today_appts = next(v for v in views if v.name == 'appointmentsToday')
        ...     print(f"Group: {today_appts.group}, Type: {today_appts.type}")
        ...
        ...     # Check if view is for overdue items
        ...     if today_appts.is_late_filter:
        ...         print("This view shows overdue items")
    """

    model_config = ConfigDict(
        frozen=False,
        validate_assignment=True,
        extra="allow",
        populate_by_name=True,
    )

    name: NonEmptyStr = Field(description="View identifier (e.g., 'allToday', 'appointmentsWeek')")
    group: NonEmptyStr = Field(
        description=(
            "Time period group: 'open', 'today', 'tomorrow', 'week', 'nextweek', "
            "'leads', 'late', 'noDate', 'completedToday'"
        )
    )
    type: NonEmptyStr = Field(
        description=(
            "Activity type filter: 'all', 'appointments', 'todos', 'phonecalls', 'coldcall', 'hot'"
        )
    )

    # Optional client reference for potential future use
    _client: Upsales | None = None

    @computed_field
    @property
    def is_all_types(self) -> bool:
        """
        Check if view includes all activity types.

        Returns:
            True if type is 'all', False otherwise.

        Example:
            >>> view.type
            'all'
            >>> view.is_all_types
            True
        """
        return self.type == "all"

    @computed_field
    @property
    def is_appointments(self) -> bool:
        """
        Check if view is for appointments only.

        Returns:
            True if type is 'appointments', False otherwise.

        Example:
            >>> view.type
            'appointments'
            >>> view.is_appointments
            True
        """
        return self.type == "appointments"

    @computed_field
    @property
    def is_todos(self) -> bool:
        """
        Check if view is for todos only.

        Returns:
            True if type is 'todos', False otherwise.

        Example:
            >>> view.type
            'todos'
            >>> view.is_todos
            True
        """
        return self.type == "todos"

    @computed_field
    @property
    def is_phonecalls(self) -> bool:
        """
        Check if view is for phone calls only.

        Returns:
            True if type is 'phonecalls', False otherwise.

        Example:
            >>> view.type
            'phonecalls'
            >>> view.is_phonecalls
            True
        """
        return self.type == "phonecalls"

    @computed_field
    @property
    def is_today_filter(self) -> bool:
        """
        Check if view shows activities for today.

        Returns:
            True if group is 'today', False otherwise.

        Example:
            >>> view.group
            'today'
            >>> view.is_today_filter
            True
        """
        return self.group == "today"

    @computed_field
    @property
    def is_late_filter(self) -> bool:
        """
        Check if view shows overdue activities.

        Returns:
            True if group is 'late', False otherwise.

        Example:
            >>> view.group
            'late'
            >>> view.is_late_filter
            True
        """
        return self.group == "late"

    @computed_field
    @property
    def is_completed_filter(self) -> bool:
        """
        Check if view shows completed activities.

        Returns:
            True if group is 'completedToday', False otherwise.

        Example:
            >>> view.group
            'completedToday'
            >>> view.is_completed_filter
            True
        """
        return self.group == "completedToday"

    @computed_field
    @property
    def is_leads_filter(self) -> bool:
        """
        Check if view shows lead-related activities.

        Returns:
            True if group is 'leads', False otherwise.

        Example:
            >>> view.group
            'leads'
            >>> view.is_leads_filter
            True
        """
        return self.group == "leads"

    @computed_field
    @property
    def display_name(self) -> str:
        """
        Generate human-readable display name from view identifier.

        Converts camelCase name to readable format by inserting spaces
        before capital letters.

        Returns:
            Human-readable view name.

        Example:
            >>> view.name
            'appointmentsToday'
            >>> view.display_name
            'Appointments Today'
        """
        # Insert space before capital letters and capitalize
        import re

        spaced = re.sub(r"(?<!^)(?=[A-Z])", " ", self.name)
        return spaced.title()
