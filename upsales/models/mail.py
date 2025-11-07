"""
Mail models for Upsales API.

Generated from /api/v2/mail endpoint.
Analysis based on 12 samples.

Enhanced with Pydantic v2 features:
- Reusable validators (BinaryFlag)
- Computed fields (@computed_field)
- Strict type checking
- Field descriptions
- Optimized serialization

Mail objects represent email messages in Upsales, including sent emails,
received emails, and email templates.
"""

from typing import Any, TypedDict, Unpack

from pydantic import Field, computed_field

from upsales.models.activities import PartialActivity
from upsales.models.appointments import PartialAppointment
from upsales.models.base import BaseModel, PartialModel
from upsales.models.company import PartialCompany
from upsales.models.contacts import PartialContact
from upsales.models.mail_templates import PartialMailTemplate
from upsales.models.projects import PartialProject
from upsales.models.user import PartialUser
from upsales.validators import BinaryFlag


class MailUpdateFields(TypedDict, total=False):
    """
    Available fields for updating a Mail.

    All fields are optional. Use with Unpack for IDE autocomplete.
    """

    subject: str
    body: str
    to: str
    from_: str  # Note: 'from' is Python keyword, use 'from_'
    fromName: str
    cc: list[str]
    bcc: list[str]
    attachments: list[Any]
    recipients: dict[str, Any]
    isMap: int
    users: list[PartialUser]
    jobId: int
    activity: dict[str, Any] | None
    mailBodySnapshotId: int
    contact: dict[str, Any] | None
    groupMailId: int
    threadId: str | None
    project: dict[str, Any] | None
    type: str
    appointment: dict[str, Any] | None
    opportunity: dict[str, Any] | None
    events: list[dict[str, Any]]
    internetMessageId: str | None
    mailThreadId: int
    userRemovable: bool
    thread: dict[str, Any]
    client: dict[str, Any] | None
    template: dict[str, Any] | None
    tags: list[dict[str, Any]]
    externalMailId: str | None
    userEditable: bool


