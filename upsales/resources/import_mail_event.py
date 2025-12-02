"""Resource manager for importing mail events.

This module provides the ImportMailEventResource class for importing mail events
(opens, clicks, bounces, deliveries) into the Upsales CRM system.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from upsales.models.import_mail_event import (
    ImportMailEventResponse,
    MailEvent,
)

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class ImportMailEventResource:
    """Manager for mail event import operations.

    This resource handles importing mail events for tracking recipient interactions
    with email campaigns. Events are imported in bulk and automatically linked to
    the appropriate mail records based on contactId and mailCampaignId.

    Attributes:
        http: HTTP client for API communication.
        endpoint: API endpoint path.

    Example:
        ```python
        async with Upsales.from_env() as upsales:
            # Create events to import
            events = [
                MailEvent(
                    contactId=12345,
                    mailCampaignId=67890,
                    event="open",
                    timestamp=1699920000000
                ),
                MailEvent(
                    contactId=12346,
                    mailCampaignId=67890,
                    event="click",
                    timestamp=1699920100000,
                    url="https://example.com/link"
                )
            ]

            # Import events
            response = await upsales.import_mail_event.import_events(events)

            # Check results
            if response.all_succeeded:
                print("All events imported successfully")
            else:
                print(f"Failed: {response.failed_count}")
                for skipped in response.skippedEvents:
                    print(f"Error: {skipped.error}")
        ```
    """

    def __init__(self, http: HTTPClient):
        """Initialize the import mail event resource.

        Args:
            http: HTTP client for making API requests.
        """
        self.http = http
        self.endpoint = "/import/mailevent"

    async def import_events(
        self,
        events: list[MailEvent] | list[dict[str, Any]],
    ) -> ImportMailEventResponse:
        """Import mail events into the system.

        This method imports multiple mail events in a single API call. Events are
        automatically linked to mail records based on contactId and mailCampaignId.
        Invalid events are returned in the response's skippedEvents list.

        Args:
            events: List of MailEvent objects or dictionaries containing event data.
                   Each event must have contactId, mailCampaignId, event type, and
                   timestamp. Click events must also include a URL.

        Returns:
            ImportMailEventResponse with skippedEvents list (empty if all succeeded).

        Raises:
            ValidationError: If event data is invalid (400).
            AuthenticationError: If authentication fails (401/403).
            ServerError: If server error occurs (500+).

        Example:
            ```python
            # Using MailEvent objects
            events = [
                MailEvent(
                    contactId=123,
                    mailCampaignId=456,
                    event="open",
                    timestamp=1699920000000
                )
            ]
            response = await upsales.import_mail_event.import_events(events)

            # Using dictionaries
            events = [
                {
                    "contactId": 123,
                    "mailCampaignId": 456,
                    "event": "click",
                    "timestamp": 1699920000000,
                    "url": "https://example.com"
                }
            ]
            response = await upsales.import_mail_event.import_events(events)

            # Check for failures
            if not response.all_succeeded:
                for skipped in response.skippedEvents:
                    print(f"Failed: {skipped.event}")
                    print(f"Error: {skipped.error}")
            ```

        Note:
            - The API automatically looks up the mailId from contactId and mailCampaignId
            - Invalid events are not rejected entirely but returned in skippedEvents
            - Click events must include a URL or they will be skipped
            - Timestamps should be Unix time in milliseconds
        """
        # Convert MailEvent objects to dicts if needed
        event_dicts = []
        for event in events:
            if isinstance(event, MailEvent):
                event_dicts.append(event.model_dump(mode="json", exclude_none=True))
            else:
                event_dicts.append(event)

        # API expects {"array": [...]}
        payload = {"array": event_dicts}

        # Make request
        response = await self.http.post(self.endpoint, json=payload)

        # Parse response
        return ImportMailEventResponse.model_validate(response)
