"""
Integration tests for Event model with real API responses.

Uses VCR.py to record API responses on first run, then replay them.
Validates that our Pydantic v2 models correctly parse real API data.

Note: The events endpoint has very limited functionality:
- CREATE (POST) - Works
- DELETE - Works
- LIST - Does NOT work (returns 500 without proper filters)
- UPDATE - Not supported by API
- Filter syntax (q parameter) - Not working in test environment

These tests focus on CREATE and DELETE operations which are confirmed to work.

To record cassettes:
    uv run pytest tests/integration/test_events_integration.py -v

To re-record (delete cassette first):
    rm -r tests/cassettes/integration/test_events_integration/
    uv run pytest tests/integration/test_events_integration.py -v
"""

import pytest
import vcr

from upsales import Upsales
from upsales.models.events import Event

# Configure VCR for these tests
my_vcr = vcr.VCR(
    cassette_library_dir="tests/cassettes/integration",
    record_mode="once",  # Record once, then always replay
    match_on=["method", "scheme", "host", "port", "path"],
    filter_headers=[
        ("cookie", "REDACTED"),
        ("authorization", "REDACTED"),
    ],
    filter_post_data_parameters=[
        ("password", "REDACTED"),
    ],
)


@pytest.mark.asyncio
@my_vcr.use_cassette("test_events_integration/test_create_event.yaml")
async def test_create_event():
    """
    Test creating an event with real API response.

    Validates Event model with real API response from create operation.
    Tests model validation, nested objects, and computed fields.

    Cassette: tests/cassettes/integration/test_events_integration/test_create_event.yaml
    """
    async with Upsales.from_env() as upsales:
        # Get a company for the event
        companies = await upsales.companies.list(limit=1)
        if not companies:
            pytest.skip("No companies found to create test event")

        company_id = companies[0].id

        # Create a test event with various fields
        event = await upsales.events.create(
            entityType="manual",
            score=10,
            client={"id": company_id},
            value="VCR integration test event",
            date="2025-12-02",
        )

        try:
            # Validate created event structure
            assert isinstance(event, Event)
            assert isinstance(event.id, int)
            assert event.id > 0
            assert event.entityType == "manual"
            assert event.score == 10
            assert event.value == "VCR integration test event"
            # API returns full ISO timestamp, not just date
            assert event.date is not None
            assert event.date.startswith("2025-12-02")

            # Validate nested company object
            assert event.client is not None
            assert event.client.id == company_id
            assert hasattr(event.client, "name")

            # Validate computed fields
            assert isinstance(event.is_manual, bool)
            assert event.is_manual is True
            assert isinstance(event.is_marketing, bool)
            assert event.is_marketing is False
            assert isinstance(event.is_news, bool)
            assert event.is_news is False
            assert isinstance(event.has_company, bool)
            assert event.has_company is True
            assert isinstance(event.has_opportunity, bool)
            assert isinstance(event.has_contacts, bool)

            # Validate optional list fields can be None
            assert event.contacts is None or isinstance(event.contacts, list)
            assert event.users is None or isinstance(event.users, list)
            assert event.mails is None or isinstance(event.mails, list)

            print(f"[OK] Created and validated event {event.id}")
            print(f"  Entity type: {event.entityType}")
            print(f"  Score: {event.score}")
            print(f"  Has company: {event.has_company}")
            print(f"  Computed fields work correctly")

        finally:
            # Clean up
            await upsales.events.delete(event.id)
            print(f"[OK] Deleted event {event.id}")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_events_integration/test_delete_event.yaml")
async def test_delete_event():
    """
    Test deleting an event.

    Validates DELETE operation works correctly.

    Cassette: tests/cassettes/integration/test_events_integration/test_delete_event.yaml
    """
    async with Upsales.from_env() as upsales:
        companies = await upsales.companies.list(limit=1)
        if not companies:
            pytest.skip("No companies found")

        # Create an event
        event = await upsales.events.create(
            entityType="manual",
            score=5,
            client={"id": companies[0].id},
            value="Test deletion",
        )

        event_id = event.id
        assert event_id > 0

        # Delete it
        await upsales.events.delete(event_id)

        print(f"[OK] Successfully deleted event {event_id}")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_events_integration/test_event_with_nested_objects.yaml")
async def test_event_with_nested_objects():
    """
    Test event creation with nested partial objects.

    Validates that PartialCompany and other nested models parse correctly
    in the API response.

    Cassette: tests/cassettes/integration/test_events_integration/test_event_with_nested_objects.yaml
    """
    async with Upsales.from_env() as upsales:
        companies = await upsales.companies.list(limit=1)
        if not companies:
            pytest.skip("No companies found")

        company = companies[0]

        # Create event with company reference
        event = await upsales.events.create(
            entityType="manual",
            score=8,
            client={"id": company.id},
            value="Test nested objects",
        )

        try:
            # Validate nested PartialCompany
            assert event.client is not None
            assert hasattr(event.client, "id")
            assert event.client.id == company.id
            assert hasattr(event.client, "name")
            assert isinstance(event.client.name, str)

            print(f"[OK] Nested PartialCompany validated:")
            print(f"  Company ID: {event.client.id}")
            print(f"  Company name: {event.client.name}")

            # Validate other nested object fields exist (may be None)
            assert hasattr(event, "opportunity")
            assert hasattr(event, "order")
            assert hasattr(event, "form")
            assert hasattr(event, "activity")
            assert hasattr(event, "appointment")

            print(f"[OK] All nested object fields present in model")

        finally:
            await upsales.events.delete(event.id)


@pytest.mark.asyncio
@my_vcr.use_cassette("test_events_integration/test_event_edit_not_supported.yaml")
async def test_event_edit_not_supported():
    """
    Test that edit() raises NotImplementedError.

    Events cannot be edited via API (only CREATE and DELETE).

    Cassette: tests/cassettes/integration/test_events_integration/test_event_edit_not_supported.yaml
    """
    async with Upsales.from_env() as upsales:
        companies = await upsales.companies.list(limit=1)
        if not companies:
            pytest.skip("No companies found")

        # Create an event
        event = await upsales.events.create(
            entityType="manual",
            score=5,
            client={"id": companies[0].id},
            value="Test edit not supported",
        )

        try:
            # Test that edit() raises NotImplementedError
            with pytest.raises(NotImplementedError, match="Events cannot be edited"):
                await event.edit(value="This should fail")

            print("[OK] edit() correctly raises NotImplementedError")

        finally:
            await upsales.events.delete(event.id)


@pytest.mark.asyncio
@my_vcr.use_cassette("test_events_integration/test_event_types.yaml")
async def test_event_types():
    """
    Test creating different event types.

    Validates that different entityType values work and computed fields
    respond correctly.

    Cassette: tests/cassettes/integration/test_events_integration/test_event_types.yaml
    """
    async with Upsales.from_env() as upsales:
        companies = await upsales.companies.list(limit=1)
        if not companies:
            pytest.skip("No companies found")

        company_id = companies[0].id

        # Test manual event
        manual_event = await upsales.events.create(
            entityType="manual",
            score=5,
            client={"id": company_id},
            value="Manual event test",
        )

        try:
            assert manual_event.entityType == "manual"
            assert manual_event.is_manual is True
            assert manual_event.is_marketing is False
            assert manual_event.is_news is False

            print(f"[OK] Manual event computed fields correct")

        finally:
            await upsales.events.delete(manual_event.id)

        # Note: Other event types like 'marketingCustom' and 'news' may require
        # additional setup or permissions, so we only test 'manual' which works
        # in all environments
