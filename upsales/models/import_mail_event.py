"""Models for mail event import endpoint.

This module provides models for importing mail events (open, click, bounce, delivered)
into the Upsales CRM system.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

MailEventType = Literal["open", "click", "bounce", "delivered"]


class MailEvent(BaseModel):
    """Represents a single mail event to be imported.

    Mail events track recipient interactions with email campaigns, such as opens,
    clicks, bounces, and deliveries.

    Attributes:
        contactId: ID of the contact who triggered the event.
        mailCampaignId: ID of the mail campaign associated with the event.
        event: Type of event (open, click, bounce, delivered).
        timestamp: Unix timestamp (milliseconds) when the event occurred.
        url: URL that was clicked (required for 'click' events).
        useragent: User agent string of the recipient's browser/client.
        ip: IP address of the recipient.

    Example:
        ```python
        event = MailEvent(
            contactId=12345,
            mailCampaignId=67890,
            event="click",
            timestamp=1699920000000,
            url="https://example.com/link"
        )
        ```
    """

    contactId: int = Field(description="Contact ID")
    mailCampaignId: int = Field(description="Mail campaign ID")
    event: MailEventType = Field(description="Event type")
    timestamp: int = Field(description="Unix timestamp in milliseconds")
    url: str | None = Field(None, description="Clicked URL (required for click events)")
    useragent: str | None = Field(None, description="User agent string")
    ip: str | None = Field(None, description="IP address")

    @model_validator(mode="after")
    def validate_click_url(self) -> MailEvent:
        """Ensure click events have a URL."""
        if self.event == "click" and not self.url:
            raise ValueError("URL is required for 'click' events")
        return self


class SkippedEvent(BaseModel):
    """Represents an event that failed to import.

    Attributes:
        event: The original event data that failed.
        error: Error message explaining why the event was skipped.

    Example:
        ```python
        skipped = SkippedEvent(
            event={"contactId": 123, "mailCampaignId": 456, "event": "open"},
            error="Contact not found"
        )
        ```
    """

    event: dict[str, Any] = Field(description="Original event data")
    error: str = Field(description="Error message")


class ImportMailEventResponse(BaseModel):
    """Response from the import mail event API.

    Attributes:
        skippedEvents: List of events that failed to import with error messages.

    Example:
        ```python
        response = ImportMailEventResponse(skippedEvents=[])
        if not response.skippedEvents:
            print("All events imported successfully")
        ```
    """

    skippedEvents: list[SkippedEvent] = Field(
        default=[], description="Events that failed to import"
    )

    @property
    def all_succeeded(self) -> bool:
        """Check if all events were imported successfully.

        Returns:
            True if no events were skipped, False otherwise.

        Example:
            ```python
            response = await upsales.import_mail_event.import_events(events)
            if response.all_succeeded:
                print("Success!")
            ```
        """
        return len(self.skippedEvents) == 0

    @property
    def failed_count(self) -> int:
        """Get the number of failed events.

        Returns:
            Number of events that failed to import.

        Example:
            ```python
            response = await upsales.import_mail_event.import_events(events)
            print(f"Failed: {response.failed_count}")
            ```
        """
        return len(self.skippedEvents)
