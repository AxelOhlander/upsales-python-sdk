"""
Activity quota resource manager for Upsales API.

Provides methods to interact with the /activityQuota endpoint.

Example:
    >>> async with Upsales(token="...") as upsales:
    ...     quota = await upsales.activity_quota.get(1)
    ...     quotas = await upsales.activity_quota.list(limit=10)
"""

from upsales.http import HTTPClient
from upsales.models.activity_quota import ActivityQuota, PartialActivityQuota
from upsales.resources.base import BaseResource


class ActivityQuotaResource(BaseResource[ActivityQuota, PartialActivityQuota]):
    """
    Resource manager for ActivityQuota endpoint.

    Tracks quarterly storage and monthly API usage metrics per user and activity type.

    Inherits standard CRUD operations from BaseResource:
    - create(**data) - Create new activity quota (admin/team leader only)
    - get(id) - Get single activity quota
    - list(limit, offset, **params) - List activity quotas with pagination
    - list_all(**params) - Auto-paginated list of all activity quotas
    - search(**filters) - Search with comparison operators
    - update(id, **data) - Update activity quota (admin/team leader only)
    - delete(id) - Delete activity quota
    - bulk_update(ids, data, max_concurrent) - Parallel updates
    - bulk_delete(ids, max_concurrent) - Parallel deletes

    Permissions:
        Create/Update: Administrator or team leader only

    Example:
        >>> resource = ActivityQuotaResource(http_client)
        >>> quota = await resource.get(1)
        >>> user_quotas = await resource.search(user__id=123)
        >>> await resource.update(1, performed=15, created=10)
    """

    def __init__(self, http: HTTPClient):
        """
        Initialize activity quota resource manager.

        Args:
            http: HTTP client for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/activityQuota",
            model_class=ActivityQuota,
            partial_class=PartialActivityQuota,
        )

    async def get_by_user(
        self, user_id: int, year: int | None = None, month: int | None = None
    ) -> list[ActivityQuota]:
        """
        Get all activity quotas for a specific user.

        Args:
            user_id: User ID to filter by.
            year: Optional year to filter by.
            month: Optional month to filter by (1-12).

        Returns:
            List of activity quotas for the user.

        Raises:
            ValidationError: If month not between 1-12.

        Example:
            >>> # Get all quotas for user 123
            >>> quotas = await resource.get_by_user(123)
            >>>
            >>> # Get quotas for specific month
            >>> quotas = await resource.get_by_user(123, year=2025, month=11)
        """
        filters = {"user__id": user_id}
        if year is not None:
            filters["year"] = year
        if month is not None:
            if not 1 <= month <= 12:
                raise ValueError(f"Month must be between 1 and 12, got {month}")
            filters["month"] = month
        return await self.search(**filters)

    async def get_by_activity_type(
        self, activity_type_id: int, year: int | None = None, month: int | None = None
    ) -> list[ActivityQuota]:
        """
        Get all activity quotas for a specific activity type.

        Args:
            activity_type_id: Activity type ID to filter by.
            year: Optional year to filter by.
            month: Optional month to filter by (1-12).

        Returns:
            List of activity quotas for the activity type.

        Raises:
            ValidationError: If month not between 1-12.

        Example:
            >>> # Get all quotas for activity type 5
            >>> quotas = await resource.get_by_activity_type(5)
            >>>
            >>> # Get quotas for specific year
            >>> quotas = await resource.get_by_activity_type(5, year=2025)
        """
        filters = {"activityType__id": activity_type_id}
        if year is not None:
            filters["year"] = year
        if month is not None:
            if not 1 <= month <= 12:
                raise ValueError(f"Month must be between 1 and 12, got {month}")
            filters["month"] = month
        return await self.search(**filters)
