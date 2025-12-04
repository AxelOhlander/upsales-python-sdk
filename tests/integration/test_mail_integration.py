"""
Integration tests for Mail model with real API responses.

Uses VCR.py to record API responses on first run, then replay them.
Validates that our Pydantic v2 models correctly parse real API data.

To record cassettes:
    uv run pytest tests/integration/test_mail_integration.py -v

To re-record (delete cassette first):
    rm -r tests/cassettes/integration/test_mail_integration/
    uv run pytest tests/integration/test_mail_integration.py -v
"""

import pytest
import vcr

from upsales import Upsales
from upsales.models.company import PartialCompany
from upsales.models.contacts import PartialContact
from upsales.models.mail import Mail
from upsales.models.projects import PartialProject
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
@my_vcr.use_cassette("test_mail_integration/test_list_mail_real_response.yaml")
async def test_list_mail_real_response():
    """
    Test listing mail with real API response structure.

    Validates that Mail model correctly parses list responses
    with pagination metadata.

    Cassette: tests/cassettes/integration/test_mail_integration/test_list_mail_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        # Get mail with limit
        mail_list = await upsales.mail.list(limit=5)

        assert isinstance(mail_list, list)
        assert len(mail_list) <= 5

        if len(mail_list) == 0:
            pytest.skip("No mail found in the system")

        for mail in mail_list:
            assert isinstance(mail, Mail)
            assert isinstance(mail.id, int)
            assert mail.id > 0
            assert isinstance(mail.subject, str)
            assert isinstance(mail.body, str)

            # Validate read-only fields
            assert isinstance(mail.modDate, str)
            assert isinstance(mail.userRemovable, bool)
            assert isinstance(mail.userEditable, bool)

            # Validate BinaryFlag field (0 or 1)
            assert mail.isMap in (0, 1)

            # Validate required fields
            assert isinstance(mail.date, str)
            assert isinstance(mail.type, str)
            assert mail.type in ("out", "in", "pro", "err")
            assert isinstance(mail.to, str)
            assert isinstance(mail.from_address, str)
            assert isinstance(mail.fromName, str)

            # Validate system IDs
            assert isinstance(mail.groupMailId, int)
            assert isinstance(mail.jobId, int)
            assert isinstance(mail.mailBodySnapshotId, int)
            assert isinstance(mail.mailThreadId, int)

        print(f"[OK] Listed {len(mail_list)} mail successfully")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_mail_integration/test_get_mail_real_response.yaml")
async def test_get_mail_real_response():
    """
    Test getting a single mail with real API response structure.

    This test records the actual API response on first run, then
    replays it from cassette on future runs. This ensures our Mail
    model correctly parses real Upsales API data.

    Cassette: tests/cassettes/integration/test_mail_integration/test_get_mail_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        # Get mail first to find a valid ID
        mail_list = await upsales.mail.list(limit=1)

        if len(mail_list) == 0:
            pytest.skip("No mail found in the system")

        mail_id = mail_list[0].id

        # Get single mail by ID
        mail = await upsales.mail.get(mail_id)

        # Validate Mail model with Pydantic v2 features
        assert isinstance(mail, Mail)
        assert mail.id == mail_id
        assert isinstance(mail.subject, str)
        assert isinstance(mail.body, str)

        # Validate timestamps
        assert isinstance(mail.modDate, str)
        assert isinstance(mail.date, str)

        # Validate BinaryFlag validator (0 or 1)
        assert mail.isMap in (0, 1)

        # Validate type
        assert isinstance(mail.type, str)
        assert mail.type in ("out", "in", "pro", "err")

        # Validate email addresses
        assert isinstance(mail.to, str)
        assert isinstance(mail.from_address, str)
        assert isinstance(mail.fromName, str)

        # Validate system IDs
        assert isinstance(mail.groupMailId, int)
        assert isinstance(mail.jobId, int)
        assert isinstance(mail.mailBodySnapshotId, int)
        assert isinstance(mail.mailThreadId, int)

        # Validate lists
        assert isinstance(mail.cc, list)
        assert isinstance(mail.bcc, list)
        assert isinstance(mail.attachments, list)
        assert isinstance(mail.events, list)
        assert isinstance(mail.tags, list)
        assert isinstance(mail.users, list)

        # Validate dicts
        assert isinstance(mail.recipients, dict)
        assert isinstance(mail.thread, dict)

        # Validate boolean fields
        assert isinstance(mail.userRemovable, bool)
        assert isinstance(mail.userEditable, bool)

        print(f"[OK] Mail parsed successfully: {mail.subject} (ID: {mail.id})")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_mail_integration/test_mail_nested_objects.yaml")
