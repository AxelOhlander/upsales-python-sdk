"""
Trigger attributes resource manager for Upsales API.

Manages /api/v2/triggerAttributes endpoint operations.

IMPORTANT: TriggerAttributes endpoint is read-only and returns a dict (not a list).
This endpoint provides attribute definitions for automation triggers and rules,
organized by entity type.

This resource manager provides:
- get(): Get trigger attribute definitions (dict by entity type)

Standard operations like create(), update(), delete(), list() are not applicable.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from upsales.http import HTTPClient

from upsales.models.trigger_attributes import TriggerAttribute, TriggerAttributes


class TriggerAttributesResource:
    """
    Resource manager for /api/v2/triggerAttributes endpoint.

    Note: Unlike most resources, triggerAttributes returns a dict organized by
    entity type rather than a list of items. This endpoint is read-only and
    provides schema metadata for automation triggers.

    Args:
        http: HTTP client instance for making API requests.

    Attributes:
        _http: HTTP client for API requests.
        _endpoint: API endpoint path (/triggerAttributes).

    Example:
        >>> async with Upsales.from_env() as upsales:
        ...     # Get all trigger attributes
        ...     attrs = await upsales.trigger_attributes.get()
        ...     print(f"Entity types: {len(attrs.entity_types)}")
        ...     print(f"Total attributes: {attrs.total_attributes}")
        ...
        ...     # Get attributes for specific entity
        ...     client_attrs = attrs.get_entity_attributes('Client')
        ...     print(f"Client has {len(client_attrs)} attributes")
        ...
        ...     # Get only criteria attributes
        ...     criteria = attrs.get_criteria_attributes('Contact')
        ...     print(f"Contact has {len(criteria)} criteria attributes")
    """

    def __init__(self, http: HTTPClient) -> None:
        """
        Initialize trigger attributes resource manager.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/triggerAttributes"

    async def get(self) -> TriggerAttributes:
        """
        Get all trigger attribute definitions.

        Returns attribute definitions organized by entity type. Each entity
        type contains a list of attributes that can be used in trigger
        conditions and actions.

        Returns:
            TriggerAttributes object with all attribute definitions.

        Raises:
            UpsalesError: If API request fails.

        Example:
            >>> attrs = await upsales.trigger_attributes.get()
            >>> attrs.entity_types
            ['Activity', 'Agreement', 'AgreementProduct', 'Appointment', ...]
            >>> attrs.total_attributes
            450
            >>> client_attrs = attrs.get_entity_attributes('Client')
            >>> client_attrs[0].id
            'Client.Name'
        """
        response = await self._http.get(self._endpoint)
        # Extract data from response wrapper and pass to model
        return TriggerAttributes(**response["data"], _client=self._http._upsales_client)

    async def get_entity_attributes(self, entity_type: str) -> list[TriggerAttribute]:
        """
        Get all attributes for a specific entity type.

        Convenience method to get attributes for a single entity without
        fetching the full structure.

        Args:
            entity_type: Entity type (e.g., 'Client', 'Contact', 'Order',
                'Activity', 'Appointment', 'Agreement', 'Project', 'Lead')

        Returns:
            List of TriggerAttribute objects for the entity type.

        Raises:
            KeyError: If entity type not found.
            UpsalesError: If API request fails.

        Example:
            >>> client_attrs = await upsales.trigger_attributes.get_entity_attributes('Client')
            >>> len(client_attrs)
            75
            >>> client_attrs[0].name
            'Name'
        """
        attrs = await self.get()
        return attrs.get_entity_attributes(entity_type)

    async def get_criteria_attributes(self, entity_type: str) -> list[TriggerAttribute]:
        """
        Get attributes that can be used as criteria for an entity type.

        Returns only attributes where asCriteria is True, meaning they can
        be used in trigger condition rules.

        Args:
            entity_type: Entity type (e.g., 'Client', 'Contact', 'Order')

        Returns:
            List of TriggerAttribute objects that can be used as criteria.

        Raises:
            KeyError: If entity type not found.
            UpsalesError: If API request fails.

        Example:
            >>> criteria = await upsales.trigger_attributes.get_criteria_attributes('Contact')
            >>> all(attr.can_be_criteria for attr in criteria)
            True
            >>> len(criteria)
            15
        """
        attrs = await self.get()
        return attrs.get_criteria_attributes(entity_type)

    async def get_attribute_by_id(self, attribute_id: str) -> TriggerAttribute | None:
        """
        Get a specific attribute by its ID.

        Args:
            attribute_id: Attribute ID (e.g., 'Client.Name', 'Contact.Email')

        Returns:
            TriggerAttribute if found, None otherwise.

        Raises:
            UpsalesError: If API request fails.

        Example:
            >>> attr = await upsales.trigger_attributes.get_attribute_by_id('Client.Name')
            >>> attr.type
            'string'
            >>> attr.can_be_criteria
            True
        """
        attrs = await self.get()
        return attrs.get_attribute_by_id(attribute_id)

    async def find_attributes_by_type(
        self, data_type: str, entity_type: str | None = None
    ) -> list[TriggerAttribute]:
        """
        Find all attributes with a specific data type.

        Useful for finding all date fields, user fields, etc. across one or
        all entity types.

        Args:
            data_type: Data type to search for (e.g., 'string', 'date', 'user',
                'integer', 'boolean', 'client', 'contact', 'project')
            entity_type: Optional entity type to limit search (searches all if None)

        Returns:
            List of matching TriggerAttribute objects.

        Raises:
            UpsalesError: If API request fails.

        Example:
            >>> # Find all date fields
            >>> date_attrs = await upsales.trigger_attributes.find_attributes_by_type('date')
            >>> len(date_attrs)
            25
            >>> # Find date fields only for Client
            >>> client_dates = await upsales.trigger_attributes.find_attributes_by_type(
            ...     'date', 'Client'
            ... )
            >>> len(client_dates)
            1
        """
        attrs = await self.get()
        return attrs.find_attributes_by_type(data_type, entity_type)

    async def get_select_attributes(self, entity_type: str) -> list[TriggerAttribute]:
        """
        Get all select/dropdown type attributes for an entity type.

        Returns attributes that have selectText defined, indicating they are
        dropdown/select fields with predefined options.

        Args:
            entity_type: Entity type (e.g., 'Client', 'Contact', 'Order')

        Returns:
            List of TriggerAttribute objects that are select types.

        Raises:
            KeyError: If entity type not found.
            UpsalesError: If API request fails.

        Example:
            >>> selects = await upsales.trigger_attributes.get_select_attributes('Client')
            >>> all(attr.is_select_type for attr in selects)
            True
            >>> selects[0].selectText
            'name'
        """
        attrs = await self.get()
        return attrs.get_select_attributes(entity_type)

    async def get_attributes_by_feature(self, feature: str) -> list[TriggerAttribute]:
        """
        Get all attributes that require a specific feature flag.

        Some attributes are only available when certain features are enabled
        in the Upsales installation.

        Args:
            feature: Feature flag name (e.g., 'NEW_FIELDS', 'PRICE_LISTS',
                'TODO_LIST', 'APPOINTMENT_OUTCOME')

        Returns:
            List of TriggerAttribute objects requiring the feature.

        Raises:
            UpsalesError: If API request fails.

        Example:
            >>> new_fields = await upsales.trigger_attributes.get_attributes_by_feature(
            ...     'NEW_FIELDS'
            ... )
            >>> all(attr.feature == 'NEW_FIELDS' for attr in new_fields)
            True
            >>> len(new_fields)
            40
        """
        attrs = await self.get()
        return attrs.get_attributes_by_feature(feature)

    async def get_entity_types(self) -> list[str]:
        """
        Get list of all available entity types.

        Returns:
            List of entity type names.

        Raises:
            UpsalesError: If API request fails.

        Example:
            >>> types = await upsales.trigger_attributes.get_entity_types()
            >>> 'Client' in types
            True
            >>> 'Contact' in types
            True
            >>> len(types)
            19
        """
        attrs = await self.get()
        return attrs.entity_types
