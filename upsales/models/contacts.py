"""
Contact models for Upsales API.

Generated from /api/v2/contacts endpoint.
Analysis based on 106 samples.

Enhanced with Pydantic v2 features:
- Reusable validators (BinaryFlag, EmailStr, CustomFieldsList, NonEmptyStr)
- Computed fields (@computed_field)
- Field serialization (@field_serializer)
- Strict type checking
- Field descriptions
- Optimized serialization
"""

from typing import Any, TypedDict, Unpack

from pydantic import Field, computed_field, field_serializer

from upsales.models.base import BaseModel, PartialModel
from upsales.models.company import PartialCompany
from upsales.models.custom_fields import CustomFields
from upsales.models.journey_step import PartialJourneyStep
from upsales.models.projects import PartialProject
from upsales.models.segments import PartialSegment
from upsales.validators import BinaryFlag, CustomFieldsList, EmailStr, NonEmptyStr


class ContactCreateFields(TypedDict, total=False):
    """
    Required and optional fields for creating a new Contact.

    REQUIRED fields (verified 2025-11-07):
    - client: Dict with client.id (company/account reference)

    IMPORTANT: Only client.id is required! All other fields are optional.
    Email is NOT required (API file was incorrect on this).

    The client field uses minimal nested structure with just ID.
    Example: {"id": 123} NOT the full PartialCompany object.

    Example Minimal:
        >>> new_contact = await upsales.contacts.create(
        ...     client={"id": 123}
        ... )

    Example With Optional Fields:
        >>> detailed_contact = await upsales.contacts.create(
        ...     client={"id": 123},
        ...     name="John Doe",
        ...     email="john@example.com",
        ...     phone="+1-555-0123",
        ...     title="Sales Manager",
        ... )
    """

    # REQUIRED field
    client: dict[str, int]  # Required: {"id": client_id}

    # OPTIONAL fields
    email: str  # Optional (API file incorrectly listed as required)
    name: str
    firstName: str
    lastName: str
    phone: str
    cellPhone: str
    phoneCountryCode: str
    cellPhoneCountryCode: str
    title: str
    salutation: str
    active: int
    notes: str
    linkedin: str
    custom: list[dict[str, Any]]
    categories: list[dict[str, Any]]
    projects: list[dict[str, Any]]
    segments: list[dict[str, Any]]


class ContactUpdateFields(TypedDict, total=False):
    """
    Available fields for updating a Contact.

    All fields are optional. Use with Unpack for IDE autocomplete.
    Excludes read-only fields (id, regDate, modDate).
    """

    active: int
    categories: list[Any]
    cellPhone: str | None
    cellPhoneCountryCode: str | None
    client: dict[str, Any]
    connectedClients: list[Any]
    custom: list[Any]
    email: str
    emailBounceReason: str
    firstName: str
    firstTouch: dict[str, Any] | None
    hadActivity: Any | None
    hadAppointment: str | None
    hadOpportunity: Any | None
    hadOrder: Any | None
    hasActivity: str | None
    hasAppointment: Any | None
    hasForm: bool
    hasMail: bool
    hasOpportunity: str | None
    hasOrder: Any | None
    hasVisit: bool
    importId: Any | None
    isPriority: bool
    journeyStep: str
    lastName: str
    linkedin: str | None
    mailBounces: list[Any]
    name: str
    notes: str | None
    optins: list[Any]
    phone: str | None
    phoneCountryCode: str | None
    projects: list[PartialProject]
    regBy: dict[str, Any] | None
    salutation: str | None
    score: int
    scoreUpdateDate: str | None
    segments: list[dict[str, Any]]
    socialEvent: list[Any]
    supportTickets: dict[str, Any]
    title: str | None
    titleCategory: str | None
    unsubscribed: Any | None
    unsubscribedMailCampaign: Any | None
    userEditable: bool
    userRemovable: bool