async def test_mail_nested_objects():
    """
    Test that nested objects (PartialUser, PartialCompany, etc.) parse correctly.

    These nested objects often have fewer fields than their full counterparts,
    so this validates our Partial models handle the actual API responses.

    Cassette: tests/cassettes/integration/test_mail_integration/test_mail_nested_objects.yaml
    """
    async with Upsales.from_env() as upsales:
        mail_list = await upsales.mail.list(limit=20)

        if len(mail_list) == 0:
            pytest.skip("No mail found in the system")

        # Check various nested objects across mail
        found_user = False
        found_client = False
        found_contact = False
        found_project = False

        for mail in mail_list:
            # Test users if present
            if mail.users:
                found_user = True
                for user in mail.users:
                    assert isinstance(user, PartialUser)
                    assert hasattr(user, "id")
                    assert hasattr(user, "name")
                    assert isinstance(user.id, int)
                    print(f"  [OK] user: id={user.id}, name={user.name}")

            # Test client (company) if present
            if mail.company is not None:
                found_client = True
                assert isinstance(mail.company, PartialCompany)
                assert hasattr(mail.company, "id")
                assert hasattr(mail.company, "name")
                assert isinstance(mail.company.id, int)
                print(f"  [OK] client: id={mail.company.id}, name={mail.company.name}")

            # Test contact if present
            if mail.contact is not None:
                found_contact = True
                assert isinstance(mail.contact, PartialContact)
                assert hasattr(mail.contact, "id")
                assert isinstance(mail.contact.id, int)
                print(f"  [OK] contact: id={mail.contact.id}")

            # Test project if present
            if mail.project is not None:
                found_project = True
                assert isinstance(mail.project, PartialProject)
                assert hasattr(mail.project, "id")
                assert isinstance(mail.project.id, int)
                print(f"  [OK] project: id={mail.project.id}")

        print(
            f"\n[OK] Nested objects found - user:{found_user}, client:{found_client}, "
            f"contact:{found_contact}, project:{found_project}"
        )


@pytest.mark.asyncio
@my_vcr.use_cassette("test_mail_integration/test_mail_computed_fields.yaml")
async def test_mail_computed_fields():
    """
    Test computed fields work correctly with real API data.

    Validates is_outgoing, is_incoming, has_error, is_map_email,
    has_attachments, has_tracking_events computed properties.

    Cassette: tests/cassettes/integration/test_mail_integration/test_mail_computed_fields.yaml
    """
    async with Upsales.from_env() as upsales:
        mail_list = await upsales.mail.list(limit=10)

        if len(mail_list) == 0:
            pytest.skip("No mail found in the system")

        mail = mail_list[0]

        # Test is_outgoing computed field
        assert isinstance(mail.is_outgoing, bool)
        assert mail.is_outgoing == (mail.type == "out")
        print(f"[OK] is_outgoing: {mail.is_outgoing} (type={mail.type})")

        # Test is_incoming computed field
        assert isinstance(mail.is_incoming, bool)
        assert mail.is_incoming == (mail.type == "in")
        print(f"[OK] is_incoming: {mail.is_incoming} (type={mail.type})")

        # Test has_error computed field
        assert isinstance(mail.has_error, bool)
        assert mail.has_error == (mail.type == "err")
        print(f"[OK] has_error: {mail.has_error} (type={mail.type})")

        # Test from_ computed field (alias for from_address)
        assert isinstance(mail.from_, str)
        assert mail.from_ == mail.from_address
        print(f"[OK] from_: {mail.from_} == from_address: {mail.from_address}")

        # Test is_map_email computed field
        assert isinstance(mail.is_map_email, bool)
        assert mail.is_map_email == (mail.isMap == 1)
        print(f"[OK] is_map_email: {mail.is_map_email} (isMap={mail.isMap})")

        # Test has_attachments computed field
        assert isinstance(mail.has_attachments, bool)
        assert mail.has_attachments == (len(mail.attachments) > 0)
        print(
            f"[OK] has_attachments: {mail.has_attachments} (attachments count={len(mail.attachments)})"
        )

        # Test has_tracking_events computed field
        assert isinstance(mail.has_tracking_events, bool)
        assert mail.has_tracking_events == (len(mail.events) > 0)
        print(
            f"[OK] has_tracking_events: {mail.has_tracking_events} (events count={len(mail.events)})"
        )


