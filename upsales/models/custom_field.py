"""
CustomField models for Upsales API.

Custom fields are user-defined fields that can be added to various entities
(accounts, orders, products, contacts, etc.) in Upsales.

Based on analysis of 13 entities with 57 total custom fields.
"""

from typing import Any, Literal, TypedDict, Unpack

from pydantic import Field

from upsales.models.base import BaseModel, PartialModel
from upsales.validators import BinaryFlag, NonEmptyStr

# All custom field types discovered across all entities
CustomFieldType = Literal[
    "String",  # Text input (max 1024-65535 chars)
    "Text",  # Large text area
    "Integer",  # Numeric input
    "Currency",  # Money values
    "Percent",  # Percentage 0-100
    "Boolean",  # Yes/No checkbox
    "Date",  # Date picker
    "Time",  # Time picker
    "Email",  # Email input
    "Phone",  # Phone input
    "Link",  # URL input
    "Select",  # Dropdown (single selection)
    "MultiSelect",  # Multi-select dropdown
    "User",  # User reference
    "Discount",  # Discount value
    "Calculation",  # Formula/calculated field
]


class CustomFieldUpdateFields(TypedDict, total=False):
    """
    Available fields for updating a CustomField.

    All fields are optional (total=False).
    """

    name: str
    datatype: str
    alias: str
    visible: int
    editable: int
    locked: int
    viewonly: int
    obligatoryField: int
    searchable: int
    lookupField: int
    default: Any
    dropdownDefault: Any
    sortId: int
    maxLength: int
    query: Any
    formGroup: Any
    roles: list[Any]
    tooltip: str
    integrationDependency: Any
    formula: str
    formulaVisible: int
    stages: list[Any]
    categories: list[Any]


class CustomField(BaseModel):
    """
    Custom field definition from /api/v2/customFields/{entity}.

    Unified model for all entities (account, order, product, contact, etc.)
    with optional entity-specific fields.

    Supports 16 field types: String, Text, Integer, Currency, Percent,
    Boolean, Date, Time, Email, Phone, Link, Select, MultiSelect, User,
    Discount, Calculation.

    Entity-specific fields:
    - formula, formulaVisible, stages: order/orderrow only
    - categories: product only

    Example:
        >>> # Get all custom fields for accounts
        >>> fields = await upsales.custom_fields.list_for_entity("account")
        >>>
        >>> # Create String field
        >>> field = await upsales.custom_fields.create(
        ...     entity="account",
        ...     name="VAT Number",
        ...     datatype="String",
        ...     alias="VAT_NO",
        ...     visible=1
        ... )
        >>>
        >>> # Create Select field with options
        >>> select = await upsales.custom_fields.create(
        ...     entity="account",
        ...     name="Priority",
        ...     datatype="Select",
        ...     alias="PRIORITY",
        ...     default=["Low", "Medium", "High"]  # Options in default!
        ... )
        >>>
        >>> # Create Calculation field (order only)
        >>> calc = await upsales.custom_fields.create(
        ...     entity="order",
        ...     name="Total Plus Tax",
        ...     datatype="Calculation",
        ...     alias="TOTAL_TAX",
        ...     formula="{Order.value} * 1.25"  # Formula!
        ... )
    """

    # Fields required for updates based on testing
    _required_update_fields: set[str] = {"name", "datatype", "alias"}

    # Read-only fields
    id: int = Field(frozen=True, strict=True, description="Unique custom field ID")

    # Required fields (always present)
    name: NonEmptyStr = Field(description="Field display name")
    datatype: CustomFieldType = Field(description="Field type (String, Select, etc.)")
    alias: str | None = Field(
        None, description="Field alias for API access (e.g., VAT_NO, can be None)"
    )

    # Boolean flags (0 or 1)
    visible: BinaryFlag = Field(default=1, description="Visible in UI (0=hidden, 1=visible)")
    editable: BinaryFlag = Field(default=1, description="User can edit (0=read-only, 1=editable)")
    locked: BinaryFlag = Field(default=0, description="Locked from changes (0=unlocked, 1=locked)")
    viewonly: BinaryFlag = Field(default=0, description="View only (0=can edit, 1=view only)")
    obligatoryField: BinaryFlag = Field(
        default=0, description="Required field (0=optional, 1=required)"
    )
    searchable: BinaryFlag = Field(
        default=0, description="Searchable (0=not searchable, 1=searchable)"
    )
    lookupField: BinaryFlag = Field(default=0, description="Lookup field (0=no, 1=yes)")

    # Common optional fields
    default: Any | None = Field(None, description="Default value (for Select: array of options!)")
    dropdownDefault: Any | None = Field(None, description="Default dropdown selection")
    sortId: int = Field(default=0, description="Sort order for display")
    maxLength: int = Field(default=1024, description="Maximum length (for String/Text types)")
    query: Any | None = Field(None, description="Query definition (complex)")
    formGroup: Any | None = Field(None, description="Form group for organization")
    roles: list[Any] = Field(default=[], description="Associated roles (access control)")
    tooltip: str | None = Field(None, description="Tooltip help text")
    integrationDependency: Any | None = Field(None, description="Integration dependency")

    # Entity-specific fields (optional)
    formula: str | None = Field(
        None, description="Calculation formula (Calculation type on order/orderrow only)"
    )
    formulaVisible: BinaryFlag | None = Field(
        None, description="Formula visible (order/orderrow only)"
    )
    stages: list[Any] = Field(
        default=[], description="Order stages where field appears (order/orderrow only)"
    )
    categories: list[Any] = Field(default=[], description="Product categories (product only)")

    async def edit(self, **kwargs: Unpack[CustomFieldUpdateFields]) -> "CustomField":
        """
        Edit this custom field definition.

        Args:
            **kwargs: Fields to update.

        Returns:
            Updated CustomField.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> field = await upsales.custom_fields.get(11, entity="account")
            >>> updated = await field.edit(
            ...     name="Updated Name",
            ...     visible=0  # Hide field
            ... )
        """
        if not self._client:
            raise RuntimeError("No client available")
        # Note: CustomFields API might need entity parameter
        # This will be determined during resource implementation
        raise NotImplementedError(
            "CustomField.edit() requires CustomFieldsResource to be registered. "
            "Use upsales.custom_fields.update(field.id, entity='account', **kwargs)"
        )


class PartialCustomField(PartialModel):
    """
    Partial CustomField for nested responses.

    Minimal fields when custom field reference appears in other objects.

    Example:
        >>> # If custom field appears nested
        >>> if hasattr(obj, 'customFieldDefinition'):
        ...     field_def = obj.customFieldDefinition  # PartialCustomField
        ...     print(field_def.name, field_def.datatype)
    """

    id: int = Field(frozen=True, strict=True, description="Custom field ID")
    name: NonEmptyStr = Field(description="Field name")
    datatype: CustomFieldType = Field(description="Field type")
    alias: str = Field(description="Field alias")

    async def fetch_full(self) -> CustomField:
        """
        Fetch complete custom field definition.

        Note: Requires entity parameter (which entity this field belongs to).
        May need to be called differently.

        Raises:
            NotImplementedError: Until CustomFieldsResource is implemented.
        """
        raise NotImplementedError(
            "PartialCustomField.fetch_full() requires knowing the entity. "
            "Use: await upsales.custom_fields.get(field.id, entity='account')"
        )

    async def edit(self, **kwargs: Any) -> CustomField:
        """Edit this custom field."""
        raise NotImplementedError(
            "Use: await upsales.custom_fields.update(field.id, entity='account', **kwargs)"
        )
