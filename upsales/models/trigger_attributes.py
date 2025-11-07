"""
Trigger attribute models for Upsales API.

The /api/v2/triggerAttributes endpoint returns available attributes for triggers
and automation rules. Unlike typical REST endpoints, this returns a dict where keys
are entity types (Client, Contact, Order, etc.) and values are lists of attributes.

This is a read-only endpoint containing schema metadata for automation triggers.
"""

from typing import TYPE_CHECKING, Any

from pydantic import BaseModel as PydanticBase
from pydantic import ConfigDict, Field, computed_field

if TYPE_CHECKING:
    from upsales.client import Upsales

from upsales.validators import NonEmptyStr


class TriggerAttribute(PydanticBase):
    """
    Single trigger attribute definition.

    Represents an attribute that can be used in trigger conditions or actions.
    These attributes define what fields are available for automation rules.

    Attributes:
        id: Attribute identifier (e.g., 'Client.Name', 'Contact.Email')
        name: Display name of the attribute
        type: Data type (string, integer, date, boolean, user, etc.)
        lang: Language key for internationalization
        asCriteria: Whether attribute can be used as criteria in trigger conditions
        selectText: Field to use for display in select dropdowns (optional)
        idAttribute: Field to use as ID for select options (optional)
        feature: Feature flag requirement (optional)
        min: Minimum value for numeric types (optional)
        max: Maximum value for numeric types (optional)

    Example:
        >>> attributes = await upsales.trigger_attributes.get()
        >>> client_attrs = attributes.get_entity_attributes('Client')
        >>> name_attr = client_attrs[0]
        >>> name_attr.id
        'Client.Name'
        >>> name_attr.can_be_criteria
        True
    """

    model_config = ConfigDict(
        frozen=False,
        validate_assignment=True,
        extra="allow",
        populate_by_name=True,
    )

    id: NonEmptyStr = Field(description="Attribute identifier (e.g., 'Client.Name')")
    name: NonEmptyStr = Field(description="Display name of the attribute")
    type: str | None = Field(None, description="Data type (string, integer, date, etc.)")
    lang: NonEmptyStr = Field(description="Language key for internationalization")
    asCriteria: bool = Field(description="Whether attribute can be used as criteria")
    selectText: str | None = Field(None, description="Field to use for display in select dropdowns")
    idAttribute: str | None = Field(None, description="Field to use as ID for select options")
    feature: str | None = Field(None, description="Feature flag requirement")
    min: int | None = Field(None, description="Minimum value for numeric types")
    max: int | None = Field(None, description="Maximum value for numeric types")

    @computed_field
    @property
    def can_be_criteria(self) -> bool:
        """
        Check if attribute can be used as criteria in trigger conditions.

        Returns:
            True if can be used as criteria, False otherwise.

        Example:
            >>> attr.can_be_criteria
            True
        """
        return self.asCriteria

    @computed_field
    @property
    def is_select_type(self) -> bool:
        """
        Check if attribute is a select/dropdown type.

        Returns:
            True if attribute has select options, False otherwise.

        Example:
            >>> attr.is_select_type
            True
        """
        return self.selectText is not None

    @computed_field
    @property
    def has_range(self) -> bool:
        """
        Check if attribute has min/max range constraints.

        Returns:
            True if attribute has range constraints, False otherwise.

        Example:
            >>> attr.has_range
            False
        """
        return self.min is not None or self.max is not None

    @computed_field
    @property
    def requires_feature(self) -> bool:
        """
        Check if attribute requires a specific feature flag.

        Returns:
            True if feature flag required, False otherwise.

        Example:
            >>> attr.requires_feature
            False
        """
        return self.feature is not None

    @computed_field
    @property
    def entity_type(self) -> str:
        """
        Extract entity type from attribute ID.

        Returns:
            Entity type (e.g., 'Client', 'Contact', 'Order').

        Example:
            >>> attr.entity_type
            'Client'
        """
        return self.id.split(".")[0] if "." in self.id else ""

    @computed_field
    @property
    def field_name(self) -> str:
        """
        Extract field name from attribute ID.

        Returns:
            Field name (e.g., 'Name', 'Email', 'Phone').

        Example:
            >>> attr.field_name
            'Name'
        """
        return self.id.split(".", 1)[1] if "." in self.id else self.id


