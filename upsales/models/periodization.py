"""
Periodization models for Upsales API.

Revenue recognition over time for orders.
"""

from typing import TypedDict, Unpack

from pydantic import Field

from upsales.models.base import BaseModel, PartialModel


class PeriodizationUpdateFields(TypedDict, total=False):
    """
    Available fields for updating a Periodization.

    All fields are optional for updates.
    """

    orderId: int
    startDate: str
    endDate: str


class PeriodizationCreateFields(TypedDict, total=False):
    """
    Available fields for creating a Periodization.

    Required fields: orderId, startDate, endDate.
    """

    orderId: int
    startDate: str
    endDate: str


class Periodization(BaseModel):
    """
    Periodization model from /api/v2/periodization.

    Represents revenue recognition over time for an order.

    Attributes:
        id: Unique periodization identifier (read-only).
        orderId: Associated order ID.
        startDate: Start date for revenue recognition (YYYY-MM-DD format).
        endDate: End date for revenue recognition (YYYY-MM-DD format).
    """

    # Read-only fields
    id: int = Field(frozen=True, strict=True, description="Unique periodization identifier")

    # Updatable fields
    orderId: int = Field(description="Associated order ID")
    startDate: str = Field(description="Start date (YYYY-MM-DD)")
    endDate: str = Field(description="End date (YYYY-MM-DD)")

    @property
    def is_valid_date_range(self) -> bool:
        """
        Check if the date range is valid (start before end).

        Returns:
            True if startDate is before endDate.

        Example:
            >>> p = Periodization(id=1, orderId=123, startDate="2025-01-01", endDate="2025-12-31")
            >>> p.is_valid_date_range
            True
        """
        return self.startDate < self.endDate

    async def edit(self, **kwargs: Unpack[PeriodizationUpdateFields]) -> "Periodization":
        """
        Edit this periodization with full IDE autocomplete.

        Args:
            **kwargs: Fields to update (orderId, startDate, endDate).

        Returns:
            Updated periodization instance with new values.

        Raises:
            RuntimeError: If no client is available.

        Example:
            >>> periodization = await upsales.periodization.get(1)
            >>> updated = await periodization.edit(
            ...     startDate="2025-02-01",
            ...     endDate="2025-12-31"
            ... )
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.periodization.update(self.id, **self.to_api_dict(**kwargs))


class PartialPeriodization(PartialModel):
    """
    Partial Periodization for nested responses.

    Minimal representation when periodizations appear in nested contexts.

    Attributes:
        id: Unique periodization identifier.
        orderId: Associated order ID.
    """

    id: int = Field(description="Unique periodization identifier")
    orderId: int = Field(description="Associated order ID")

    async def fetch_full(self) -> Periodization:
        """
        Fetch complete periodization data from API.

        Returns:
            Full Periodization instance with all fields populated.

        Raises:
            RuntimeError: If no client is available.

        Example:
            >>> partial = PartialPeriodization(id=1, orderId=123)
            >>> full = await partial.fetch_full()
            >>> print(full.startDate)
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.periodization.get(self.id)

    async def edit(self, **kwargs: Unpack[PeriodizationUpdateFields]) -> Periodization:
        """
        Edit this periodization.

        Args:
            **kwargs: Fields to update.

        Returns:
            Updated full Periodization instance.

        Raises:
            RuntimeError: If no client is available.

        Example:
            >>> partial = PartialPeriodization(id=1, orderId=123)
            >>> updated = await partial.edit(startDate="2025-03-01")
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.periodization.update(self.id, **kwargs)