class Contact(BaseModel):
    """
    Contact model from /api/v2/contacts.

    Represents a contact in the Upsales system with full data. Enhanced with
    Pydantic v2 validators, computed fields, and optimized serialization.

    Generated from 106 samples with field analysis.

    CREATING CONTACTS (verified 2025-11-07):
        Use ContactCreateFields TypedDict for required field reference.
        Only ONE field is required (client.id with minimal nested structure):
        - client: {"id": client_id}

        Email is OPTIONAL (API file incorrectly listed it as required).

    UPDATING CONTACTS:
        Use ContactUpdateFields TypedDict for IDE autocomplete.
        All fields optional.

    Example Create (minimal):
        >>> new_contact = await upsales.contacts.create(
        ...     client={"id": 123}
        ... )
        >>> new_contact.id
        702

    Example Create (with optional fields):
        >>> detailed_contact = await upsales.contacts.create(
        ...     client={"id": 123},
        ...     name="John Doe",
        ...     email="john@example.com",
        ...     phone="+1-555-0123",
        ...     title="Sales Manager",
        ... )

    Example Read:
        >>> contact = await upsales.contacts.get(1)
        >>> contact.name
        'John Doe'
        >>> contact.is_active  # Computed property
        True
        >>> contact.full_name  # Computed from firstName + lastName
        'John Doe'
        >>> contact.custom_fields[11]  # Access custom fields
        'value'

    Example Update:
        >>> await contact.edit(email="new@example.com")  # IDE autocomplete
    """

    # Read-only fields (frozen=True)
    id: int = Field(frozen=True, strict=True, description="Unique contact ID")
    regDate: str | None = Field(None, frozen=True, description="Registration date")
    modDate: str = Field(frozen=True, description="Last modification date")

    # Fields that API can return as empty strings (all have defaults)
    name: str = Field(default="", description="Contact's full name (can be empty)")
    firstName: str = Field(default="", description="Contact's first name")
    lastName: str = Field(default="", description="Contact's last name")
    email: str = Field(default="", description="Contact's email (optional, can be empty)")
    emailBounceReason: str = Field(
        default="", description="Email bounce reason (empty if no bounces)"
    )
    journeyStep: str = Field(default="", description="Contact's position in customer journey")

    # Binary flags (validated 0 or 1)
    active: BinaryFlag = Field(default=1, description="Active status (0=inactive, 1=active)")
    hasForm: bool = Field(description="Has submitted a form")
    hasMail: bool = Field(description="Has received email")
    hasVisit: bool = Field(description="Has visited website")
    isPriority: bool = Field(description="Priority contact flag")
    userEditable: bool = Field(description="User can edit this contact")
    userRemovable: bool = Field(description="User can remove this contact")

    # Custom fields (validated structure)
    custom: CustomFieldsList = Field(
        default=[], description="Custom fields with validated structure"
    )

    # Numeric fields
    score: int = Field(default=0, description="Contact score (lead scoring)")

    # List fields
    categories: list[Any] = Field(default=[], description="Contact categories")
    connectedClients: list[Any] = Field(default=[], description="Connected companies")
    mailBounces: list[Any] = Field(default=[], description="Email bounce history")
    optins: list[Any] = Field(default=[], description="Marketing opt-ins")
    projects: list[PartialProject] = Field(default=[], description="Associated projects")
    segments: list[PartialSegment] = Field(default=[], description="Contact segments")
    socialEvent: list[Any] = Field(default=[], description="Social media events")

    # Dict fields
    client: PartialCompany = Field(description="Associated company data")
    firstTouch: dict[str, Any] | None = Field(default={}, description="First touch attribution")
    regBy: dict[str, Any] | None = Field(default={}, description="Registered by user")
    supportTickets: dict[str, Any] = Field(default={}, description="Support ticket data")

    # Optional fields
    cellPhone: str | None = Field(None, description="Cell phone number")
    cellPhoneCountryCode: str | None = Field(None, description="Cell phone country code")
    hadActivity: Any | None = Field(None, description="Had activity timestamp")
    hadAppointment: str | None = Field(None, description="Had appointment timestamp")
    hadOpportunity: Any | None = Field(None, description="Had opportunity timestamp")
    hadOrder: Any | None = Field(None, description="Had order timestamp")
    hasActivity: str | None = Field(None, description="Has active activity")
    hasAppointment: Any | None = Field(None, description="Has active appointment")
    hasOpportunity: str | None = Field(None, description="Has active opportunity")
    hasOrder: Any | None = Field(None, description="Has active order")
    importId: Any | None = Field(None, description="Import ID for tracking")
    linkedin: str | None = Field(None, description="LinkedIn profile URL")
    notes: str | None = Field(None, description="Contact notes")
    phone: str | None = Field(None, description="Phone number")
    phoneCountryCode: str | None = Field(None, description="Phone country code")
    salutation: str | None = Field(None, description="Salutation (Mr., Ms., etc.)")
    scoreUpdateDate: str | None = Field(None, description="Last score update date")
    title: str | None = Field(None, description="Contact's job title")
    titleCategory: str | None = Field(None, description="Job title category")
    unsubscribed: Any | None = Field(None, description="Unsubscribed timestamp")
    unsubscribedMailCampaign: Any | None = Field(
        None, description="Unsubscribed from mail campaign"
    )

    @computed_field
    @property
    def custom_fields(self) -> CustomFields:
        """
        Access custom fields with dict-like interface.

        Returns:
            CustomFields helper for easy access by ID or alias.

        Example:
            >>> contact.custom_fields[11]  # By field ID
            'value'
            >>> contact.custom_fields.get(11, "default")
            'value'
        """
        return CustomFields(self.custom)

    @computed_field
    @property
    def is_active(self) -> bool:
        """
        Check if contact is active.

        Returns:
            True if active flag is 1, False otherwise.

        Example:
            >>> contact.is_active
            True
        """
        return self.active == 1

    @computed_field
    @property
    def full_name(self) -> str:
        """
        Get full name from first and last name.

        Returns:
            Combined first and last name, falling back to name field.

        Example:
            >>> contact.full_name
            'John Doe'
        """
        if self.firstName and self.lastName:
            return f"{self.firstName} {self.lastName}"
        return self.name

    @computed_field
    @property
    def has_phone(self) -> bool:
        """
        Check if contact has phone or cell phone.

        Returns:
            True if phone or cellPhone is set, False otherwise.

        Example:
            >>> contact.has_phone
            True
        """
        return bool(self.phone or self.cellPhone)

    @field_serializer("custom", when_used="json")
    def serialize_custom_fields(self, custom: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Serialize custom fields for API requests.

        Removes any fields without values to keep API payloads clean.

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

    async def edit(self, **kwargs: Unpack[ContactUpdateFields]) -> "Contact":
        """
        Edit this contact.

        Uses Pydantic v2's optimized serialization via to_api_dict().
        With Python 3.13 free-threaded mode, multiple edits can run
        in true parallel without GIL contention.

        Args:
            **kwargs: Fields to update (full IDE autocomplete support).

        Returns:
            Updated contact with fresh data from API.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> contact = await upsales.contacts.get(1)
            >>> updated = await contact.edit(
            ...     name="Jane Doe",
            ...     email="jane@example.com",
            ...     active=1
            ... )
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.contacts.update(self.id, **self.to_api_dict(**kwargs))


class PartialContact(PartialModel):
    """
    Partial Contact for nested responses.

    Contains minimal fields for when Contact appears nested in other
    API responses (e.g., as opportunity owner, company contact, etc.).

    Use fetch_full() to get complete Contact object with all fields.

    Example:
        >>> opportunity = await upsales.opportunities.get(1)
        >>> owner = opportunity.owner  # PartialContact
        >>> full_contact = await owner.fetch_full()  # Now Contact
    """

    id: int = Field(frozen=True, strict=True, description="Unique contact ID")
    name: NonEmptyStr = Field(description="Contact's name")
    email: EmailStr | None = Field(None, description="Contact's email")
    journeyStep: PartialJourneyStep | None = Field(None, description="Contact's journey step")

    async def fetch_full(self) -> Contact:
        """
        Fetch complete contact data.

        Returns:
            Full Contact object with all fields populated.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> partial = opportunity.owner  # PartialContact
            >>> full = await partial.fetch_full()  # Contact
            >>> full.phone  # Now available
            '+1-555-0123'
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.contacts.get(self.id)

    async def edit(self, **kwargs: Any) -> Contact:
        """
        Edit contact via partial reference.

        Args:
            **kwargs: Fields to update.

        Returns:
            Updated full Contact object from API.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> partial = opportunity.owner  # PartialContact
            >>> updated = await partial.edit(name="New Name")  # Returns Contact
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.contacts.update(self.id, **kwargs)
