"""Data source models for standard integration operations.

This module provides models for the dataSource endpoint, which handles
integration data source operations like typeahead, buy, settings, and monitor
actions.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel as PydanticBase
from pydantic import Field

from upsales.models.base import PartialModel


class DataSourceRequest(PydanticBase):
    """Request model for data source operations.

    This model represents the request structure for data source operations
    like typeahead, buy, settings, and monitor.

    Attributes:
        type: Type of data source operation
        integration_id: ID of the integration
        path: Optional path parameter for GET requests
        additional_data: Any additional data required for the operation

    Example:
        ```python
        request = DataSourceRequest(
            type="typeahead",
            integration_id=123,
            path="search",
        )
        ```
    """

    type: str = Field(description="Type of data source operation")
    integration_id: int = Field(alias="integrationId", description="ID of the integration")
    path: str | None = Field(None, description="Optional path parameter")
    additional_data: dict[str, Any] | None = Field(
        None, description="Additional operation-specific data"
    )


class DataSourceResponse(PydanticBase):
    """Response model for data source operations.

    This model represents the response structure from data source operations.

    Attributes:
        success: Whether the operation was successful
        data: Response data from the operation
        error: Error message if operation failed

    Example:
        ```python
        response = DataSourceResponse(
            success=True,
            data={"results": [...]},
        )
        ```
    """

    success: bool = Field(default=True, description="Operation success status")
    data: dict[str, Any] | list[dict[str, Any]] | None = Field(None, description="Response data")
    error: str | None = Field(None, description="Error message if failed")


class PartialDataSourceResponse(PartialModel):
    """Minimal data source response for nested references.

    This partial model is used when data source responses appear as nested
    objects in other API responses.

    Attributes:
        success: Whether the operation was successful
        data: Response data from the operation

    Example:
        ```python
        partial = PartialDataSourceResponse(
            success=True,
            data={"status": "ok"},
        )

        # Fetch full details if needed
        full = await partial.fetch_full()
        ```
    """

    success: bool = Field(default=True, description="Operation success status")
    data: dict[str, Any] | None = Field(None, description="Response data")

    async def fetch_full(self) -> DataSourceResponse:
        """Fetch full data source response details.

        Note:
            This operation may not be supported for all data source responses
            as they are typically operation-specific.

        Returns:
            Full DataSourceResponse model with all fields populated.

        Raises:
            RuntimeError: If no client is available.
            UpsalesError: If the API request fails.

        Example:
            ```python
            partial = PartialDataSourceResponse(success=True)
            full = await partial.fetch_full()
            print(full.data)
            ```
        """
        if not self._client:
            raise RuntimeError("No client available for API operations")

        # Note: Data source responses are operation-specific and may not
        # support fetching full details separately
        return DataSourceResponse(success=self.success, data=self.data, error=None)

    async def edit(self, **kwargs: Any) -> DataSourceResponse:
        """Edit data source response.

        Note:
            This operation is not typically supported for data source responses
            as they represent read-only operation results.

        Args:
            **kwargs: Fields to update

        Returns:
            Updated DataSourceResponse model.

        Raises:
            RuntimeError: If no client is available.
            NotImplementedError: Data source responses are typically read-only.

        Example:
            ```python
            # This operation may not be supported
            try:
                updated = await partial.edit(success=False)
            except NotImplementedError:
                print("Edit not supported for data source responses")
            ```
        """
        if not self._client:
            raise RuntimeError("No client available for API operations")

        raise NotImplementedError("Data source responses are read-only and cannot be edited")


__all__ = [
    "DataSourceRequest",
    "DataSourceResponse",
    "PartialDataSourceResponse",
]
