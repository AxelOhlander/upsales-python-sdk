"""
CustomFields resource manager for Upsales API.

Handles custom field definitions across multiple entities.
Each entity (account, order, product, contact, etc.) can have its own
custom fields.

Example:
    >>> async with Upsales(token="...") as upsales:
    ...     # Get all custom fields for accounts
    ...     fields = await upsales.custom_fields.list_for_entity("account")
    ...
    ...     # Get specific field
    ...     field = await upsales.custom_fields.get(11, entity="account")
    ...
    ...     # Create new field
    ...     new_field = await upsales.custom_fields.create_for_entity(
    ...         entity="account",
    ...         name="Test Field",
    ...         datatype="String",
    ...         alias="TEST"
    ...     )
"""

from typing import Any

from upsales.http import HTTPClient
from upsales.models.custom_field import CustomField


class CustomFieldsResource:
    """
    Resource manager for CustomField definitions.

    Unlike other resources, custom fields are entity-specific.
    Each entity (account, order, product) has its own custom fields.

    Entities that support custom fields:
    - account, order, orderrow, agreement, activity, todo, appointment,
      contact, product, project, projectPlan, ticket, user

    Note: This resource works differently from BaseResource because
    custom fields require an entity parameter for most operations.

    Example:
        >>> fields = CustomFieldsResource(http_client)
        >>> # List all custom fields for accounts
        >>> account_fields = await fields.list_for_entity("account")
        >>> # Get specific field
        >>> field = await fields.get(11, entity="account")
    """

    def __init__(self, http: HTTPClient):
        """
        Initialize custom fields resource manager.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http

    async def list_for_entity(self, entity: str) -> list[CustomField]:
        """
        List all custom fields for a specific entity.

        Args:
            entity: Entity type (e.g., "account", "order", "product").

        Returns:
            List of CustomField definitions for that entity.

        Example:
            >>> # Get all custom fields for accounts
            >>> fields = await upsales.custom_fields.list_for_entity("account")
            >>> for field in fields:
            ...     print(f"{field.name} ({field.datatype}): {field.alias}")
            >>>
            >>> # Get order custom fields
            >>> order_fields = await upsales.custom_fields.list_for_entity("order")
        """
        response = await self._http.get(f"/customFields/{entity}")
        return [
            CustomField(**item, _client=self._http._upsales_client) for item in response["data"]
        ]

    async def get(self, field_id: int, entity: str) -> CustomField:
        """
        Get a specific custom field by ID.

        Args:
            field_id: Custom field ID.
            entity: Entity the field belongs to.

        Returns:
            CustomField definition.

        Example:
            >>> field = await upsales.custom_fields.get(11, entity="account")
            >>> print(field.name, field.datatype)
            'VAT Number' 'String'
        """
        # Get all fields for entity and find the one with matching ID
        all_fields = await self.list_for_entity(entity)
        for field in all_fields:
            if field.id == field_id:
                return field

        from upsales.exceptions import NotFoundError

        raise NotFoundError(f"Custom field {field_id} not found in entity '{entity}'")

    async def create_for_entity(
        self,
        entity: str,
        **data: Any,
    ) -> CustomField:
        """
        Create a new custom field for an entity.

        Args:
            entity: Entity to create field for (e.g., "account", "order").
            **data: Custom field properties (name, datatype, alias required).

        Returns:
            Newly created CustomField.

        Example:
            >>> # Create String field
            >>> field = await upsales.custom_fields.create_for_entity(
            ...     entity="account",
            ...     name="Customer Code",
            ...     datatype="String",
            ...     alias="CUSTOMER_CODE",
            ...     maxLength=50,
            ...     visible=1,
            ...     editable=1
            ... )
            >>>
            >>> # Create Select field with options
            >>> priority = await upsales.custom_fields.create_for_entity(
            ...     entity="account",
            ...     name="Priority",
            ...     datatype="Select",
            ...     alias="PRIORITY",
            ...     default=["Low", "Medium", "High"]  # Options!
            ... )
            >>>
            >>> # Create Calculation field (order only)
            >>> calc = await upsales.custom_fields.create_for_entity(
            ...     entity="order",
            ...     name="Total with Tax",
            ...     datatype="Calculation",
            ...     alias="TOTAL_TAX",
            ...     formula="{Order.value} * 1.25"
            ... )

        Note:
            Required fields: name, datatype, alias
            For Select/MultiSelect: Include options in 'default' field
            For Calculation: Include 'formula' field
        """
        response = await self._http.post(f"/customFields/{entity}", **data)
        return CustomField(**response["data"], _client=self._http._upsales_client)

    async def update(
        self,
        field_id: int,
        entity: str,
        **data: Any,
    ) -> CustomField:
        """
        Update a custom field definition.

        Args:
            field_id: Custom field ID to update.
            entity: Entity the field belongs to.
            **data: Fields to update.

        Returns:
            Updated CustomField.

        Example:
            >>> # Update field name
            >>> updated = await upsales.custom_fields.update(
            ...     11,
            ...     entity="account",
            ...     name="Updated Name"
            ... )
            >>>
            >>> # Update Select field options
            >>> updated = await upsales.custom_fields.update(
            ...     12,
            ...     entity="account",
            ...     default=["New Option 1", "New Option 2"]  # New options
            ... )
        """
        response = await self._http.put(f"/customFields/{entity}/{field_id}", **data)
        return CustomField(**response["data"], _client=self._http._upsales_client)

    async def delete(self, field_id: int, entity: str) -> dict[str, Any]:
        """
        Delete a custom field definition.

        Warning: This will delete the field and all its data!

        Args:
            field_id: Custom field ID to delete.
            entity: Entity the field belongs to.

        Returns:
            Response from API.

        Example:
            >>> await upsales.custom_fields.delete(11, entity="account")
        """
        return await self._http.delete(f"/customFields/{entity}/{field_id}")

    async def get_by_alias(self, alias: str, entity: str) -> CustomField | None:
        """
        Get custom field by alias.

        Args:
            alias: Field alias (e.g., "VAT_NO").
            entity: Entity to search in.

        Returns:
            CustomField if found, None otherwise.

        Example:
            >>> field = await upsales.custom_fields.get_by_alias(
            ...     "VAT_NO",
            ...     entity="account"
            ... )
            >>> if field:
            ...     print(field.name, field.id)
        """
        fields = await self.list_for_entity(entity)
        for field in fields:
            if field.alias == alias:
                return field
        return None

    async def list_by_type(
        self,
        entity: str,
        datatype: str,
    ) -> list[CustomField]:
        """
        List all custom fields of a specific type for an entity.

        Args:
            entity: Entity to search.
            datatype: Field type (e.g., "String", "Select", "Boolean").

        Returns:
            List of CustomFields matching the type.

        Example:
            >>> # Get all Select fields for accounts
            >>> select_fields = await upsales.custom_fields.list_by_type(
            ...     entity="account",
            ...     datatype="Select"
            ... )
            >>> for field in select_fields:
            ...     print(f"{field.name}: {field.default}")  # Show options
        """
        all_fields = await self.list_for_entity(entity)
        return [f for f in all_fields if f.datatype == datatype]
