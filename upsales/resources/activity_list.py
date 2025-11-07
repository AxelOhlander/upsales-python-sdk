"""
Activity list resource manager for Upsales API.

Manages /api/v2/search/activitylist endpoint operations.

This is a read-only search endpoint that aggregates different activity types
(tasks, appointments, emails) into a unified list. This endpoint does not
support create/update/delete operations.

This resource manager provides:
- search(): Search activity list with filters
- list(): Paginated list of activities
- list_all(): Auto-paginated list of all activities
"""

from __future__ import annotations

import builtins
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from upsales.http import HTTPClient

from upsales.models.activity_list_item import ActivityListItem


class ActivityListResource:
    """
    Resource manager for /api/v2/search/activitylist endpoint.

    This is a read-only search endpoint that returns a heterogeneous list
    of activities including tasks, appointments, and emails.

    Args:
        http: HTTP client instance for making API requests.

    Attributes:
        _http: HTTP client for API requests.
        _endpoint: API endpoint path (/search/activitylist).

    Example:
        >>> async with Upsales.from_env() as upsales:
        ...     # Get all activities
        ...     items = await upsales.activity_list.list(limit=50)
        ...     print(f"Found {len(items)} activities")
        ...
        ...     # Get all activities (auto-paginated)
        ...     all_items = await upsales.activity_list.list_all()
        ...     print(f"Total: {len(all_items)} activities")
        ...
        ...     # Filter by type
        ...     for item in items:
        ...         if item.is_email:
        ...             print(f"Email: {item.subject}")
        ...         elif item.is_appointment:
        ...             print(f"Appointment: {item.description}")
    """

    def __init__(self, http: HTTPClient) -> None:
        """
        Initialize activity list resource manager.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/search/activitylist"

    async def list(
        self, limit: int = 100, offset: int = 0, **params: Any
    ) -> builtins.list[ActivityListItem]:
        """
        Get paginated list of activities from activity list.

        Args:
            limit: Maximum number of items to return (default: 100).
            offset: Number of items to skip (default: 0).
            **params: Additional query parameters.

        Returns:
            List of ActivityListItem objects.

        Raises:
            UpsalesError: If API request fails.

        Example:
            >>> # Get first 50 activities
            >>> items = await upsales.activity_list.list(limit=50)
            >>> len(items)
            50
            >>>
            >>> # Get next 50 activities
            >>> items = await upsales.activity_list.list(limit=50, offset=50)
        """
        params["limit"] = limit
        params["offset"] = offset
        response = await self._http.get(self._endpoint, params=params)

        return [
            ActivityListItem(**item, _client=self._http._upsales_client)
            for item in response["data"]
        ]

    async def list_all(self, **params: Any) -> builtins.list[ActivityListItem]:
        """
        Get all activities from activity list (auto-paginated).

        Automatically handles pagination to fetch all items. Use with caution
        on large datasets.

        Args:
            **params: Additional query parameters.

        Returns:
            List of all ActivityListItem objects.

        Raises:
            UpsalesError: If API request fails.

        Example:
            >>> # Get all activities
            >>> all_items = await upsales.activity_list.list_all()
            >>> print(f"Total activities: {len(all_items)}")
            Total activities: 396
        """
        items: list[ActivityListItem] = []
        offset = 0
        limit = 1000

        while True:
            batch = await self.list(limit=limit, offset=offset, **params)
            if not batch:
                break
            items.extend(batch)
            if len(batch) < limit:
                break
            offset += limit

        return items

    async def search(self, **filters: Any) -> builtins.list[ActivityListItem]:
        """
        Search activity list with filters.

        Alias for list() method for semantic clarity.

        Args:
            **filters: Query parameters for filtering (limit, offset, etc.).

        Returns:
            List of ActivityListItem objects matching filters.

        Raises:
            UpsalesError: If API request fails.

        Example:
            >>> # Search with limit
            >>> items = await upsales.activity_list.search(limit=10)
            >>> len(items)
            10
        """
        return await self.list(**filters)

    async def get_emails(self, limit: int = 100) -> builtins.list[ActivityListItem]:
        """
        Get email activities from activity list.

        Returns only items that are emails (have subject field).

        Args:
            limit: Maximum number of items to fetch before filtering.

        Returns:
            List of ActivityListItem objects that are emails.

        Raises:
            UpsalesError: If API request fails.

        Example:
            >>> emails = await upsales.activity_list.get_emails()
            >>> for email in emails:
            ...     print(f"From: {email.from_}, To: {email.to}, Subject: {email.subject}")
        """
        items = await self.list(limit=limit)
        return [item for item in items if item.is_email]

    async def get_appointments(self, limit: int = 100) -> builtins.list[ActivityListItem]:
        """
        Get appointment activities from activity list.

        Returns only items that are appointments.

        Args:
            limit: Maximum number of items to fetch before filtering.

        Returns:
            List of ActivityListItem objects that are appointments.

        Raises:
            UpsalesError: If API request fails.

        Example:
            >>> appointments = await upsales.activity_list.get_appointments()
            >>> for apt in appointments:
            ...     print(f"Date: {apt.date}, Description: {apt.description}")
        """
        items = await self.list(limit=limit)
        return [item for item in items if item.is_appointment]

    async def get_tasks(self, limit: int = 100) -> builtins.list[ActivityListItem]:
        """
        Get task activities from activity list.

        Returns only items that are tasks (not appointments, not emails).

        Args:
            limit: Maximum number of items to fetch before filtering.

        Returns:
            List of ActivityListItem objects that are tasks.

        Raises:
            UpsalesError: If API request fails.

        Example:
            >>> tasks = await upsales.activity_list.get_tasks()
            >>> for task in tasks:
            ...     print(f"Date: {task.date}, Description: {task.description}")
        """
        items = await self.list(limit=limit)
        return [item for item in items if item.is_task]


__all__ = ["ActivityListResource"]
