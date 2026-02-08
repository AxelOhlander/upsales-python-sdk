"""Integration log resource for Upsales API.

Tracks standard integration execution logs and callback results.

Example:
    ```python
    async with Upsales(token="...") as upsales:
        logs = await upsales.integration_log.list()
        await upsales.integration_log.update(456, status=200, message={"result": "ok"})
    ```
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class IntegrationLogResource:
    """Resource manager for integration execution logs.

    Full CRUD at /integrationLog. GET single and PUT require admin.

    Example:
        ```python
        resource = IntegrationLogResource(http_client)
        logs = await resource.list()
        ```
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize integration log resource.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/integrationLog"

    async def list(self, **params: Any) -> dict[str, Any]:
        """List integration logs.

        Args:
            **params: Query parameters for filtering.

        Returns:
            API response with log entries (max 1000).

        Example:
            ```python
            logs = await upsales.integration_log.list()
            ```
        """
        return await self._http.get(self._endpoint, **params)

    async def get(self, log_id: int) -> dict[str, Any]:
        """Get a single integration log entry.

        Requires admin permissions.

        Args:
            log_id: The log entry ID.

        Returns:
            Log entry data.

        Example:
            ```python
            log = await upsales.integration_log.get(456)
            ```
        """
        return await self._http.get(f"{self._endpoint}/{log_id}")

    async def create(self, **data: Any) -> dict[str, Any]:
        """Create an integration log entry.

        Args:
            **data: Log data (standardIntegrationConfigId, integrationId,
                   userId, initObjectId, initType, etc.).

        Returns:
            Created log entry.

        Example:
            ```python
            log = await upsales.integration_log.create(
                integrationId=1, initType="Client", initObjectId=100
            )
            ```
        """
        return await self._http.post(self._endpoint, **data)

    async def update(self, log_id: int, **data: Any) -> dict[str, Any]:
        """Update an integration log entry.

        Requires admin. Auto-sets callbackDate to current UTC time.

        Args:
            log_id: The log entry ID.
            **data: Fields to update (status, message).

        Returns:
            Updated log entry.

        Example:
            ```python
            await upsales.integration_log.update(
                456, status=200, message={"result": "success"}
            )
            ```
        """
        return await self._http.put(f"{self._endpoint}/{log_id}", **data)

    async def delete(self, log_id: int) -> dict[str, Any]:
        """Delete an integration log entry.

        Args:
            log_id: The log entry ID.

        Returns:
            API response data.

        Example:
            ```python
            await upsales.integration_log.delete(456)
            ```
        """
        return await self._http.delete(f"{self._endpoint}/{log_id}")
