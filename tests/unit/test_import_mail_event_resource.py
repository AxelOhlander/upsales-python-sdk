"""Unit tests for import mail event resource."""

from unittest.mock import AsyncMock

import pytest

from upsales.models.import_mail_event import (
    ImportMailEventResponse,
    MailEvent,
    SkippedEvent,
)
from upsales.resources.import_mail_event import ImportMailEventResource


@pytest.fixture
def resource():
    """Create import mail event resource with mocked HTTP client."""
    http = AsyncMock()
    return ImportMailEventResource(http), http


@pytest.mark.asyncio
async def test_import_events_with_mail_event_objects(resource):
    """Test importing events using MailEvent objects."""
    resource, http = resource

    # Mock API response
    http.post.return_value = {"skippedEvents": []}

    # Create events
    events = [
        MailEvent(
            contactId=12345,
            mailCampaignId=67890,
            event="open",
            timestamp=1699920000000,
        ),
        MailEvent(
            contactId=12346,
            mailCampaignId=67890,
            event="click",
            timestamp=1699920100000,
            url="https://example.com/link",
        ),
    ]

    # Import events
    response = await resource.import_events(events)

    # Verify request
    http.post.assert_called_once_with(
        "/import/mailevent",
        json={
            "array": [
                {
                    "contactId": 12345,
                    "mailCampaignId": 67890,
                    "event": "open",
                    "timestamp": 1699920000000,
                },
                {
                    "contactId": 12346,
                    "mailCampaignId": 67890,
                    "event": "click",
                    "timestamp": 1699920100000,
                    "url": "https://example.com/link",
                },
            ]
        },
    )

    # Verify response
    assert isinstance(response, ImportMailEventResponse)
    assert response.all_succeeded is True
    assert response.failed_count == 0


@pytest.mark.asyncio
async def test_import_events_with_dictionaries(resource):
    """Test importing events using dictionaries."""
    resource, http = resource

    # Mock API response
    http.post.return_value = {"skippedEvents": []}

    # Create events as dicts
    events = [
        {
            "contactId": 123,
            "mailCampaignId": 456,
            "event": "delivered",
            "timestamp": 1699920000000,
        }
    ]

    # Import events
    response = await resource.import_events(events)

    # Verify request
    http.post.assert_called_once_with(
        "/import/mailevent",
        json={"array": events},
    )

    # Verify response
    assert response.all_succeeded is True


@pytest.mark.asyncio
async def test_import_events_with_skipped_events(resource):
    """Test importing events with some failures."""
    resource, http = resource

    # Mock API response with skipped events
    http.post.return_value = {
        "skippedEvents": [
            {
                "event": {"contactId": 999, "mailCampaignId": 456, "event": "open"},
                "error": "Contact not found",
            }
        ]
    }

    # Create events
    events = [
        MailEvent(
            contactId=123,
            mailCampaignId=456,
            event="open",
            timestamp=1699920000000,
        ),
        MailEvent(
            contactId=999,
            mailCampaignId=456,
            event="open",
            timestamp=1699920100000,
        ),
    ]

    # Import events
    response = await resource.import_events(events)

    # Verify response
    assert response.all_succeeded is False
    assert response.failed_count == 1
    assert len(response.skippedEvents) == 1
    assert response.skippedEvents[0].error == "Contact not found"


@pytest.mark.asyncio
async def test_import_events_with_optional_fields(resource):
    """Test importing events with optional fields."""
    resource, http = resource

    # Mock API response
    http.post.return_value = {"skippedEvents": []}

    # Create event with optional fields
    events = [
        MailEvent(
            contactId=123,
            mailCampaignId=456,
            event="click",
            timestamp=1699920000000,
            url="https://example.com",
            useragent="Mozilla/5.0",
            ip="192.168.1.1",
        )
    ]

    # Import events
    await resource.import_events(events)

    # Verify optional fields are included
    http.post.assert_called_once()
    call_args = http.post.call_args
    assert call_args[1]["json"]["array"][0]["useragent"] == "Mozilla/5.0"
    assert call_args[1]["json"]["array"][0]["ip"] == "192.168.1.1"


@pytest.mark.asyncio
async def test_mail_event_validation_click_requires_url():
    """Test that click events require a URL."""
    with pytest.raises(ValueError, match="URL is required for 'click' events"):
        MailEvent(
            contactId=123,
            mailCampaignId=456,
            event="click",
            timestamp=1699920000000,
            # Missing URL!
        )


@pytest.mark.asyncio
async def test_mail_event_validation_click_with_url():
    """Test that click events work with URL."""
    event = MailEvent(
        contactId=123,
        mailCampaignId=456,
        event="click",
        timestamp=1699920000000,
        url="https://example.com",
    )
    assert event.url == "https://example.com"


@pytest.mark.asyncio
async def test_mail_event_other_events_dont_require_url():
    """Test that non-click events don't require URL."""
    for event_type in ["open", "bounce", "delivered"]:
        event = MailEvent(
            contactId=123,
            mailCampaignId=456,
            event=event_type,
            timestamp=1699920000000,
        )
        assert event.url is None


def test_import_mail_event_response_properties():
    """Test ImportMailEventResponse computed properties."""
    # Test all succeeded
    response = ImportMailEventResponse(skippedEvents=[])
    assert response.all_succeeded is True
    assert response.failed_count == 0

    # Test with failures
    response = ImportMailEventResponse(
        skippedEvents=[
            SkippedEvent(event={"contactId": 123}, error="Error 1"),
            SkippedEvent(event={"contactId": 456}, error="Error 2"),
        ]
    )
    assert response.all_succeeded is False
    assert response.failed_count == 2


def test_skipped_event_model():
    """Test SkippedEvent model."""
    skipped = SkippedEvent(
        event={"contactId": 123, "mailCampaignId": 456, "event": "open"},
        error="Contact not found",
    )
    assert skipped.event["contactId"] == 123
    assert skipped.error == "Contact not found"
