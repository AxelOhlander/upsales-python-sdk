"""
Integration tests for Contact model with real API responses.

Uses VCR.py to record API responses on first run, then replay them.
Validates that our Pydantic v2 models correctly parse real API data.

To record cassettes:
    uv run pytest tests/integration/test_contacts_integration.py -v

To re-record (delete cassette first):
    rm tests/cassettes/integration/test_contacts_integration/*.yaml
    uv run pytest tests/integration/test_contacts_integration.py -v
"""

import pytest
import vcr

from upsales import Upsales
from upsales.models.contacts import Contact

# Configure VCR for these tests
my_vcr = vcr.VCR(
    cassette_library_dir="tests/cassettes/integration",
    record_mode="once",  # Record once, then always replay
    match_on=["method", "scheme", "host", "port", "path", "query"],
    filter_headers=[
        ("cookie", "REDACTED"),
        ("authorization", "REDACTED"),
    ],
    filter_post_data_parameters=[
        ("password", "REDACTED"),
    ],
)


@pytest.mark.asyncio
@my_vcr.use_cassette("test_contacts_integration/test_get_contact_real_response.yaml")
async def test_get_contact_real_response():
    """
    Test getting a contact with real API response structure.

    This test records the actual API response on first run, then
    replays it from cassette on future runs. This ensures our Contact
    model correctly parses real Upsales API data.

    Cassette: tests/cassettes/integration/test_contacts_integration/test_get_contact_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        # Get a real contact (or replay from cassette)
        contacts = await upsales.contacts.list(limit=1)

        assert len(contacts) > 0, "Should have at least one contact"
        contact = contacts[0]

        # Validate Contact model with Pydantic v2 features
        assert isinstance(contact, Contact)
        assert isinstance(contact.id, int)
        assert isinstance(contact.name, str)

        # Email is normalized to lowercase by EmailStr validator
        if contact.email:
            assert contact.email == contact.email.lower()

        # Validate BinaryFlag field (0 or 1)
        assert contact.active in (0, 1)

        # Validate computed fields
        assert isinstance(contact.is_active, bool)
        assert isinstance(contact.full_name, str)
        assert isinstance(contact.has_phone, bool)

        # Validate custom_fields property
        assert hasattr(contact, "custom_fields")

        print(f"[OK] Contact parsed successfully: {contact.name} (ID: {contact.id})")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_contacts_integration/test_list_contacts_real_response.yaml")
async def test_list_contacts_real_response():
    """
    Test listing contacts with real API response structure.

    Validates pagination metadata and multiple contact objects.

    Cassette: tests/cassettes/integration/test_contacts_integration/test_list_contacts_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        # Get contacts with limit
        contacts = await upsales.contacts.list(limit=5)

        assert isinstance(contacts, list)
        assert len(contacts) <= 5

        for contact in contacts:
            assert isinstance(contact, Contact)
            assert contact.id > 0
            assert len(contact.name) > 0

        print(f"[OK] Listed {len(contacts)} contacts successfully")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_contacts_integration/test_contact_computed_fields_with_real_data.yaml")
async def test_contact_computed_fields_with_real_data():
    """
    Test computed fields work correctly with real API data.

    Validates all computed properties return expected types and values.

    Cassette: tests/cassettes/integration/test_contacts_integration/test_contact_computed_fields_with_real_data.yaml
    """
    async with Upsales.from_env() as upsales:
        contacts = await upsales.contacts.list(limit=5)

        for contact in contacts:
            # Test computed fields
            assert isinstance(contact.is_active, bool)
            assert contact.is_active == (contact.active == 1)

            assert isinstance(contact.full_name, str)
            # full_name should be firstName + lastName, or fall back to name
            if contact.firstName and contact.lastName:
                assert contact.full_name == f"{contact.firstName} {contact.lastName}"
            else:
                assert contact.full_name == contact.name

            assert isinstance(contact.has_phone, bool)
            assert contact.has_phone == bool(contact.phone or contact.cellPhone)

        print(f"[OK] Computed fields work for {len(contacts)} contacts")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_contacts_integration/test_contact_custom_fields_with_real_data.yaml")