class Mail(BaseModel):
    """
    Mail model from /api/v2/mail.

    Represents email messages in Upsales, including sent and received emails.
    Enhanced with Pydantic v2 validators, computed fields, and optimized serialization.

    Example:
        >>> # Get mail
        >>> mail = await upsales.mail.get(1)
        >>> mail.subject
        'Meeting follow-up'
        >>>
        >>> # Use computed fields
        >>> mail.is_map_email
        True
        >>> mail.has_attachments
        False
        >>>
        >>> # Edit mail (IDE autocomplete!)
        >>> await mail.edit(
        ...     subject="Updated subject",
        ...     body="Updated body"
        ... )
    """

    # Read-only fields (frozen=True, strict=True)
    id: int = Field(frozen=True, strict=True, description="Unique mail ID")
    date: str = Field(frozen=True, description="Mail date (ISO 8601)")
    modDate: str = Field(frozen=True, description="Last modification date (ISO 8601)")

    # Required email fields
    subject: str = Field(description="Email subject")
    body: str = Field(description="Email body content")
    to: str = Field(description="To recipients (comma-separated)")
    from_: str = Field(alias="from", description="From email address")
    fromName: str = Field(description="From display name")

    # Email type and status
    type: str = Field(description="Mail type (e.g., 'sent', 'received', 'draft')")
    isMap: BinaryFlag = Field(default=0, description="Is MAP email? (0=no, 1=yes)")

    # Recipients
    cc: list[str] = Field(default=[], description="CC recipients")
    bcc: list[str] = Field(default=[], description="BCC recipients")
    recipients: dict[str, Any] = Field(default_factory=dict, description="Recipients metadata")

    # Email content and attachments
    attachments: list[Any] = Field(default=[], description="Email attachments")
    mailBodySnapshotId: int = Field(description="Mail body snapshot ID")

    # Threading and grouping
    mailThreadId: int = Field(description="Mail thread ID")
    threadId: str | None = Field(None, description="External thread ID")
    groupMailId: int = Field(description="Group mail ID")
    thread: dict[str, Any] = Field(default_factory=dict, description="Thread metadata")

    # External IDs
    externalMailId: str | None = Field(None, description="External mail system ID")
    internetMessageId: str | None = Field(None, description="Internet message ID (RFC 5322)")

    # Related entities
    client: PartialCompany | None = Field(None, description="Linked company/client")
    contact: PartialContact | None = Field(None, description="Linked contact")
    activity: PartialActivity | None = Field(None, description="Linked activity")
    opportunity: dict[str, Any] | None = Field(None, description="Linked opportunity")
    project: PartialProject | None = Field(None, description="Linked project")
    appointment: PartialAppointment | None = Field(None, description="Linked appointment")
    template: PartialMailTemplate | None = Field(None, description="Email template used")

    # Users and permissions
    users: list[PartialUser] = Field(default=[], description="Assigned users")
    userEditable: bool = Field(default=True, description="Can user edit this mail?")
    userRemovable: bool = Field(default=True, description="Can user remove this mail?")

    # Events and tracking
    events: list[dict[str, Any]] = Field(default=[], description="Email events (opens, clicks)")
    lastReadDate: str | None = Field(None, description="Last read date (ISO 8601)")
    lastClickDate: str | None = Field(None, description="Last click date (ISO 8601)")
    lastEventDate: str | None = Field(None, description="Last event date (ISO 8601)")

    # Error handling
    errorCause: str | None = Field(None, description="Error cause if mail failed")
    jobId: int = Field(description="Email job ID")

    # Tags
    tags: list[dict[str, Any]] = Field(default=[], description="Mail tags")

    @computed_field
    @property
    def is_map_email(self) -> bool:
        """
        Check if this is a MAP (Marketing Automation Platform) email.

        Returns:
            True if isMap flag is 1, False otherwise.

        Example:
            >>> mail.is_map_email
            True
        """
        return self.isMap == 1

    @computed_field
    @property
    def has_attachments(self) -> bool:
        """
        Check if mail has attachments.

        Returns:
            True if attachments list is not empty.

        Example:
            >>> mail.has_attachments
            True
        """
        return len(self.attachments) > 0

    @computed_field
    @property
    def has_tracking_events(self) -> bool:
        """
        Check if mail has any tracking events (opens, clicks).

        Returns:
            True if events list is not empty.

        Example:
            >>> mail.has_tracking_events
            True
        """
        return len(self.events) > 0

    async def edit(self, **kwargs: Unpack[MailUpdateFields]) -> "Mail":
        """
        Edit this mail.

        Args:
            **kwargs: Fields to update. See MailUpdateFields for available options.

        Returns:
            Updated mail instance.

        Raises:
            RuntimeError: If no client is available.

        Example:
            >>> mail = await upsales.mail.get(1)
            >>> updated = await mail.edit(
            ...     subject="New subject",
            ...     body="Updated content"
            ... )
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.mail.update(self.id, **self.to_api_dict(**kwargs))


class PartialMail(PartialModel):
    """
    Partial Mail for nested responses.

    Used when mail appears as a nested object in other API responses.
    Contains minimal fields, but can fetch full Mail or edit directly.

    Example:
        >>> # From nested response
        >>> activity = await upsales.activities.get(1)
        >>> partial_mail = activity.mail  # PartialMail
        >>>
        >>> # Fetch full data
        >>> full_mail = await partial_mail.fetch_full()
        >>> full_mail.body
        'Full email body'
        >>>
        >>> # Or edit directly
        >>> await partial_mail.edit(subject="Updated")
    """

    id: int = Field(description="Unique mail ID")
    subject: str | None = Field(None, description="Email subject")
    type: str | None = Field(None, description="Mail type")

    async def fetch_full(self) -> Mail:
        """
        Fetch complete mail data.

        Returns:
            Full Mail instance with all fields populated.

        Raises:
            RuntimeError: If no client is available.

        Example:
            >>> partial = PartialMail(id=1)
            >>> full = await partial.fetch_full()
            >>> full.body
            'Full email body'
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.mail.get(self.id)

    async def edit(self, **kwargs: Unpack[MailUpdateFields]) -> Mail:
        """
        Edit this mail directly from partial.

        Args:
            **kwargs: Fields to update. See MailUpdateFields for available options.

        Returns:
            Full Mail instance with updates applied.

        Raises:
            RuntimeError: If no client is available.

        Example:
            >>> partial = PartialMail(id=1)
            >>> updated = await partial.edit(subject="New subject")
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.mail.update(self.id, **kwargs)
