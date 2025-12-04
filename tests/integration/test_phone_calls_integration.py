"""
Integration tests for PhoneCall model with real API responses.

Uses VCR.py to record API responses on first run, then replay them.
Validates that our Pydantic v2 models correctly parse real API data.

To record cassettes:
    uv run pytest tests/integration/test_phone_calls_integration.py -v

To re-record (delete cassette first):
    rm -r tests/cassettes/integration/test_phone_calls_integration/
    uv run pytest tests/integration/test_phone_calls_integration.py -v
"""

import pytest
import vcr

from upsales import Upsales
from upsales.models.company import PartialCompany
from upsales.models.contacts import PartialContact
from upsales.models.phone_call import PhoneCall
from upsales.models.user import PartialUser

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
@my_vcr.use_cassette("test_phone_calls_integration/test_list_phone_calls_real_response.yaml")
async def test_list_phone_calls_real_response():
    """
    Test listing phone calls with real API response structure.

    Validates that PhoneCall model correctly parses list responses
    with pagination metadata.

    Cassette: tests/cassettes/integration/test_phone_calls_integration/test_list_phone_calls_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        phone_calls = await upsales.phone_calls.list(limit=10)

        assert isinstance(phone_calls, list)

        if len(phone_calls) == 0:
            pytest.skip("No phone calls found in the system")

        for call in phone_calls:
            assert isinstance(call, PhoneCall)
            assert isinstance(call.id, int)
            assert call.id > 0

            # Validate required relationships
            assert isinstance(call.user, PartialUser)
            assert isinstance(call.contact, PartialContact)
            assert isinstance(call.client, PartialCompany)

            # Validate call details
            assert isinstance(call.durationInS, int)
            assert call.durationInS >= 0
            assert isinstance(call.phoneNumber, str)
            assert isinstance(call.date, str)
            assert isinstance(call.type, str)
            assert isinstance(call.status, int)

            # Validate optional fields
            if call.conversationUrl is not None:
                assert isinstance(call.conversationUrl, str)
            assert isinstance(call.externalId, str)
            assert isinstance(call.related, list)

        print(f"[OK] Listed {len(phone_calls)} phone calls successfully")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_phone_calls_integration/test_get_phone_call_real_response.yaml")
async def test_get_phone_call_real_response():
    """
    Test getting a single phone call with real API response structure.

    Validates full PhoneCall model including all nested objects.

    Cassette: tests/cassettes/integration/test_phone_calls_integration/test_get_phone_call_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        # First list to get a valid phone call ID
        calls = await upsales.phone_calls.list(limit=1)

        if len(calls) == 0:
            pytest.skip("No phone calls found in the system")

        call_id = calls[0].id

        # Now get the specific phone call
        call = await upsales.phone_calls.get(call_id)

        assert isinstance(call, PhoneCall)
        assert call.id == call_id

        # Validate required relationships exist
        assert isinstance(call.user, PartialUser)
        assert hasattr(call.user, "id")
        assert hasattr(call.user, "name")

        assert isinstance(call.contact, PartialContact)
        assert hasattr(call.contact, "id")

        assert isinstance(call.client, PartialCompany)
        assert hasattr(call.client, "id")
        assert hasattr(call.client, "name")

        # Validate call details
        assert isinstance(call.durationInS, int)
        assert isinstance(call.phoneNumber, str)
        assert isinstance(call.date, str)
        assert isinstance(call.type, str)
        assert isinstance(call.status, int)

        # Validate optional fields
        if call.conversationUrl:
            assert isinstance(call.conversationUrl, str)
        assert isinstance(call.externalId, str)
        assert isinstance(call.related, list)

        print(f"[OK] Got phone call {call.id}: {call.phoneNumber} ({call.type})")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_phone_calls_integration/test_phone_call_nested_objects.yaml")
async def test_phone_call_nested_objects():
    """
    Test that nested objects (PartialUser, PartialCompany, PartialContact) parse correctly.

    These nested objects often have fewer fields than their full counterparts,
    so this validates our Partial models handle the actual API responses.

    Cassette: tests/cassettes/integration/test_phone_calls_integration/test_phone_call_nested_objects.yaml
    """
    async with Upsales.from_env() as upsales:
        calls = await upsales.phone_calls.list(limit=10)

        if len(calls) == 0:
            pytest.skip("No phone calls found in the system")

        # Check nested objects across calls
        found_user = False
        found_contact = False
        found_client = False

        for call in calls:
            # Test user (required field)
            if call.user is not None:
                found_user = True
                assert isinstance(call.user, PartialUser)
                assert hasattr(call.user, "id")
                assert hasattr(call.user, "name")
                assert isinstance(call.user.id, int)
                assert isinstance(call.user.name, str)
                print(f"  [OK] user: id={call.user.id}, name={call.user.name}")

            # Test contact (required field)
            if call.contact is not None:
                found_contact = True
                assert isinstance(call.contact, PartialContact)
                assert hasattr(call.contact, "id")
                assert isinstance(call.contact.id, int)
                print(f"  [OK] contact: id={call.contact.id}")

            # Test client/company (required field)
            if call.client is not None:
                found_client = True
                assert isinstance(call.client, PartialCompany)
                assert hasattr(call.client, "id")
                assert hasattr(call.client, "name")
                assert isinstance(call.client.id, int)
                assert isinstance(call.client.name, str)
                print(f"  [OK] client: id={call.client.id}, name={call.client.name}")

        print(
            f"\n[OK] Nested objects found - user:{found_user}, "
            f"contact:{found_contact}, client:{found_client}"
        )


@pytest.mark.asyncio
@my_vcr.use_cassette("test_phone_calls_integration/test_phone_call_details.yaml")
async def test_phone_call_details():
    """
    Test that phone call details parse correctly.

    Validates duration, phone number, date, type, status fields with real API data.

    Cassette: tests/cassettes/integration/test_phone_calls_integration/test_phone_call_details.yaml
    """
    async with Upsales.from_env() as upsales:
        calls = await upsales.phone_calls.list(limit=10)

        if len(calls) == 0:
            pytest.skip("No phone calls found in the system")

        call = calls[0]

        # Test duration (should be non-negative integer)
        assert isinstance(call.durationInS, int)
        assert call.durationInS >= 0
        print(f"[OK] durationInS: {call.durationInS}s")

        # Test phone number (should be string)
        assert isinstance(call.phoneNumber, str)
        print(f"[OK] phoneNumber: {call.phoneNumber}")

        # Test date (should be string in API format)
        assert isinstance(call.date, str)
        print(f"[OK] date: {call.date}")

        # Test type (should be string)
        assert isinstance(call.type, str)
        print(f"[OK] type: {call.type}")

        # Test status (should be integer)
        assert isinstance(call.status, int)
        print(f"[OK] status: {call.status}")

        # Test optional conversationUrl
        if call.conversationUrl:
            assert isinstance(call.conversationUrl, str)
            print(f"[OK] conversationUrl: {call.conversationUrl}")
        else:
            print("[OK] conversationUrl: None (optional)")

        # Test externalId
        assert isinstance(call.externalId, str)
        print(f"[OK] externalId: {call.externalId if call.externalId else '(empty)'}")

        # Test related list
        assert isinstance(call.related, list)
        print(f"[OK] related: {len(call.related)} related objects")
