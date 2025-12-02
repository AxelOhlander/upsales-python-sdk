"""
Ticket models for Upsales API.

This module provides models for working with support tickets in Upsales.
Tickets represent customer support requests and can be linked to companies,
contacts, opportunities, and other entities.

Example:
    >>> # Create a new ticket
    >>> ticket = await upsales.tickets.create(
    ...     title="Customer needs help",
    ...     statusId=1,
    ...     typeId=1,
    ...     clientId=123
    ... )
    >>>
    >>> # Update ticket status
    >>> await ticket.edit(statusId=2, isRead=True)
    >>>
    >>> # Mark as archived
    >>> await ticket.edit(isArchived=True)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypedDict, Unpack

from pydantic import Field, computed_field, field_serializer

from upsales.models.base import BaseModel, PartialModel
from upsales.models.custom_fields import CustomFields
from upsales.validators import CustomFieldsList

if TYPE_CHECKING:
    from upsales.models.company import PartialCompany
    from upsales.models.contacts import PartialContact
    from upsales.models.ticket_statuses import PartialTicketStatus
    from upsales.models.ticket_types import PartialTicketType
    from upsales.models.user import PartialUser


class TicketUpdateFields(TypedDict, total=False):
    """
    Available fields for updating a Ticket.

    All fields are optional. Use this for type hints and IDE autocomplete
    when calling ticket.edit().

    Read-only Fields (cannot be updated):
        id, contact, contactId, lastUpdated, resolveDate, firstResolveDate,
        firstReplyDate, regDate, regBy, modDate, modBy
    """

    title: str
    userId: int
    statusId: int
    typeId: int
    clientId: int
    priority: int
    isArchived: bool
    isPending: bool
    isRead: bool
    snoozeDate: str
    activityId: int
    appointmentId: int
    opportunityId: int
    relatedTicketId: int
    agreementId: int
    projectPlanId: int
    mergedWithId: int
    source: str
    emailUsed: str
    involved: list[dict[str, Any]]
    externalContacts: list[Any]
    custom: list[dict[str, Any]]


class Ticket(BaseModel):
    """
    Support ticket model from /api/v2/tickets.

    Represents a customer support ticket that can be linked to companies,
    contacts, opportunities, and other entities. Tracks status, priority,
    assignments, and resolution dates.

    Attributes:
        id: Unique ticket ID (read-only)
        title: Ticket title
        userId: Assigned user ID
        statusId: Current status ID
        typeId: Ticket type ID
        clientId: Associated company ID
        contactId: Associated contact ID (read-only)
        priority: Priority level (0-3, default 0)
        isArchived: Whether ticket is archived
        isPending: Whether ticket is pending
        isRead: Whether ticket has been read
        isMultiMatch: Whether multiple matches found
        source: Ticket source (email, manual, etc.)
        emailUsed: Email address used
        snoozeDate: Snooze until datetime
        resolveDate: Date ticket was resolved (read-only)
        firstResolveDate: First resolution date (read-only)
        firstReplyDate: First reply date (read-only)
        lastUpdated: Last update timestamp (read-only)
        regDate: Registration date (read-only)
        modDate: Last modification date (read-only)
        regBy: User who created ticket (read-only)
        modBy: Last user who modified ticket (read-only)
        activityId: Linked activity ID
        appointmentId: Linked appointment ID
        opportunityId: Linked opportunity ID
        relatedTicketId: Related ticket ID
        agreementId: Linked agreement ID
        projectPlanId: Linked project plan ID
        mergedWithId: Ticket this was merged with
        client: Associated company (nested)
        contact: Associated contact (nested, read-only)
        user: Assigned user (nested)
        status: Ticket status (nested)
        type: Ticket type (nested)
        involved: List of involved parties
        externalContacts: External contacts list
        mergedTickets: Tickets merged into this one
        directlyMergedTicketIds: IDs of directly merged tickets
        multiMatchClientContacts: Multiple match contacts
        customStatusSort: Custom status sort order
        unreadComments: Count of unread comments
        custom: Custom fields

    Example:
        >>> # Get ticket and update
        >>> ticket = await upsales.tickets.get(1)
        >>> await ticket.edit(
        ...     statusId=2,
        ...     priority=3,
        ...     isRead=True
        ... )
        >>>
        >>> # Access custom fields
        >>> value = ticket.custom_fields[11]
        >>> ticket.custom_fields["FIELD_ALIAS"] = "new value"
        >>>
        >>> # Check if archived
        >>> if ticket.is_archived:
        ...     print("Ticket is archived")
    """

    # Read-only fields (frozen=True based on API spec)
    id: int = Field(frozen=True, strict=True, description="Unique ticket ID")
    contactId: int | None = Field(None, frozen=True, description="Associated contact ID")
    contact: PartialContact | None = Field(
        None, frozen=True, description="Associated contact (nested)"
    )
    lastUpdated: str | None = Field(None, frozen=True, description="Last update timestamp")
    resolveDate: str | None = Field(None, frozen=True, description="Date ticket was resolved")
    firstResolveDate: str | None = Field(None, frozen=True, description="First resolution date")
    firstReplyDate: str | None = Field(None, frozen=True, description="First reply date")
    regDate: str | None = Field(None, frozen=True, description="Registration date (ISO 8601)")
    regBy: PartialUser | None = Field(None, frozen=True, description="User who created ticket")
    modDate: str | None = Field(None, frozen=True, description="Last modification date (ISO 8601)")
    modBy: int | None = Field(None, frozen=True, description="Last user who modified ticket")

    # Updatable fields
    title: str = Field(description="Ticket title (max 150 chars)", max_length=150)
    userId: int | None = Field(None, description="Assigned user ID")
    statusId: int | None = Field(None, description="Current status ID")
    typeId: int | None = Field(None, description="Ticket type ID")
    clientId: int | None = Field(None, description="Associated company ID")
    priority: int = Field(default=0, ge=0, le=3, description="Priority level (0-3)")
    isArchived: bool = Field(default=False, description="Whether ticket is archived")
    isPending: bool = Field(default=False, description="Whether ticket is pending")
    isRead: bool = Field(default=False, description="Whether ticket has been read")
    isMultiMatch: bool = Field(default=False, description="Whether multiple matches found")
    source: str | None = Field(None, description="Ticket source (email, manual, etc.)")
    emailUsed: str = Field(default="", description="Email address used")
    snoozeDate: str | None = Field(None, description="Snooze until datetime")
    activityId: int | None = Field(None, description="Linked activity ID")
    appointmentId: int | None = Field(None, description="Linked appointment ID")
    opportunityId: int | None = Field(None, description="Linked opportunity ID")
    relatedTicketId: int | None = Field(None, description="Related ticket ID")
    agreementId: int | None = Field(None, description="Linked agreement ID")
    projectPlanId: int | None = Field(None, description="Linked project plan ID")
    mergedWithId: int | None = Field(None, description="Ticket this was merged with")

    # Nested objects
    client: PartialCompany | None = Field(None, description="Associated company (nested)")
    user: PartialUser | None = Field(None, description="Assigned user (nested)")
    status: PartialTicketStatus | None = Field(None, description="Ticket status (nested)")
    type: PartialTicketType | None = Field(None, description="Ticket type (nested)")

    # Arrays
    involved: list[dict[str, Any]] = Field(
        default_factory=list, description="List of involved parties"
    )
    externalContacts: list[Any] = Field(default_factory=list, description="External contacts list")
    mergedTickets: list[Any] = Field(
        default_factory=list, description="Tickets merged into this one"
    )
    directlyMergedTicketIds: list[int] = Field(
        default_factory=list, description="IDs of directly merged tickets"
    )
    multiMatchClientContacts: list[Any] = Field(
        default_factory=list, description="Multiple match contacts"
    )

    # Metadata
    customStatusSort: int = Field(default=0, description="Custom status sort order")
    unreadComments: int = Field(default=0, description="Count of unread comments")

    # Custom fields
    custom: CustomFieldsList = Field(
        default_factory=list, description="Custom fields for extensibility"
    )

    @computed_field
    @property
    def custom_fields(self) -> CustomFields:
        """
        Access custom fields with dict-like interface.

        Returns:
            CustomFields helper providing dictionary-style access by ID or alias.

        Example:
            >>> ticket.custom_fields[11] = "value"
            >>> value = ticket.custom_fields["FIELD_ALIAS"]
        """
        return CustomFields(self.custom)

    @computed_field
    @property
    def is_archived(self) -> bool:
        """Check if ticket is archived."""
        return self.isArchived

    @computed_field
    @property
    def is_pending(self) -> bool:
        """Check if ticket is pending."""
        return self.isPending

    @computed_field
    @property
    def is_read(self) -> bool:
        """Check if ticket has been read."""
        return self.isRead

    @field_serializer("custom", when_used="json")
    def serialize_custom_fields(self, custom: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Clean custom fields for API requests.

        Removes null values and empty fields before sending to API.

        Args:
            custom: Raw custom fields list.

        Returns:
            Cleaned custom fields ready for API.
        """
        return [
            {"fieldId": item["fieldId"], "value": item.get("value")}
            for item in custom
            if "value" in item and item.get("value") is not None
        ]

    async def edit(self, **kwargs: Unpack[TicketUpdateFields]) -> Ticket:
        """
        Edit this ticket with type-safe field updates.

        Updates only the specified fields. Uses Pydantic v2 optimized serialization
        (5-50x faster) and automatically excludes read-only fields.

        Args:
            **kwargs: Fields to update (see TicketUpdateFields for available fields).

        Returns:
            Updated ticket with new field values.

        Raises:
            RuntimeError: If no client available.
            ValidationError: If field validation fails.
            UpsalesError: If API request fails.

        Example:
            >>> ticket = await upsales.tickets.get(1)
            >>> updated = await ticket.edit(
            ...     title="Updated title",
            ...     statusId=2,
            ...     priority=3,
            ...     isRead=True
            ... )
        """
        if not self._client:
            raise RuntimeError("No client available for API request")
        return await self._client.tickets.update(self.id, **self.to_api_dict(**kwargs))


