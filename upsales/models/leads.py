"""
Lead models for Upsales API.

Generated from /api/v2/leads endpoint.

Enhanced with Pydantic v2 features:
- Reusable validators (BinaryFlag, CustomFieldsList, EmailStr)
- Computed fields (@computed_field)
- Field serialization (@field_serializer)
- Strict type checking
- Field descriptions
- Optimized serialization
"""

from typing import TYPE_CHECKING, Any, TypedDict, Unpack

from pydantic import Field, computed_field, field_serializer

from upsales.models.base import BaseModel, PartialModel
from upsales.models.custom_fields import CustomFields
from upsales.validators import BinaryFlag, CustomFieldsList, EmailStr

if TYPE_CHECKING:
    from upsales.models.campaign import PartialCampaign
    from upsales.models.company import PartialCompany
    from upsales.models.user import PartialUser


class LeadUpdateFields(TypedDict, total=False):
    """
    Available fields for updating a Lead.

    All fields are optional. Use with Unpack for IDE autocomplete.

    Note:
        Excludes read-only fields: id, regDate, modDate, userRemovable, userEditable
    """

    name: str
    description: str
    contact: str
    email: str
    phone: str
    address: str
    active: int
    custom: list[dict[str, Any]]
    source: dict[str, Any]
    channel: dict[str, Any]
    client: dict[str, Any]
    project: dict[str, Any]
    user: dict[str, Any]


class Lead(BaseModel):
    """
    Lead model from /api/v2/leads.

    Represents a lead/prospect in the Upsales system.

    Example:
        >>> lead = await upsales.leads.get(1)
        >>> lead.name
        'New Prospect'
        >>> lead.is_active
        True
        >>> lead.custom_fields[11]
        'value'
    """

    # Read-only fields (frozen=True, strict=True)
    id: int = Field(frozen=True, strict=True, description="Unique lead ID")
    regDate: str | None = Field(None, frozen=True, description="Registration date")
    modDate: str | None = Field(None, frozen=True, description="Last modification date")
    userRemovable: bool = Field(True, frozen=True, description="User can remove")
    userEditable: bool = Field(True, frozen=True, description="User can edit")

    # Optional core fields
    name: str | None = Field(None, description="Lead name")
    description: str | None = Field(None, description="Lead description")
    contact: str | None = Field(None, description="Contact person name")
    email: EmailStr | None = Field(None, description="Email address")
    phone: str | None = Field(None, description="Phone number")
    address: str | None = Field(None, description="Address")
    active: BinaryFlag = Field(default=1, description="Active status (0=inactive, 1=active)")

    # List fields
    custom: CustomFieldsList = Field(default=[], description="Custom fields")

    # Relationship fields (nested objects)
    source: dict[str, Any] | None = Field(
        None, description="Lead source (required for CREATE, structure: {id: number})"
    )
    channel: dict[str, Any] | None = Field(
        None, description="Lead channel (structure: {id: number})"
    )
    client: "PartialCompany | None" = Field(
        None, alias="client", description="Associated company (structure: {id: number})"
    )
    project: "PartialCampaign | None" = Field(
        None, description="Associated project (structure: {id: number})"
    )
    user: "PartialUser | None" = Field(None, description="Assigned user (structure: {id: number})")

    @computed_field
    @property
    def custom_fields(self) -> CustomFields:
        """
        Access custom fields with dict-like interface.

        Returns:
            CustomFields helper for easy access by ID or alias.

        Example:
            >>> lead.custom_fields[11]  # By field ID
            'value'
            >>> lead.custom_fields["SOURCE_TYPE"] = "Web"  # By alias
        """
        return CustomFields(self.custom)

    @computed_field
    @property
    def is_active(self) -> bool:
        """
        Check if lead is active.

        Returns:
            True if active flag is 1, False otherwise.

        Example:
            >>> lead.is_active
            True
        """
        return self.active == 1

    @field_serializer("custom", when_used="json")
    def serialize_custom_fields(self, custom: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Serialize custom fields for API requests.

        Removes fields without values to keep payloads clean.

        Args:
            custom: List of custom field dicts.

        Returns:
            Cleaned list with only fields that have values.
        """
        return [
            {"fieldId": item["fieldId"], "value": item.get("value")}
            for item in custom
            if "value" in item and item.get("value") is not None
        ]

    async def edit(self, **kwargs: Unpack[LeadUpdateFields]) -> "Lead":
        """
        Edit this lead.

        Uses Pydantic v2's optimized serialization via to_api_dict().

        Args:
            **kwargs: Fields to update (full IDE autocomplete support).

        Returns:
            Updated lead with fresh data from API.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> lead = await upsales.leads.get(1)
            >>> updated = await lead.edit(
            ...     name="Updated Lead",
            ...     active=1,
            ...     email="new@example.com"
            ... )
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.leads.update(self.id, **self.to_api_dict(**kwargs))


class PartialLead(PartialModel):
    """
    Partial Lead for nested responses.

    Contains minimal fields for when Lead appears nested in other
    API responses.

    Use fetch_full() to get complete Lead object with all fields.

    Example:
        >>> # If lead appears nested somewhere
        >>> partial_lead = some_object.lead  # PartialLead
        >>> full_lead = await partial_lead.fetch_full()  # Lead
    """

    id: int = Field(frozen=True, strict=True, description="Unique lead ID")
    name: str | None = Field(None, description="Lead name")
    description: str | None = Field(None, description="Lead description")

    @computed_field
    @property
    def display_name(self) -> str:
        """
        Get display name for the lead.

        Returns:
            Lead name formatted for display.

        Example:
            >>> partial_lead.display_name
            'New Prospect'
        """
        return self.name or f"Lead #{self.id}"

    async def fetch_full(self) -> Lead:
        """
        Fetch complete lead data.

        Returns:
            Full Lead object with all fields populated.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> partial = some_object.lead  # PartialLead
            >>> full = await partial.fetch_full()  # Lead
            >>> full.email  # Now available
            'lead@example.com'
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.leads.get(self.id)

    async def edit(self, **kwargs: Unpack[LeadUpdateFields]) -> Lead:
        """
        Edit this lead.

        Returns full Lead object after update.

        Args:
            **kwargs: Fields to update (full IDE autocomplete support).

        Returns:
            Updated full Lead object.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> partial = some_object.lead  # PartialLead
            >>> updated = await partial.edit(name="Updated Lead")  # Returns Lead
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.leads.update(self.id, **kwargs)
