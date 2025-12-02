"""
Bulk prospecting save models for Upsales API.

This module provides models for bulk saving prospecting companies to Upsales.
The bulk endpoint allows saving multiple filtered prospecting companies in one operation.

Example:
    Basic bulk save operation:

    >>> bulk_request = BulkSaveRequest(
    ...     filters=[{"field": "country", "value": "US"}],
    ...     userId=123,
    ...     categoryId=456
    ... )
    >>> result = await upsales.bulk.save(bulk_request.model_dump())
"""

from __future__ import annotations

from typing import Any, TypedDict, Unpack

from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field

from upsales.models.base import BaseModel, PartialModel


class BulkSaveFields(TypedDict, total=False):
    """
    Available fields for bulk save operation.

    This TypedDict provides type hints for the bulk save endpoint parameters.
    All fields are optional.
    """

    filters: list[dict[str, Any]]
    operationalAccountId: int
    userId: int
    categoryId: int
    stageId: int


class BulkSaveRequest(BaseModel):
    """
    Request model for bulk saving prospecting companies.

    This model represents the data structure required for the bulk save endpoint.
    It allows filtering prospecting companies and specifying default values for
    saved companies.

    Attributes:
        filters: Array of filter conditions to select prospecting companies.
            Each filter should specify criteria like country, industry, etc.
        operationalAccountId: Optional operational account ID to assign to saved companies.
        userId: Optional user ID to assign as owner of saved companies.
        categoryId: Optional category ID to assign to saved companies.
        stageId: Optional stage ID to assign to saved companies.

    Example:
        Create a bulk save request:

        >>> request = BulkSaveRequest(
        ...     filters=[
        ...         {"field": "country", "value": "US"},
        ...         {"field": "employees", "operator": "gte", "value": 50}
        ...     ],
        ...     userId=123,
        ...     categoryId=456
        ... )
        >>> await upsales.bulk.save(request.model_dump())
    """

    filters: list[dict[str, Any]] = Field(
        description="Filter conditions to select prospecting companies"
    )
    operationalAccountId: int | None = Field(
        None, description="Operational account ID for saved companies"
    )
    userId: int | None = Field(None, description="User ID to assign as owner")
    categoryId: int | None = Field(None, description="Category ID to assign")
    stageId: int | None = Field(None, description="Stage ID to assign")


class BulkSaveResponse(PydanticBaseModel):
    """
    Response model for bulk save operation.

    This model represents the response from the bulk save endpoint.
    Since the bulk endpoint doesn't return standard fields like id,
    this uses Pydantic's BaseModel directly rather than the SDK's BaseModel.

    Attributes:
        success: Whether the bulk save operation succeeded.
        count: Number of companies saved.
        message: Optional message about the operation.

    Example:
        Process bulk save response:

        >>> response = await upsales.bulk.save(request_data)
        >>> print(f"Saved {response.count} companies")
    """

    success: bool = Field(description="Operation success status")
    count: int | None = Field(None, description="Number of companies saved")
    message: str | None = Field(None, description="Operation message")


class PartialBulkSaveRequest(PartialModel):
    """
    Minimal bulk save request model for nested responses.

    This partial model is used when bulk save requests appear in nested API responses.
    Use BulkSaveRequest for creating new bulk save operations.

    Attributes:
        filters: Array of filter conditions.

    Example:
        Fetch full request details:

        >>> partial_request = PartialBulkSaveRequest(filters=[...])
        >>> # Note: This endpoint doesn't support GET operations
    """

    filters: list[dict[str, Any]] = Field(
        description="Filter conditions to select prospecting companies"
    )

    async def fetch_full(self) -> BulkSaveRequest:
        """
        Fetch full bulk save request details.

        Note:
            The bulk endpoint does not support GET operations.
            This method is provided for interface consistency but will raise an error.

        Returns:
            Full BulkSaveRequest instance.

        Raises:
            RuntimeError: Always raised as bulk endpoint doesn't support GET.
        """
        raise RuntimeError(
            "Bulk endpoint does not support GET operations. "
            "Use BulkSaveRequest directly for POST requests."
        )

    async def edit(self, **kwargs: Unpack[BulkSaveFields]) -> BulkSaveRequest:
        """
        Edit bulk save request.

        Note:
            The bulk endpoint does not support UPDATE operations.
            This method is provided for interface consistency but will raise an error.

        Args:
            **kwargs: Fields to update.

        Returns:
            Updated BulkSaveRequest instance.

        Raises:
            RuntimeError: Always raised as bulk endpoint doesn't support UPDATE.
        """
        raise RuntimeError(
            "Bulk endpoint does not support UPDATE operations. "
            "Create a new bulk save request with BulkSaveRequest."
        )
