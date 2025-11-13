"""
ProcessedBy models for company processing tracking.

This model represents audit/tracking data for when a company was processed.
It only appears nested in other API responses (e.g., company.processedBy)
and has no direct endpoint.

Based on analysis of company.processedBy field structure (34% populated).

Example API structure:
    {
        "id": 123,
        "entityType": "company",
        "date": "2025-10-15",
        "time": "14:30:00",
        "user": {
            "id": 1,
            "name": "John Doe",
            "email": "john@example.com"
        }
    }

Example:
    >>> company = await upsales.companies.get(1)
    >>> if company.processedBy:
    ...     print(f"Processed by {company.processedBy.user.name}")
    ...     print(f"On {company.processedBy.date} at {company.processedBy.time}")
    >>> partial = company.processedBy  # PartialProcessedBy
    >>> full = await partial.fetch_full()  # Requires implementing if endpoint exists
"""

from typing import Any

from pydantic import Field

from upsales.models.base import BaseModel, PartialModel
from upsales.models.user import PartialUser
from upsales.validators import NonEmptyStr


class ProcessedBy(BaseModel):
    """
    ProcessedBy model for company processing tracking.

    Represents audit/tracking data showing when and by whom a company
    was processed. This is nested data only - no direct endpoint.

    All fields are guaranteed present in full responses.

    Attributes:
        id: Unique identifier for the processing record.
        entityType: Type of entity processed (e.g., "company").
        date: Date when processing occurred (ISO format: YYYY-MM-DD).
        time: Time when processing occurred (HH:MM:SS format).
        user: User who performed the processing.

    Example:
        >>> company = await upsales.companies.get(1)
        >>> if company.processedBy:
        ...     processed = company.processedBy
        ...     print(f"ID: {processed.id}")
        ...     print(f"Type: {processed.entityType}")
        ...     print(f"When: {processed.date} {processed.time}")
        ...     print(f"By: {processed.user.name}")
    """

    # Read-only fields (frozen=True, strict=True)
    id: int = Field(frozen=True, strict=True, description="Unique processing record ID")

    # Required fields
    entityType: NonEmptyStr = Field(description="Entity type that was processed (e.g., 'company')")
    date: NonEmptyStr = Field(description="Processing date in ISO format (YYYY-MM-DD)")

    # Optional fields (API doesn't always return these)
    time: str | None = Field(
        default=None, description="Processing time in HH:MM:SS format (optional)"
    )

    # Nested user reference (accepts both PartialUser object and dict)
    user: PartialUser | dict[str, Any] = Field(
        description="User who performed the processing (minimal data)"
    )

    async def edit(self, **kwargs: Any) -> "ProcessedBy":
        """
        Edit this processing record.

        Note:
            This is audit/tracking data and likely read-only in the API.
            This method is provided for consistency with BaseModel interface
            but may not be supported by the Upsales API.

        Args:
            **kwargs: Fields to update.

        Returns:
            Updated ProcessedBy object.

        Raises:
            RuntimeError: If no client reference available.
            NotImplementedError: If the API does not support editing processing records.

        Example:
            >>> # This may not be supported by the API
            >>> # updated = await processed_by.edit(date="2025-10-16")
        """
        if not self._client:
            raise RuntimeError("No client available")
        raise NotImplementedError(
            "ProcessedBy records are audit data and cannot be edited directly. "
            "This data is managed by the Upsales system."
        )

    def __repr__(self: "ProcessedBy") -> str:
        """
        Return string representation of the processing record.

        Returns:
            String like "<ProcessedBy id=123 entityType='company'>".

        Example:
            >>> print(processed_by)
            <ProcessedBy id=123 entityType='company'>
        """
        return f"<ProcessedBy id={self.id} entityType='{self.entityType}'>"


class PartialProcessedBy(PartialModel):
    """
    Partial ProcessedBy for nested responses.

    Contains minimal fields for when ProcessedBy appears nested in other
    API responses (e.g., company.processedBy).

    Use fetch_full() to get complete ProcessedBy object with all fields.

    Attributes:
        id: Unique identifier for the processing record.
        entityType: Type of entity processed.
        date: Processing date.

    Example:
        >>> company = await upsales.companies.get(1)
        >>> partial = company.processedBy  # PartialProcessedBy (if present)
        >>> # fetch_full() not implemented - no direct endpoint exists
        >>> print(f"{partial.entityType} processed on {partial.date}")
    """

    id: int = Field(frozen=True, strict=True, description="Unique processing record ID")
    entityType: NonEmptyStr = Field(description="Entity type processed")
    date: NonEmptyStr = Field(description="Processing date (YYYY-MM-DD)")

    async def fetch_full(self) -> ProcessedBy:
        """
        Fetch complete processing record data.

        Note:
            ProcessedBy data appears nested only and has no direct endpoint.
            This method is provided for consistency with PartialModel interface
            but cannot be implemented without a dedicated API endpoint.

        Returns:
            Full ProcessedBy object with all fields populated.

        Raises:
            RuntimeError: If no client reference available.
            NotImplementedError: Always - no direct endpoint exists.

        Example:
            >>> partial = company.processedBy
            >>> # This will raise NotImplementedError
            >>> # full = await partial.fetch_full()
        """
        if not self._client:
            raise RuntimeError("No client available")
        raise NotImplementedError(
            "ProcessedBy has no direct API endpoint. "
            "This data only appears nested in other responses (e.g., company.processedBy)."
        )

    async def edit(self, **kwargs: Any) -> ProcessedBy:
        """
        Edit this processing record.

        Note:
            This is audit/tracking data and likely read-only in the API.
            No direct endpoint exists for ProcessedBy records.

        Args:
            **kwargs: Fields to update.

        Returns:
            Updated full ProcessedBy object.

        Raises:
            RuntimeError: If no client reference available.
            NotImplementedError: Always - editing not supported.

        Example:
            >>> partial = company.processedBy
            >>> # This will raise NotImplementedError
            >>> # updated = await partial.edit(date="2025-10-16")
        """
        if not self._client:
            raise RuntimeError("No client available")
        raise NotImplementedError(
            "ProcessedBy records are audit data and cannot be edited. "
            "No direct API endpoint exists for this resource."
        )

    def __repr__(self: "PartialProcessedBy") -> str:
        """
        Return string representation of the partial processing record.

        Returns:
            String like "<PartialProcessedBy id=123 entityType='company'>".

        Example:
            >>> print(partial)
            <PartialProcessedBy id=123 entityType='company'>
        """
        return f"<PartialProcessedBy id={self.id} entityType='{self.entityType}'>"
