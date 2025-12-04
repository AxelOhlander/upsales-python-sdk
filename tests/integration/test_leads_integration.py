"""
Integration tests for Lead model with real API responses.

Uses VCR.py to record API responses on first run, then replay them.
Validates that our Pydantic v2 models correctly parse real API data.

To record cassettes:
    uv run pytest tests/integration/test_leads_integration.py -v

To re-record (delete cassette first):
    rm -r tests/cassettes/integration/test_leads_integration/
    uv run pytest tests/integration/test_leads_integration.py -v
"""

import pytest
import vcr

from upsales import Upsales
from upsales.models.leads import Lead

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
@my_vcr.use_cassette("test_leads_integration/test_list_leads_real_response.yaml")
async def test_list_leads_real_response() -> None:
    """
    Test listing leads with real API response structure.

    Validates that Lead model correctly parses real API data including
    nested objects like PartialUser, PartialCompany, PartialCampaign, etc.

    Cassette: tests/cassettes/integration/test_leads_integration/test_list_leads_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        leads = await upsales.leads.list(limit=5)

        assert isinstance(leads, list)

        if len(leads) == 0:
            pytest.skip("No leads found in the system")

        for lead in leads:
            assert isinstance(lead, Lead)
            assert isinstance(lead.id, int)
            assert lead.id > 0

            # Validate read-only fields are present
            if lead.regDate is not None:
                assert isinstance(lead.regDate, str)
            if lead.modDate is not None:
                assert isinstance(lead.modDate, str)

            # Validate active flag (BinaryFlag validator: 0 or 1)
            assert lead.active in (0, 1)

            # Validate boolean fields
            assert isinstance(lead.userRemovable, bool)
            assert isinstance(lead.userEditable, bool)

        print(f"[OK] Listed {len(leads)} leads successfully")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_leads_integration/test_get_lead_real_response.yaml")
async def test_get_lead_real_response() -> None:
    """
    Test getting a single lead with real API response structure.

    Validates full Lead model including all nested objects.

    Cassette: tests/cassettes/integration/test_leads_integration/test_get_lead_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        # First list to get a valid lead ID
        leads = await upsales.leads.list(limit=1)

        if len(leads) == 0:
            pytest.skip("No leads found in the system")

        lead_id = leads[0].id

        # Now get the specific lead
        lead = await upsales.leads.get(lead_id)

        assert isinstance(lead, Lead)
        assert lead.id == lead_id

        # Validate core fields
        if lead.name is not None:
            assert isinstance(lead.name, str)
        if lead.description is not None:
            assert isinstance(lead.description, str)
        if lead.contact is not None:
            assert isinstance(lead.contact, str)
        if lead.email is not None:
            assert isinstance(lead.email, str)
        if lead.phone is not None:
            assert isinstance(lead.phone, str)
        if lead.address is not None:
            assert isinstance(lead.address, str)

        # Validate BinaryFlag field
        assert lead.active in (0, 1)

        # Validate custom fields list
        assert isinstance(lead.custom, list)

        # Validate read-only fields
        assert isinstance(lead.userRemovable, bool)
        assert isinstance(lead.userEditable, bool)

        print(f"[OK] Got lead {lead.id}: {lead.name or 'Unnamed'}")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_leads_integration/test_lead_nested_objects.yaml")
async def test_lead_nested_objects() -> None:
    """
    Test that nested objects (PartialUser, PartialCompany, PartialCampaign) parse correctly.

    These nested objects often have fewer fields than their full counterparts,
    so this validates our Partial models handle the actual API responses.

    Cassette: tests/cassettes/integration/test_leads_integration/test_lead_nested_objects.yaml
    """
    async with Upsales.from_env() as upsales:
        leads = await upsales.leads.list(limit=20)

        if len(leads) == 0:
            pytest.skip("No leads found in the system")

        # Check various nested objects across leads
        found_user = False
        found_client = False
        found_project = False
        found_source = False
        found_channel = False

        for lead in leads:
            if lead.user is not None:
                found_user = True
                assert hasattr(lead.user, "id")
                assert hasattr(lead.user, "name")
                print(f"  [OK] user: id={lead.user.id}, name={lead.user.name}")

            if lead.client is not None:
                found_client = True
                assert hasattr(lead.client, "id")
                assert hasattr(lead.client, "name")
                print(f"  [OK] client: id={lead.client.id}, name={lead.client.name}")

            if lead.project is not None:
                found_project = True
                assert hasattr(lead.project, "id")
                print(f"  [OK] project: id={lead.project.id}")

            if lead.source is not None:
                found_source = True
                assert isinstance(lead.source, dict)
                assert "id" in lead.source
                print(f"  [OK] source: id={lead.source['id']}")

            if lead.channel is not None:
                found_channel = True
                assert isinstance(lead.channel, dict)
                assert "id" in lead.channel
                print(f"  [OK] channel: id={lead.channel['id']}")

        print(
            f"\n[OK] Nested objects found - user:{found_user}, client:{found_client}, "
            f"project:{found_project}, source:{found_source}, channel:{found_channel}"
        )


@pytest.mark.asyncio
@my_vcr.use_cassette("test_leads_integration/test_lead_computed_fields.yaml")
async def test_lead_computed_fields() -> None:
    """
    Test computed fields work correctly with real API data.

    Validates is_active computed property.

    Cassette: tests/cassettes/integration/test_leads_integration/test_lead_computed_fields.yaml
    """
    async with Upsales.from_env() as upsales:
        leads = await upsales.leads.list(limit=5)

        if len(leads) == 0:
            pytest.skip("No leads found in the system")

        lead = leads[0]

        # Test computed fields exist and return correct types
        assert isinstance(lead.is_active, bool)
        assert lead.is_active == (lead.active == 1)

        # Test custom_fields property
        assert hasattr(lead, "custom_fields")

        print(f"[OK] Computed fields: is_active={lead.is_active} (active={lead.active})")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_leads_integration/test_lead_custom_fields.yaml")
async def test_lead_custom_fields() -> None:
    """
    Test custom fields parsing with real API data.

    Validates CustomFieldsList validator and CustomFields helper.

    Cassette: tests/cassettes/integration/test_leads_integration/test_lead_custom_fields.yaml
    """
    async with Upsales.from_env() as upsales:
        leads = await upsales.leads.list(limit=20)

        if len(leads) == 0:
            pytest.skip("No leads found in the system")

        # Find a lead with custom fields
        lead_with_custom = None
        for lead in leads:
            if lead.custom:
                lead_with_custom = lead
                break

        if lead_with_custom:
            # Validate custom fields structure (CustomFieldsList validator)
            assert isinstance(lead_with_custom.custom, list)
            for field in lead_with_custom.custom:
                assert "fieldId" in field, "CustomFieldsList should validate fieldId presence"

            # Validate custom_fields helper
            cf = lead_with_custom.custom_fields
            assert hasattr(cf, "__getitem__")

            print(f"[OK] Custom fields validated: {len(lead_with_custom.custom)} fields")
        else:
            print("[SKIP] No leads with custom fields found")