async def test_contact_custom_fields_with_real_data():
    """
    Test custom fields parsing with real API data.

    Validates CustomFieldsList validator and CustomFields helper.

    Cassette: tests/cassettes/integration/test_contacts_integration/test_contact_custom_fields_with_real_data.yaml
    """
    async with Upsales.from_env() as upsales:
        contacts = await upsales.contacts.list(limit=10)

        # Find a contact with custom fields
        contact_with_custom = None
        for contact in contacts:
            if contact.custom:
                contact_with_custom = contact
                break

        if contact_with_custom:
            # Validate custom fields structure (CustomFieldsList validator)
            assert isinstance(contact_with_custom.custom, list)
            for field in contact_with_custom.custom:
                assert "fieldId" in field, "CustomFieldsList should validate fieldId presence"

            # Validate custom_fields helper
            cf = contact_with_custom.custom_fields
            assert hasattr(cf, "__getitem__")

            print(f"[OK] Custom fields validated: {len(contact_with_custom.custom)} fields")
        else:
            print("[SKIP] No contacts with custom fields found")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_contacts_integration/test_create_contact_minimal_fields.yaml")
async def test_create_contact_minimal_fields():
    """
    Test creating contact with only required field (client.id).

    Validates the minimal nested structure requirement discovered through
    test_required_create_fields.py script (2025-11-07).

    FINDING: Only client.id is required! Email is optional (API file was wrong).

    Cassette: tests/cassettes/integration/test_contacts_integration/test_create_contact_minimal_fields.yaml
    """
    async with Upsales.from_env() as upsales:
        # Use a known valid client ID (adjust if needed for your sandbox)
        client_id = 1  # Using client ID 1 for testing

        # Create contact with ONLY required field
        new_contact = await upsales.contacts.create(
            client={"id": client_id}  # Only this is required!
        )

        # Verify creation succeeded
        assert isinstance(new_contact, Contact)
        assert new_contact.id > 0

        # Verify API returns full nested object
        assert hasattr(new_contact, "client")
        # Note: client.id verification depends on PartialCompany working

        print(f"✅ Created contact {new_contact.id} with minimal fields (client.id only)")

        # Note: Cleanup omitted for VCR cassette simplicity
        # Contact can be manually deleted or will be cleaned up in sandbox resets


@pytest.mark.asyncio
@my_vcr.use_cassette("test_contacts_integration/test_create_contact_with_optional_fields.yaml")
async def test_create_contact_with_optional_fields():
    """
    Test creating contact with optional fields.

    Validates that email, name, phone, etc. are all optional fields.

    Cassette: tests/cassettes/integration/test_contacts_integration/test_create_contact_with_optional_fields.yaml
    """
    async with Upsales.from_env() as upsales:
        # Use a known valid client ID (adjust if needed for your sandbox)
        client_id = 1  # Using client ID 1 for testing

        # Create contact with optional fields
        new_contact = await upsales.contacts.create(
            client={"id": client_id},
            name="Test Contact",
            email="test.contact@example.com",
            phone="+1-555-0123",
            title="Test Engineer",
            active=1,
        )

        # Verify creation succeeded
        assert isinstance(new_contact, Contact)
        assert new_contact.id > 0
        assert new_contact.name == "Test Contact"
        assert new_contact.email == "test.contact@example.com"
        assert new_contact.phone == "+1-555-0123"
        assert new_contact.title == "Test Engineer"
        assert new_contact.active == 1

        print(f"✅ Created detailed contact {new_contact.id}")

        # Clean up
        await upsales.contacts.delete(new_contact.id)
        print(f"🗑️  Cleaned up test contact {new_contact.id}")