@pytest.mark.asyncio
@my_vcr.use_cassette("test_mail_integration/test_mail_type_filters.yaml")
async def test_mail_type_filters():
    """
    Test filtering mail by type.

    Validates different mail types (out, in, pro, err) parse correctly.

    Cassette: tests/cassettes/integration/test_mail_integration/test_mail_type_filters.yaml
    """
    async with Upsales.from_env() as upsales:
        # Try to get different types
        outgoing = await upsales.mail.list(limit=5, type="out")
        incoming = await upsales.mail.list(limit=5, type="in")

        # Validate outgoing
        if outgoing:
            for mail in outgoing:
                assert isinstance(mail, Mail)
                assert mail.type == "out"
                assert mail.is_outgoing is True
            print(f"[OK] Found {len(outgoing)} outgoing mail")
        else:
            print("[SKIP] No outgoing mail found")

        # Validate incoming
        if incoming:
            for mail in incoming:
                assert isinstance(mail, Mail)
                assert mail.type == "in"
                assert mail.is_incoming is True
            print(f"[OK] Found {len(incoming)} incoming mail")
        else:
            print("[SKIP] No incoming mail found")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_mail_integration/test_mail_attachments.yaml")
async def test_mail_attachments():
    """
    Test mail with attachments.

    Validates attachments field structure and has_attachments computed field.

    Cassette: tests/cassettes/integration/test_mail_integration/test_mail_attachments.yaml
    """
    async with Upsales.from_env() as upsales:
        mail_list = await upsales.mail.list(limit=50)

        if len(mail_list) == 0:
            pytest.skip("No mail found in the system")

        # Find mail with attachments
        mail_with_attachments = None
        for mail in mail_list:
            if mail.attachments:
                mail_with_attachments = mail
                break

        if mail_with_attachments:
            assert isinstance(mail_with_attachments.attachments, list)
            assert len(mail_with_attachments.attachments) > 0
            assert mail_with_attachments.has_attachments is True

            # Validate attachment structure
            for attachment in mail_with_attachments.attachments:
                assert isinstance(attachment, dict)

            print(f"[OK] Found mail with {len(mail_with_attachments.attachments)} attachments")
        else:
            print("[SKIP] No mail with attachments found in sample")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_mail_integration/test_mail_tracking_events.yaml")
async def test_mail_tracking_events():
    """
    Test mail with tracking events.

    Validates events field structure and has_tracking_events computed field.

    Cassette: tests/cassettes/integration/test_mail_integration/test_mail_tracking_events.yaml
    """
    async with Upsales.from_env() as upsales:
        mail_list = await upsales.mail.list(limit=50)

        if len(mail_list) == 0:
            pytest.skip("No mail found in the system")

        # Find mail with tracking events
        mail_with_events = None
        for mail in mail_list:
            if mail.events:
                mail_with_events = mail
                break

        if mail_with_events:
            assert isinstance(mail_with_events.events, list)
            assert len(mail_with_events.events) > 0
            assert mail_with_events.has_tracking_events is True

            # Validate event structure
            for event in mail_with_events.events:
                assert isinstance(event, dict)

            print(f"[OK] Found mail with {len(mail_with_events.events)} tracking events")
        else:
            print("[SKIP] No mail with tracking events found in sample")
