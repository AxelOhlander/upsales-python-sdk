"""
Mail campaign models for Upsales API.

This module provides models for email campaigns in the Upsales CRM system.
"""

from typing import TYPE_CHECKING, Any, TypedDict, Unpack

from pydantic import Field, computed_field

from upsales.models.base import BaseModel, PartialModel
from upsales.validators import BinaryFlag

if TYPE_CHECKING:
    from upsales.models.projects import PartialProject
    from upsales.models.user import PartialUser


class MailCampaignUpdateFields(TypedDict, total=False):
    """
    Available fields for updating a MailCampaign.

    All fields are optional. Only include fields you want to update.
    """

    name: str
    subject: str
    body: str
    fromName: str
    sendDate: str
    projectId: int
    filter: str
    segmentId: int
    segments: list[Any]
    isArchived: int


class MailCampaign(BaseModel):
    """
    Email campaign model from /api/v2/mailCampaigns endpoint.

    Represents an email marketing campaign with recipients, content,
    and tracking statistics.

    Example:
        ```python
        # Get a campaign
        campaign = await upsales.mail_campaigns.get(123)

        # Update campaign
        await campaign.edit(
            subject="Updated Subject",
            isArchived=0
        )

        # Check statistics
        print(f"Sent: {campaign.mailSent}")
        print(f"Read: {campaign.mailRead}")
        print(f"Clicked: {campaign.mailClicked}")
        print(f"Is archived: {campaign.is_archived}")
        ```
    """

    # Read-only fields
    id: int = Field(frozen=True, strict=True, description="Unique campaign ID")
    status: str = Field(
        frozen=True, description="Campaign status (DRAFT, SCHEDULED, PROCESSING, SENT)"
    )
    mailSent: int = Field(frozen=True, description="Number of emails sent")
    mailRead: int = Field(frozen=True, description="Number of emails read")
    mailClicked: int = Field(frozen=True, description="Number of clicks")
    mailError: int = Field(frozen=True, description="Number of errors")
    mailPending: int = Field(frozen=True, description="Number of pending emails")
    mailUnsub: int = Field(frozen=True, description="Number of unsubscribes")
    modDate: str | None = Field(None, frozen=True, description="Last modification date")
    version: int = Field(frozen=True, description="Campaign version")
    jobId: int = Field(frozen=True, description="Job ID")

    # Required fields
    name: str = Field(description="Campaign name")
    subject: str = Field(description="Email subject line")
    body: str = Field(description="Email body HTML content")
    bodyJson: str = Field(description="Email body JSON representation")
    fromName: str = Field(description="Sender display name")

    # Email address field
    from_email: str = Field(alias="from", description="Sender email address")

    # Optional updatable fields
    sendDate: str | None = Field(None, description="Scheduled send date (YYYY-MM-DD HH:MM:SS)")
    filter: str | None = Field(None, description="Recipient filter JSON")
    filterConfig: str | None = Field(None, description="Filter configuration")
    isArchived: BinaryFlag = Field(default=0, description="Archive status (0=active, 1=archived)")

    # Nested objects
    project: "PartialProject | None" = Field(None, description="Associated project")
    user: "PartialUser" = Field(description="Campaign creator/owner")
    template: dict[str, Any] | None = Field(None, description="Email template")
    category: dict[str, Any] | None = Field(None, description="Campaign category")

    # Arrays
    attachments: list[Any] = Field(default_factory=list, description="Email attachments")
    labels: list[Any] = Field(default_factory=list, description="Campaign labels")
    segments: list[Any] = Field(default_factory=list, description="Recipient segments")

    # Other optional fields
    segment: Any | None = Field(None, description="Primary segment")
    socialEventId: int | None = Field(None, description="Social event ID")
    socialEventSendToStatus: str | None = Field(None, description="Social event send status")
    flowId: Any | None = Field(None, description="Flow ID")
    externalId: Any | None = Field(None, description="External ID")

    @computed_field
    @property
    def is_archived(self) -> bool:
        """Check if campaign is archived."""
        return self.isArchived == 1

    @computed_field
    @property
    def is_draft(self) -> bool:
        """Check if campaign is in draft status."""
        return self.status == "DRAFT"

    @computed_field
    @property
    def is_sent(self) -> bool:
        """Check if campaign has been sent."""
        return self.status == "SENT"

    @computed_field
    @property
    def open_rate(self) -> float:
        """Calculate email open rate percentage."""
        if self.mailSent == 0:
            return 0.0
        return (self.mailRead / self.mailSent) * 100

    @computed_field
    @property
    def click_rate(self) -> float:
        """Calculate email click rate percentage."""
        if self.mailSent == 0:
            return 0.0
        return (self.mailClicked / self.mailSent) * 100

    async def edit(self, **kwargs: Unpack[MailCampaignUpdateFields]) -> "MailCampaign":
        """
        Edit this mail campaign.

        Note:
            Cannot update campaigns with status PROCESSING or SENT.

        Args:
            **kwargs: Fields to update. See MailCampaignUpdateFields for available options.

        Returns:
            Updated MailCampaign instance.

        Raises:
            RuntimeError: If no client is available.
            ValidationError: If trying to update a sent or processing campaign.

        Example:
            ```python
            campaign = await upsales.mail_campaigns.get(123)
            updated = await campaign.edit(
                name="Updated Campaign Name",
                subject="New Subject"
            )
            ```
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.mail_campaigns.update(self.id, **self.to_api_dict(**kwargs))


class PartialMailCampaign(PartialModel):
    """
    Partial MailCampaign for nested responses.

    Used when mail campaigns appear as nested objects in other API responses.

    Example:
        ```python
        # From a nested response
        partial_campaign = contact.mailCampaign

        # Fetch full details
        full_campaign = await partial_campaign.fetch_full()
        ```
    """

    id: int = Field(description="Campaign ID")
    name: str = Field(description="Campaign name")

    async def fetch_full(self) -> MailCampaign:
        """
        Fetch complete mail campaign data.

        Returns:
            Full MailCampaign instance with all fields.

        Raises:
            RuntimeError: If no client is available.
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.mail_campaigns.get(self.id)

    async def edit(self, **kwargs: Unpack[MailCampaignUpdateFields]) -> MailCampaign:
        """
        Edit this mail campaign.

        Args:
            **kwargs: Fields to update.

        Returns:
            Updated MailCampaign instance.

        Raises:
            RuntimeError: If no client is available.
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.mail_campaigns.update(self.id, **kwargs)