class TriggerAttributes(PydanticBase):
    """
    Complete trigger attributes data from /api/v2/triggerAttributes.

    Contains attribute definitions for all entity types. This is a read-only
    endpoint that provides schema metadata for building automation triggers.

    The data structure is a dict where keys are entity types and values are
    lists of TriggerAttribute objects.

    Attributes:
        attributes: Dictionary mapping entity types to their attribute lists

    Example:
        >>> attributes = await upsales.trigger_attributes.get()
        >>> len(attributes.entity_types)
        19
        >>> 'Client' in attributes.entity_types
        True
        >>> client_attrs = attributes.get_entity_attributes('Client')
        >>> len(client_attrs)
        75
    """

    model_config = ConfigDict(
        frozen=False,
        validate_assignment=True,
        arbitrary_types_allowed=True,
        extra="allow",
        populate_by_name=True,
    )

    attributes: dict[str, list[TriggerAttribute]] = Field(
        default_factory=dict,
        description="Dictionary mapping entity types to attribute lists",
    )

    _client: "Upsales | None" = None

    def __init__(self, **data: Any) -> None:
        """
        Initialize trigger attributes with optional client reference.

        Args:
            **data: Trigger attributes data from API.
        """
        client = data.pop("_client", None)
        # The API returns the dict directly in 'data' field
        # We need to transform it into our attributes structure
        if "attributes" not in data and any(
            key
            in [
                "Client",
                "Contact",
                "Order",
                "Activity",
                "Appointment",
                "Project",
                "Agreement",
            ]
            for key in data
        ):
            # Raw API response - wrap it in attributes dict
            attributes_dict = {}
            for entity_type, attrs in data.items():
                if isinstance(attrs, list):
                    attributes_dict[entity_type] = [TriggerAttribute(**attr) for attr in attrs]
            data = {"attributes": attributes_dict}

        super().__init__(**data)
        object.__setattr__(self, "_client", client)

    @computed_field
    @property
    def entity_types(self) -> list[str]:
        """
        Get list of available entity types.

        Returns:
            List of entity type names.

        Example:
            >>> attributes.entity_types
            ['Client', 'Contact', 'Order', 'Activity', ...]
        """
        return sorted(self.attributes.keys())

    @computed_field
    @property
    def total_attributes(self) -> int:
        """
        Get total number of attributes across all entity types.

        Returns:
            Total attribute count.

        Example:
            >>> attributes.total_attributes
            450
        """
        return sum(len(attrs) for attrs in self.attributes.values())

    def get_entity_attributes(self, entity_type: str) -> list[TriggerAttribute]:
        """
        Get all attributes for a specific entity type.

        Args:
            entity_type: Entity type (e.g., 'Client', 'Contact', 'Order')

        Returns:
            List of TriggerAttribute objects for the entity type.

        Raises:
            KeyError: If entity type not found.

        Example:
            >>> client_attrs = attributes.get_entity_attributes('Client')
            >>> len(client_attrs)
            75
            >>> client_attrs[0].name
            'Name'
        """
        return self.attributes[entity_type]

    def get_criteria_attributes(self, entity_type: str) -> list[TriggerAttribute]:
        """
        Get attributes that can be used as criteria for an entity type.

        Args:
            entity_type: Entity type (e.g., 'Client', 'Contact', 'Order')

        Returns:
            List of TriggerAttribute objects that can be used as criteria.

        Raises:
            KeyError: If entity type not found.

        Example:
            >>> criteria = attributes.get_criteria_attributes('Client')
            >>> all(attr.can_be_criteria for attr in criteria)
            True
        """
        return [attr for attr in self.attributes[entity_type] if attr.can_be_criteria]

    def get_attribute_by_id(self, attribute_id: str) -> TriggerAttribute | None:
        """
        Get a specific attribute by its ID.

        Args:
            attribute_id: Attribute ID (e.g., 'Client.Name', 'Contact.Email')

        Returns:
            TriggerAttribute if found, None otherwise.

        Example:
            >>> attr = attributes.get_attribute_by_id('Client.Name')
            >>> attr.type
            'string'
            >>> attr.can_be_criteria
            True
        """
        entity_type = attribute_id.split(".")[0] if "." in attribute_id else None
        if not entity_type or entity_type not in self.attributes:
            return None

        return next(
            (attr for attr in self.attributes[entity_type] if attr.id == attribute_id),
            None,
        )

    def find_attributes_by_type(
        self, data_type: str, entity_type: str | None = None
    ) -> list[TriggerAttribute]:
        """
        Find all attributes with a specific data type.

        Args:
            data_type: Data type to search for (e.g., 'string', 'date', 'user')
            entity_type: Optional entity type to limit search (searches all if None)

        Returns:
            List of matching TriggerAttribute objects.

        Example:
            >>> date_attrs = attributes.find_attributes_by_type('date')
            >>> len(date_attrs)
            25
            >>> client_dates = attributes.find_attributes_by_type('date', 'Client')
            >>> len(client_dates)
            1
        """
        results: list[TriggerAttribute] = []
        search_entities = [entity_type] if entity_type else self.attributes.keys()

        for entity in search_entities:
            if entity in self.attributes:
                results.extend(attr for attr in self.attributes[entity] if attr.type == data_type)

        return results

    def get_select_attributes(self, entity_type: str) -> list[TriggerAttribute]:
        """
        Get all select/dropdown type attributes for an entity type.

        Args:
            entity_type: Entity type (e.g., 'Client', 'Contact', 'Order')

        Returns:
            List of TriggerAttribute objects that are select types.

        Raises:
            KeyError: If entity type not found.

        Example:
            >>> selects = attributes.get_select_attributes('Client')
            >>> all(attr.is_select_type for attr in selects)
            True
        """
        return [attr for attr in self.attributes[entity_type] if attr.is_select_type]

    def get_attributes_by_feature(self, feature: str) -> list[TriggerAttribute]:
        """
        Get all attributes that require a specific feature flag.

        Args:
            feature: Feature flag name (e.g., 'NEW_FIELDS', 'PRICE_LISTS')

        Returns:
            List of TriggerAttribute objects requiring the feature.

        Example:
            >>> new_fields = attributes.get_attributes_by_feature('NEW_FIELDS')
            >>> all(attr.feature == 'NEW_FIELDS' for attr in new_fields)
            True
        """
        results: list[TriggerAttribute] = []
        for attrs in self.attributes.values():
            results.extend(attr for attr in attrs if attr.feature == feature)
        return results
