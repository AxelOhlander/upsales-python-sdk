"""
Mail models for Upsales API.

Represents email messages in the Upsales system. Emails can be tracked, logged, and associated
with companies, contacts, and other entities.
"""

from typing import Any, TypedDict, Unpack

from pydantic import Field, computed_field

from upsales.models.base import BaseModel, PartialModel
from upsales.models.company import PartialCompany
from upsales.models.contacts import PartialContact
from upsales.models.projects import PartialProject
from upsales.models.user import PartialUser
from upsales.validators import BinaryFlag


class MailUpdateFields(TypedDict, total=False):
    """
    Available fields for updating a Mail.

    Based on API specification PUT /api/v2/mail/:id allowed fields.
    All fields are optional.
    """

    date: str
    subject: str
    body: str
    to: str
    from_address: str
    fromName: str
    type: str


class Mail(BaseModel):
    """
    Mail model representing email messages in Upsales.

    Emails can be sent, received, and associated with companies, contacts, projects,
    and other entities in the CRM.

    Examples:
        Create a new email record:
        ```python
        mail = await upsales.mail.create(
            date="2025-01-01",
            type="out",
            clientId=123,
            contactId=456,
            subject="Meeting Follow-up",
            body="<p>Thanks for the meeting...</p>",
            to="customer@example.com",
            from_address="sales@company.com"
        )
        ```

        Update email:
        ```python
        await mail.edit(subject="Updated Subject", body="<p>New content</p>")
        ```
    """

    # Read-only fields (frozen) - from API spec
    id: int = Field(frozen=True, strict=True, description="Unique email ID")
    modDate: str = Field(default="", frozen=True, description="Last modification date")
    userRemovable: bool = Field(default=True, frozen=True, description="Whether user can remove")
    userEditable: bool = Field(default=True, frozen=True, description="Whether user can edit")

    # Core fields (defaults for sparse responses)
    date: str = Field(default="", frozen=True, description="Email date (YYYY-MM-DD format)")
    type: str = Field(
        default="",
        description="Email type: 'out' (sent), 'in' (received), 'pro' (processed), 'err' (error)",
    )
    subject: str = Field(default="", description="Email subject line")
    body: str = Field(default="", description="Email body content (HTML)")
    to: str = Field(default="", description="Recipient email address(es)")
    from_address: str = Field(default="", alias="from", description="Sender email address")
    fromName: str = Field(default="", description="Sender display name")

    # System IDs (defaults for sparse responses)
    groupMailId: int = Field(default=0, description="Group mail campaign ID")
    jobId: int = Field(default=0, description="Job ID for processing")
    mailBodySnapshotId: int = Field(default=0, description="Snapshot ID for body content")
    mailThreadId: int = Field(default=0, description="Thread ID for conversation grouping")
    isMap: BinaryFlag = Field(default=0, description="Whether email is mapped (0 or 1)")

    # Related entities
    company: PartialCompany | None = Field(None, alias="client", description="Associated company")
    contact: PartialContact | None = Field(None, description="Associated contact")
    project: PartialProject | None = Field(None, description="Associated project")
    users: list[PartialUser] = Field(default_factory=list, description="Associated users")

    # Optional fields
    cc: list[str] = Field(default_factory=list, description="CC recipients")
    bcc: list[str] = Field(default_factory=list, description="BCC recipients")
    attachments: list[dict[str, Any]] = Field(default_factory=list, description="Email attachments")
    errorCause: str | None = Field(None, description="Error message if type is 'err'")
    threadId: str | None = Field(None, description="External thread identifier")
    internetMessageId: str | None = Field(None, description="RFC 2822 Message-ID")
    externalMailId: str | None = Field(None, description="External mail system ID")

    # Tracking fields
    lastEventDate: str | None = Field(None, description="Last email event date")
    lastReadDate: str | None = Field(None, description="Last time email was read")
    lastClickDate: str | None = Field(None, description="Last time link was clicked")

    # Related data
    events: list[dict[str, Any]] = Field(default_factory=list, description="Email tracking events")
    recipients: dict[str, Any] = Field(
        default_factory=dict, description="Detailed recipient information"
    )
    tags: list[dict[str, Any]] = Field(default_factory=list, description="Email tags")
    template: dict[str, Any] | None = Field(None, description="Email template used")
    thread: dict[str, Any] | None = Field(default_factory=dict, description="Thread information")

    # Related entities (optional)
    activity: dict[str, Any] | None = Field(None, description="Related activity")
    appointment: dict[str, Any] | None = Field(None, description="Related appointment")
    opportunity: dict[str, Any] | None = Field(None, description="Related opportunity")

    @computed_field
    @property
    def is_outgoing(self) -> bool:
        """Check if email is outgoing."""
        return self.type == "out"

    @computed_field
    @property
    def is_incoming(self) -> bool:
        """Check if email is incoming."""
        return self.type == "in"

    @computed_field
    @property
    def has_error(self) -> bool:
        """Check if email has an error."""
        return self.type == "err"

    @computed_field
    @property
    def from_(self) -> str:
        """Alias for from_address field (Python-safe property name)."""
        return self.from_address

    @computed_field
    @property
    def is_map_email(self) -> bool:
        """Check if email is a MAP (Marketing Automation Platform) email."""
        return self.isMap == 1

    @computed_field
    @property
    def has_attachments(self) -> bool:
        """Check if email has attachments."""
        return len(self.attachments) > 0

    @computed_field
    @property
    def has_tracking_events(self) -> bool:
        """Check if email has tracking events."""
        return len(self.events) > 0

    async def edit(self, **kwargs: Unpack[MailUpdateFields]) -> "Mail":
        """
        Edit this email.

        Args:
            **kwargs: Fields to update (date, subject, body, to, from_address, fromName, type).

        Returns:
            Updated mail object.

        Raises:
            RuntimeError: If no client is available.

        Examples:
            ```python
            mail = await upsales.mail.get(123)
            updated = await mail.edit(
                subject="Updated Subject",
                body="<p>Updated content</p>"
            )
            ```
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.mail.update(self.id, **self.to_api_dict(**kwargs))


class PartialMail(PartialModel):
    """
    Partial Mail for nested responses.

    Used when email data appears as a nested object in other API responses.

    Examples:
        Fetch full email data:
        ```python
        partial_mail = activity.mail  # From activity response
        full_mail = await partial_mail.fetch_full()
        ```
    """

    id: int = Field(description="Unique email ID")
    subject: str | None = Field(None, description="Email subject line")
    type: str | None = Field(None, description="Email type")
    date: str | None = Field(None, description="Email date")

    async def fetch_full(self) -> Mail:
        """
        Fetch full email data from the API.

        Returns:
            Complete Mail object with all fields.

        Raises:
            RuntimeError: If no client is available.

        Examples:
            ```python
            partial_mail = activity.mail
            full_mail = await partial_mail.fetch_full()
            print(full_mail.body)  # Access full email body
            ```
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.mail.get(self.id)

    async def edit(self, **kwargs: Unpack[MailUpdateFields]) -> Mail:
        """
        Edit this email without fetching full data first.

        Args:
            **kwargs: Fields to update.

        Returns:
            Updated Mail object.

        Raises:
            RuntimeError: If no client is available.

        Examples:
            ```python
            partial_mail = activity.mail
            updated = await partial_mail.edit(subject="New Subject")
            ```
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.mail.update(self.id, **kwargs)
