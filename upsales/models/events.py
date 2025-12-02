"""
Event models for Upsales API.

Event model for /api/v2/events endpoint.
Events represent activity timeline entries in Upsales.

Enhanced with Pydantic v2 features:
- Reusable validators (BinaryFlag, CustomFieldsList, NonEmptyStr)
- Computed fields (@computed_field)
- Field serialization (@field_serializer)
- Strict type checking
- Field descriptions
- Optimized serialization

Events can be manual entries, marketing activities, news updates, or system-generated
timeline entries linked to various entities (companies, contacts, opportunities, etc.).
"""

from typing import Any, TypedDict, Unpack

from pydantic import Field, computed_field

from upsales.models.base import BaseModel, PartialModel
from upsales.models.company import PartialCompany
from upsales.models.contacts import PartialContact
from upsales.models.orders import PartialOrder
from upsales.models.user import PartialUser
from upsales.validators import NonEmptyStr


class EventCreateFields(TypedDict, total=False):
    """
    Available fields for creating an Event.

    Required fields:
        entityType: Event type (e.g., 'manual', 'marketingCustom', 'news')
        score: Event score (set to 0 for reject-listed clients)

    All other fields are optional. Use with Unpack for IDE autocomplete.
    """

    # Required
    entityType: str
    score: int

    # Optional
    subType: str
    entityId: int
    client: dict[str, Any]
    contact: dict[str, Any]
    user: dict[str, Any]
    opportunityId: int
    integrationId: int
    externalId: str
    form: dict[str, Any]
    date: str
    value: str
    comment: dict[str, Any]
    brandId: int
    notify: bool


class EventUpdateFields(TypedDict, total=False):
    """
    Available fields for updating an Event.

    Note: The Upsales API does not support PUT/PATCH for events.
    This TypedDict is provided for consistency but edit() is not implemented.
    """

    entityType: str
    subType: str
    score: int
    value: str
    comment: dict[str, Any]


class Event(BaseModel):
    """
    Event model from /api/v2/events.

    Represents timeline events in Upsales. Enhanced with
    Pydantic v2 validators, computed fields, and optimized serialization.

    Events can be:
    - Manual entries
    - Marketing custom events
    - News updates
    - System-generated activities
    - Linked to companies, contacts, opportunities, agreements, etc.

    Example:
        >>> # Get event (requires filter parameter)
        >>> events = await upsales.events.list(q="entityType:manual")
        >>> event = events[0]
        >>> event.entityType
        'manual'
        >>>
        >>> # Use computed fields
        >>> event.is_manual
        True
        >>> event.has_company
        True
        >>>
        >>> # Note: Events do not support edit() in API
        >>> # Can only create and delete
    """

    # Read-only fields (frozen=True, strict=True)
    id: int = Field(frozen=True, strict=True, description="Unique event ID")

    # Required fields with validators
    entityType: NonEmptyStr = Field(
        description="Event type (e.g., 'manual', 'marketingCustom', 'news')"
    )
    score: int = Field(default=0, description="Event score (0 for reject-listed clients)")

    # Optional core fields
    subType: str | None = Field(None, description="Event subtype")
    entityId: int | None = Field(None, description="Related entity ID")
    date: str | None = Field(None, description="Event date (ISO 8601 format)")
    value: str | None = Field(None, description="Event value (max 512 chars)")

    # Related entities
    client: PartialCompany | None = Field(None, description="Linked company/client")
    contacts: list[PartialContact] = Field(default=[], description="Linked contacts")
    users: list[PartialUser] = Field(default=[], description="Related users")

    # Optional nested objects
    form: dict[str, Any] | None = Field(None, description="Linked form data")
    marketingCustom: dict[str, Any] | None = Field(None, description="Marketing custom data")
    opportunity: PartialOrder | None = Field(None, description="Linked opportunity/order")
    activity: dict[str, Any] | None = Field(None, description="Linked activity data")
    appointment: dict[str, Any] | None = Field(None, description="Linked appointment data")
    agreement: dict[str, Any] | None = Field(None, description="Linked agreement data")
    mail: dict[str, Any] | None = Field(None, description="Linked mail data")
    mails: list[dict[str, Any]] = Field(default=[], description="Multiple linked mails")
    order: PartialOrder | None = Field(None, description="Linked order")
    visit: dict[str, Any] | None = Field(None, description="Linked visit data")
    esign: dict[str, Any] | None = Field(None, description="Linked e-signature data")
    news: dict[str, Any] | None = Field(None, description="Linked news data")
    socialEvent: dict[str, Any] | None = Field(None, description="Social event data")
    comment: dict[str, Any] | None = Field(None, description="Comment data")
    plan: dict[str, Any] | None = Field(None, description="Linked plan data")
    ticket: dict[str, Any] | None = Field(None, description="Linked ticket data")

    @computed_field
    @property
    def is_manual(self) -> bool:
        """
        Check if event is a manual entry.

        Returns:
            True if entityType is 'manual', False otherwise.

        Example:
            >>> event.is_manual
            True
            >>> event.entityType
            'manual'
        """
        return self.entityType == "manual"

    @computed_field
    @property
    def is_marketing(self) -> bool:
        """
        Check if event is a marketing custom event.

        Returns:
            True if entityType is 'marketingCustom', False otherwise.

        Example:
            >>> event.is_marketing
            True
            >>> event.entityType
            'marketingCustom'
        """
        return self.entityType == "marketingCustom"

    @computed_field
    @property
    def is_news(self) -> bool:
        """
        Check if event is a news update.

        Returns:
            True if entityType is 'news', False otherwise.

        Example:
            >>> event.is_news
            True
            >>> event.entityType
            'news'
        """
        return self.entityType == "news"

    @computed_field
    @property
    def has_company(self) -> bool:
        """
        Check if event is linked to a company.

        Returns:
            True if client field contains data, False otherwise.

        Example:
            >>> event.has_company
            True
            >>> event.client.name
            'ACME Corp'
        """
        return bool(self.client and self.client.id)

    @computed_field
    @property
    def has_opportunity(self) -> bool:
        """
        Check if event is linked to an opportunity.

        Returns:
            True if opportunity field contains data, False otherwise.

        Example:
            >>> event.has_opportunity
            True
            >>> event.opportunity.id
            5
        """
        return bool(self.opportunity and self.opportunity.id)

    @computed_field
    @property
    def has_contacts(self) -> bool:
        """
        Check if event has linked contacts.

        Returns:
            True if contacts list is not empty, False otherwise.

        Example:
            >>> event.has_contacts
            True
            >>> len(event.contacts)
            2
        """
        return len(self.contacts) > 0

    async def edit(self, **kwargs: Unpack[EventUpdateFields]) -> "Event":
        """
        Edit this event.

        Note: The Upsales API does not support PUT/PATCH operations for events.
        Events can only be created (POST) and deleted (DELETE).
        This method is provided for consistency with other models but will
        raise NotImplementedError.

        Args:
            **kwargs: Fields to update (not supported).

        Returns:
            Updated Event object (not supported).

        Raises:
            NotImplementedError: Events cannot be edited via API.

        Example:
            >>> event = await upsales.events.get(1)
            >>> await event.edit(value="new value")  # Raises NotImplementedError
            NotImplementedError: Events cannot be edited. API only supports CREATE and DELETE.
        """
        raise NotImplementedError(
            "Events cannot be edited. API only supports CREATE and DELETE operations."
        )


