"""Standard field resource for Upsales API.

Manages standard field definitions — field visibility, tooltips,
and required status per entity type.

Example:
    ```python
    async with Upsales(token="...") as upsales:
        fields = await upsales.standard_fields.list()
        contact_fields = await upsales.standard_fields.get_for_entity("Contact")
    ```
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class StandardFieldsResource:
    """Resource manager for standard field configuration.

    Endpoint at /standardField. Requires admin permissions.

    Example:
        ```python
        resource = StandardFieldsResource(http_client)
        fields = await resource.list()
        ```
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize standard fields resource.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/standardField"

    async def list(self) -> dict[str, Any]:
        """List all standard field configs for all entity types.

        Returns:
            API response with field configurations keyed by entity type.

        Example:
            ```python
            fields = await upsales.standard_fields.list()
            ```
        """
        return await self._http.get(self._endpoint)

    async def get_for_entity(self, entity: str) -> dict[str, Any]:
        """Get standard field configs for a specific entity type.

        Args:
            entity: Entity type (Client, Contact, Activity, Appointment,
                   Order, Product, Todo).

        Returns:
            Field configurations for the entity.

        Example:
            ```python
            contact_fields = await upsales.standard_fields.get_for_entity("Contact")
            ```
        """
        return await self._http.get(f"{self._endpoint}/{entity}")

    async def update(self, field_id: int, **data: Any) -> dict[str, Any]:
        """Update a standard field configuration.

        Args:
            field_id: The field ID.
            **data: Fields to update (tooltip, active, required).

        Returns:
            Updated field configuration.

        Example:
            ```python
            await upsales.standard_fields.update(
                42, tooltip="Enter company phone", active=True, required=True
            )
            ```
        """
        return await self._http.put(f"{self._endpoint}/{field_id}", **data)
