"""
Bulk prospecting save resource manager for Upsales API.

Provides methods to bulk save prospecting companies to Upsales.
This is a specialized endpoint that only supports POST operations.

Example:
    Bulk save prospecting companies:

    >>> async with Upsales(token="...") as upsales:
    ...     result = await upsales.bulk.save(
    ...         filters=[{"field": "country", "value": "US"}],
    ...         userId=123,
    ...         categoryId=456
    ...     )
    ...     print(f"Saved {result.count} companies")
"""

from typing import Any

from upsales.http import HTTPClient
from upsales.models.bulk import BulkSaveResponse


class BulkResource:
    """
    Resource manager for bulk prospecting save endpoint.

    This is a specialized resource that only supports bulk save operations.
    Unlike standard resources, it does not inherit from BaseResource as it
    doesn't support standard CRUD operations (GET, UPDATE, DELETE).

    The bulk endpoint allows saving multiple prospecting companies that match
    specified filter criteria in a single operation.

    Attributes:
        http: HTTP client for API requests.
        endpoint: API endpoint path (/api/v2/prospectingbulk).

    Example:
        Basic bulk save:

        >>> resource = BulkResource(http_client)
        >>> result = await resource.save(
        ...     filters=[
        ...         {"field": "country", "value": "US"},
        ...         {"field": "employees", "operator": "gte", "value": 50}
        ...     ],
        ...     userId=123,
        ...     categoryId=456,
        ...     stageId=789
        ... )
        >>> print(f"Successfully saved {result.count} companies")

        Using BulkSaveRequest model:

        >>> request = BulkSaveRequest(
        ...     filters=[{"field": "industry", "value": "Technology"}],
        ...     userId=123
        ... )
        >>> result = await resource.save(**request.model_dump())
    """

    def __init__(self, http: HTTPClient):
        """
        Initialize bulk resource manager.

        Args:
            http: HTTP client for API requests.

        Example:
            >>> from upsales.http import HTTPClient
            >>> http = HTTPClient(token="...")
            >>> bulk = BulkResource(http)
        """
        self.http = http
        self.endpoint = "/prospectingbulk"

    async def save(  # noqa: N803
        self,
        *,
        filters: list[dict[str, Any]],
        operationalAccountId: int | None = None,  # noqa: N803 - matches API field name
        userId: int | None = None,  # noqa: N803 - matches API field name
        categoryId: int | None = None,  # noqa: N803 - matches API field name
        stageId: int | None = None,  # noqa: N803 - matches API field name
    ) -> BulkSaveResponse:
        """
        Bulk save prospecting companies to Upsales.

        Saves multiple prospecting companies that match the specified filter criteria.
        You can optionally specify default values (user, category, stage) to assign
        to all saved companies.

        Args:
            filters: Array of filter conditions to select prospecting companies.
                Each filter should be a dict with keys like 'field', 'value', 'operator'.
                Example: [{"field": "country", "value": "US"}]
            operationalAccountId: Optional operational account ID to assign to saved companies.
            userId: Optional user ID to assign as owner of saved companies.
            categoryId: Optional category ID to assign to saved companies.
            stageId: Optional stage ID to assign to saved companies.

        Returns:
            BulkSaveResponse with operation results including success status and count.

        Raises:
            ValidationError: If filters are empty or invalid.
            ServerError: If the API request fails.

        Example:
            Save US companies with 50+ employees:

            >>> result = await resource.save(
            ...     filters=[
            ...         {"field": "country", "value": "US"},
            ...         {"field": "employees", "operator": "gte", "value": 50}
            ...     ],
            ...     userId=123,
            ...     categoryId=456
            ... )
            >>> if result.success:
            ...     print(f"Saved {result.count} companies")
            ... else:
            ...     print(f"Error: {result.message}")

            Save with BulkSaveRequest model:

            >>> request = BulkSaveRequest(
            ...     filters=[{"field": "industry", "value": "Technology"}],
            ...     userId=123
            ... )
            >>> result = await resource.save(**request.model_dump())
        """
        data: dict[str, Any] = {"filters": filters}
        if operationalAccountId is not None:
            data["operationalAccountId"] = operationalAccountId
        if userId is not None:
            data["userId"] = userId
        if categoryId is not None:
            data["categoryId"] = categoryId
        if stageId is not None:
            data["stageId"] = stageId

        response = await self.http.post(self.endpoint, **data)
        # HTTPClient.post() returns the full response, extract data
        if isinstance(response, dict) and "data" in response:
            return BulkSaveResponse.model_validate(response["data"])
        return BulkSaveResponse.model_validate(response)