class PartialTicket(PartialModel):
    """
    Partial Ticket model for nested API responses.

    Used when ticket data appears nested in other objects, containing only
    essential identification fields.

    Attributes:
        id: Unique ticket ID
        title: Ticket title

    Example:
        >>> # From nested response
        >>> opportunity = await upsales.orders.get(1)
        >>> if opportunity.ticket:
        ...     full_ticket = await opportunity.ticket.fetch_full()
    """

    id: int = Field(description="Unique ticket ID")
    title: str = Field(description="Ticket title")

    async def fetch_full(self) -> Ticket:
        """
        Fetch complete ticket data from API.

        Returns:
            Full Ticket object with all fields populated.

        Raises:
            RuntimeError: If no client available.
            NotFoundError: If ticket doesn't exist.
            UpsalesError: If API request fails.

        Example:
            >>> partial = PartialTicket(id=1, title="Support Request")
            >>> full = await partial.fetch_full()
            >>> print(full.statusId)
        """
        if not self._client:
            raise RuntimeError("No client available for API request")
        return await self._client.tickets.get(self.id)

    async def edit(self, **kwargs: Unpack[TicketUpdateFields]) -> Ticket:
        """
        Edit this ticket directly from partial model.

        Args:
            **kwargs: Fields to update (see TicketUpdateFields).

        Returns:
            Updated full Ticket object.

        Raises:
            RuntimeError: If no client available.
            UpsalesError: If API request fails.

        Example:
            >>> partial = PartialTicket(id=1, title="Support")
            >>> updated = await partial.edit(statusId=2)
        """
        if not self._client:
            raise RuntimeError("No client available for API request")
        return await self._client.tickets.update(self.id, **kwargs)
