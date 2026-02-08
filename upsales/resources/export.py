"""Export resource for Upsales API.

Triggers async export of entity data.

Example:
    ```python
    async with Upsales(token="...") as upsales:
        await upsales.export.trigger(
            entity="Client",
            columns=[
                {"key": "Client_name", "title": "Company Name"},
                {"key": "Client_phone", "title": "Phone"},
            ],
            filters={"q": [{"a": "active", "c": "eq", "v": 1}]},
            name="active-companies",
        )
    ```
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class ExportResource:
    """Resource manager for data exports.

    Function endpoint at /function/export. Requires export permission.
    Exports run asynchronously and are delivered as file downloads or email.

    Example:
        ```python
        resource = ExportResource(http_client)
        await resource.trigger(entity="Client", columns=[...], filters={}, name="export")
        ```
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize export resource.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/function/export"

    async def trigger(
        self,
        entity: str,
        columns: list[dict[str, str]],
        filters: dict[str, Any],
        name: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Trigger an async data export.

        Args:
            entity: Entity type to export (Client, Contact, Order, Activity, etc.).
            columns: Column definitions, each with 'key' and 'title'.
            filters: Standard Upsales filter object.
            name: Export file name.
            **kwargs: Additional options (exportOrderRows, customFieldIds, etc.).

        Returns:
            API response (typically "OK" — export runs in background).

        Example:
            ```python
            await upsales.export.trigger(
                entity="Contact",
                columns=[{"key": "Contact_name", "title": "Name"}],
                filters={},
                name="all-contacts",
            )
            ```
        """
        return await self._http.post(
            self._endpoint,
            entity=entity,
            columns=columns,
            filters=filters,
            name=name,
            **kwargs,
        )
