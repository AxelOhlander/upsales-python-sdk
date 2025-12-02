"""
Quotas resource manager for Upsales API.

Provides methods to interact with the /quota endpoint.

Example:
    >>> async with Upsales(token="...") as upsales:
    ...     quota = await upsales.quota.get(1)
    ...     quota_list = await upsales.quota.list(limit=10)
"""

from upsales.http import HTTPClient
from upsales.models.quota import PartialQuota, Quota
from upsales.resources.base import BaseResource


class QuotasResource(BaseResource[Quota, PartialQuota]):
    """
    Resource manager for Quota endpoint.

    Inherits standard CRUD operations from BaseResource:
    - get(id) - Get single quota
    - list(limit, offset, **params) - List quota with pagination
    - list_all(**params) - Auto-paginated list of all quota
    - create(**data) - Create new quota (requires admin/teamleader)
    - update(id, **data) - Update quota (requires admin/teamleader)
    - delete(id) - Delete quota
    - bulk_update(ids, data, max_concurrent) - Parallel updates
    - bulk_delete(ids, max_concurrent) - Parallel deletes

    Example:
        >>> resource = QuotasResource(http_client)
        >>> quota = await resource.get(1)
        >>> quotas_2025 = await resource.get_by_year(2025)
        >>> q4_quotas = await resource.get_by_quarter(2025, 4)
    """

    def __init__(self, http: HTTPClient):
        """
        Initialize quota resource manager.

        Args:
            http: HTTP client for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/quota",
            model_class=Quota,
            partial_class=PartialQuota,
        )

    async def get_by_user(self, user_id: int) -> list[Quota]:
        """
        Get all quotas for a specific user.

        Args:
            user_id: User ID to filter by.

        Returns:
            List of quotas for the specified user.

        Example:
            >>> quotas = await upsales.quota.get_by_user(123)
            >>> len(quotas)
            12  # All months for user
        """
        return await self.list_all(**{"user.id": user_id})

    async def get_by_year(self, year: int) -> list[Quota]:
        """
        Get all quotas for a specific year.

        Args:
            year: Year to filter by (e.g., 2025).

        Returns:
            List of quotas for the specified year.

        Example:
            >>> quotas = await upsales.quota.get_by_year(2025)
        """
        return await self.list_all(year=year)

    async def get_by_quarter(self, year: int, quarter: int) -> list[Quota]:
        """
        Get all quotas for a specific quarter.

        Args:
            year: Year (e.g., 2025).
            quarter: Quarter (1-4).

        Returns:
            List of quotas for the specified quarter.

        Raises:
            ValueError: If quarter is not 1-4.

        Example:
            >>> quotas = await upsales.quota.get_by_quarter(2025, 4)
            >>> len(quotas)
            3  # Oct, Nov, Dec
        """
        if quarter not in [1, 2, 3, 4]:
            raise ValueError(f"Quarter must be 1-4, got {quarter}")

        # Calculate months for quarter
        start_month = (quarter - 1) * 3 + 1
        end_month = quarter * 3

        # Get all for year and filter by quarter
        all_quotas = await self.get_by_year(year)
        return [q for q in all_quotas if start_month <= q.month <= end_month]

    async def get_by_user_and_period(
        self, user_id: int, year: int, month: int | None = None
    ) -> list[Quota]:
        """
        Get quotas for a specific user and period.

        Args:
            user_id: User ID to filter by.
            year: Year to filter by.
            month: Optional month to filter by (1-12).

        Returns:
            List of matching quotas.

        Raises:
            ValueError: If month is not 1-12.

        Example:
            >>> # All quotas for user in 2025
            >>> quotas = await upsales.quota.get_by_user_and_period(123, 2025)
            >>> # Specific month
            >>> nov_quota = await upsales.quota.get_by_user_and_period(123, 2025, 11)
        """
        if month is not None and (month < 1 or month > 12):
            raise ValueError(f"Month must be 1-12, got {month}")

        filters = {"user.id": user_id, "year": year}
        if month is not None:
            filters["month"] = month

        return await self.list_all(**filters)