class PartialEvent(PartialModel):
    """
    Partial Event for nested responses.

    Contains minimal fields for when Event appears nested in other
    API responses (e.g., as recent event, related event, etc.).

    Use fetch_full() to get complete Event object with all fields.

    Example:
        >>> company = await upsales.companies.get(1)
        >>> recent = company.recent_event  # PartialEvent
        >>> full = await recent.fetch_full()  # Now Event
        >>> full.entityType
        'marketingCustom'
    """

    # Minimum fields for identification
    id: int = Field(frozen=True, strict=True, description="Unique event ID")
    entityType: NonEmptyStr = Field(
        description="Event type (e.g., 'manual', 'marketingCustom', 'news')"
    )
    date: str | None = Field(None, description="Event date (ISO 8601)")

    @computed_field
    @property
    def is_manual(self) -> bool:
        """
        Check if event is a manual entry.

        Returns:
            True if entityType is 'manual', False otherwise.

        Example:
            >>> partial.is_manual
            True
        """
        return self.entityType == "manual"

    async def fetch_full(self) -> Event:
        """
        Fetch complete event data from API.

        Note: Fetching events requires proper filter parameters.

        Returns:
            Full Event object with all fields populated.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> partial = company.recent_event  # PartialEvent
            >>> full = await partial.fetch_full()  # Event
            >>> full.value
            'Event details here'
        """
        if not self._client:
            raise RuntimeError("No client available")
        # Events list requires filter parameter, so we fetch all and find by ID
        events = await self._client.events.list(limit=1000)
        for event in events:
            if event.id == self.id:
                return event
        raise ValueError(f"Event with ID {self.id} not found")

    async def edit(self, **kwargs: Unpack[EventUpdateFields]) -> Event:
        """
        Edit event via partial reference.

        Note: The Upsales API does not support PUT/PATCH operations for events.
        This method will raise NotImplementedError.

        Args:
            **kwargs: Fields to update (not supported).

        Returns:
            Updated full Event object from API (not supported).

        Raises:
            NotImplementedError: Events cannot be edited via API.

        Example:
            >>> partial = company.recent_event  # PartialEvent
            >>> await partial.edit(value="new")  # Raises NotImplementedError
            NotImplementedError: Events cannot be edited.
        """
        raise NotImplementedError(
            "Events cannot be edited. API only supports CREATE and DELETE operations."
        )
