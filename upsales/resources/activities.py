"""
Activities resource manager for Upsales API.

Provides methods to interact with the /activities endpoint.

Example:
    >>> async with Upsales(token="...") as upsales:
    ...     activity = await upsales.activities.get(1)
    ...     activities = await upsales.activities.list(limit=10)
    ...     appointments = await upsales.activities.get_appointments()
"""

from upsales.http import HTTPClient
from upsales.models.activities import Activity, PartialActivity
from upsales.resources.base import BaseResource


class ActivitiesResource(BaseResource[Activity, PartialActivity]):
    """
    Resource manager for Activity endpoint.

    Inherits standard CRUD operations from BaseResource:
    - create(**data) - Create new activity
    - get(id) - Get single activity
    - list(limit, offset, **params) - List activities with pagination
    - list_all(**params) - Auto-paginated list of all activities
    - search(**filters) - Search with comparison operators
    - update(id, **data) - Update activity
    - delete(id) - Delete activity
    - bulk_update(ids, data, max_concurrent) - Parallel updates
    - bulk_delete(ids, max_concurrent) - Parallel deletes

    Example:
        >>> activities = ActivitiesResource(http_client)
        >>> activity = await activities.get(1)
        >>> all_tasks = await activities.get_tasks()
        >>> closed = await activities.search(closeDate=">=2025-11-01")
    """

    def __init__(self, http: HTTPClient):
        """
        Initialize activities resource manager.

        Args:
            http: HTTP client for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/activities",
            model_class=Activity,
            partial_class=PartialActivity,
        )

    async def get_appointments(self) -> list[Activity]:
        """
        Get all appointments (isAppointment=1).

        Returns:
            List of activities that are appointments.

        Example:
            >>> appointments = await upsales.activities.get_appointments()
            >>> all(a.is_appointment for a in appointments)
            True
        """
        return await self.list_all(isAppointment=1)

    async def get_tasks(self) -> list[Activity]:
        """
        Get all tasks (isAppointment=0).

        Returns:
            List of activities that are tasks (not appointments).

        Example:
            >>> tasks = await upsales.activities.get_tasks()
            >>> all(a.is_task for a in tasks)
            True
        """
        return await self.list_all(isAppointment=0)

    async def get_open(self) -> list[Activity]:
        """
        Get all open activities (closeDate is null).

        Returns:
            List of activities that are still open.

        Example:
            >>> open_activities = await upsales.activities.get_open()
            >>> all(not a.is_closed for a in open_activities)
            True
        """
        # Note: API might not support filtering by null directly
        # Fallback: fetch all and filter in-memory
        all_activities: list[Activity] = await self.list_all()
        return [a for a in all_activities if not a.is_closed]

    async def get_by_company(self, company_id: int) -> list[Activity]:
        """
        Get all activities for a specific company.

        Args:
            company_id: Company ID to filter by.

        Returns:
            List of activities linked to the company.

        Example:
            >>> activities = await upsales.activities.get_by_company(123)
            >>> len(activities)
            15
        """
        # Use nested field search
        return await self.search(**{"client.id": company_id})

    async def get_by_opportunity(self, opportunity_id: int) -> list[Activity]:
        """
        Get all activities for a specific opportunity.

        Args:
            opportunity_id: Opportunity ID to filter by.

        Returns:
            List of activities linked to the opportunity.

        Example:
            >>> activities = await upsales.activities.get_by_opportunity(456)
            >>> all(a.has_opportunity for a in activities)
            True
        """
        # Use nested field search
        return await self.search(**{"opportunity.id": opportunity_id})

    async def get_by_date_range(self, start_date: str, end_date: str) -> list[Activity]:
        """
        Get activities within a date range.

        Args:
            start_date: Start date (ISO 8601 format, e.g., "2025-11-01")
            end_date: End date (ISO 8601 format, e.g., "2025-11-30")

        Returns:
            List of activities in the date range.

        Example:
            >>> activities = await upsales.activities.get_by_date_range(
            ...     "2025-11-01",
            ...     "2025-11-30"
            ... )
            >>> len(activities)
            42
        """
        # Get all activities and filter in-memory for date range
        all_activities: list[Activity] = await self.list_all(sort="-date")
        return [a for a in all_activities if start_date <= a.date <= end_date]

    async def get_high_priority(self, min_priority: int = 3) -> list[Activity]:
        """
        Get high priority activities.

        Args:
            min_priority: Minimum priority level (default: 3)

        Returns:
            List of activities with priority >= min_priority.

        Example:
            >>> urgent = await upsales.activities.get_high_priority(min_priority=4)
            >>> all(a.priority >= 4 for a in urgent)
            True
        """
        return await self.search(
            priority=f">={min_priority}",
            fields=["id", "description", "date", "priority"],  # Optimize
            sort="-priority",  # Highest priority first
        )

    async def get_recent(self, days: int = 7) -> list[Activity]:
        """
        Get recent activities from the last N days.

        Args:
            days: Number of days to look back (default: 7)

        Returns:
            List of activities from the last N days.

        Example:
            >>> recent = await upsales.activities.get_recent(days=7)
            >>> len(recent)
            23
        """
        from datetime import datetime, timedelta

        cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        return await self.search(
            date=f">={cutoff_date}",
            sort="-date",  # Newest first
        )
