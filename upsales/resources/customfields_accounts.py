"""Custom fields for accounts resource for Upsales API.

Manages custom field definitions on accounts/companies. This manages the
schema/configuration of custom fields, not the values on individual accounts.

Example:
    ```python
    async with Upsales(token="...") as upsales:
        # List all account custom fields
        fields = await upsales.customfields_accounts.list()

        # Create a custom field
        field = await upsales.customfields_accounts.create(
            name="Industry Segment",
            datatype="cbo",
            dropdownDefault=["Tech", "Finance", "Healthcare"],
        )
    ```
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class CustomfieldsAccountsResource:
    """Resource manager for account custom field definitions.

    Full CRUD at /customfields/account. POST/PUT/DELETE require admin.

    Example:
        ```python
        resource = CustomfieldsAccountsResource(http_client)
        fields = await resource.list()
        ```
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize customfields accounts resource.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/customfields/account"

    async def list(self) -> dict[str, Any]:
        """List all account custom field definitions.

        Returns:
            API response with custom field definitions.

        Example:
            ```python
            fields = await upsales.customfields_accounts.list()
            ```
        """
        return await self._http.get(self._endpoint)

    async def get(self, field_id: int) -> dict[str, Any]:
        """Get a single custom field definition.

        Args:
            field_id: The custom field ID.

        Returns:
            Custom field definition data.

        Example:
            ```python
            field = await upsales.customfields_accounts.get(11)
            ```
        """
        return await self._http.get(f"{self._endpoint}/{field_id}")

    async def create(self, **data: Any) -> dict[str, Any]:
        """Create a new custom field definition.

        Requires admin permissions.

        Args:
            **data: Field data. Required: name. Optional: datatype, dropdownDefault,
                   default, sortId, visible, editable, locked, obligatoryField,
                   searchable, maxLength, alias, viewonly, formGroup.

        Returns:
            Created custom field definition.

        Example:
            ```python
            field = await upsales.customfields_accounts.create(
                name="Industry",
                datatype="cbo",
                dropdownDefault=["Tech", "Finance"],
            )
            ```
        """
        return await self._http.post(self._endpoint, **data)

    async def update(self, field_id: int, **data: Any) -> dict[str, Any]:
        """Update a custom field definition.

        Requires admin permissions.

        Args:
            field_id: The custom field ID.
            **data: Fields to update.

        Returns:
            Updated custom field definition.

        Example:
            ```python
            await upsales.customfields_accounts.update(11, visible=False)
            ```
        """
        return await self._http.put(f"{self._endpoint}/{field_id}", **data)

    async def delete(self, field_id: int) -> dict[str, Any]:
        """Delete a custom field definition.

        Requires admin permissions.

        Args:
            field_id: The custom field ID.

        Returns:
            API response data.

        Example:
            ```python
            await upsales.customfields_accounts.delete(11)
            ```
        """
        return await self._http.delete(f"{self._endpoint}/{field_id}")
