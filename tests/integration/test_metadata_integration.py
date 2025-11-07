"""
Integration tests for Metadata model with real API responses.

Uses VCR.py to record API responses on first run, then replay them.
Validates that our Pydantic v2 models correctly parse real API data.

To record cassettes:
    uv run pytest tests/integration/test_metadata_integration.py -v

To re-record (delete cassette first):
    rm tests/cassettes/integration/test_metadata_integration/*.yaml
    uv run pytest tests/integration/test_metadata_integration.py -v
"""

import pytest
import vcr

from upsales import Upsales
from upsales.models.metadata import Currency, FieldDefinition, Metadata, MetadataUser

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
@my_vcr.use_cassette("test_metadata_integration/test_get_metadata_real_response.yaml")
async def test_get_metadata_real_response():
    """
    Test getting metadata with real API response structure.

    This test records the actual API response on first run, then
    replays it from cassette on future runs. This ensures our Metadata
    model correctly parses real Upsales API data.

    Cassette: tests/cassettes/integration/test_metadata_integration/test_get_metadata_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        # Get metadata (or replay from cassette)
        metadata = await upsales.metadata.get()

        # Validate Metadata model
        assert isinstance(metadata, Metadata)
        assert isinstance(metadata.version, str)
        assert metadata.version  # Should not be empty
        assert isinstance(metadata.licenses, int)
        assert metadata.licenses >= 0

        # Validate user info
        assert isinstance(metadata.user, MetadataUser)
        assert isinstance(metadata.user.id, int)
        assert isinstance(metadata.user.name, str)
        assert metadata.user.administrator in (0, 1)  # BinaryFlag validator
        assert metadata.user.active in (0, 1)  # BinaryFlag validator

        # Validate computed fields on user
        assert isinstance(metadata.user.is_admin, bool)
        assert isinstance(metadata.user.is_active, bool)
        assert isinstance(metadata.user.is_team_leader, bool)
        assert isinstance(metadata.user.has_crm_access, bool)

        # Validate currencies
        assert isinstance(metadata.customerCurrencies, list)
        assert len(metadata.customerCurrencies) > 0
        assert all(isinstance(c, Currency) for c in metadata.customerCurrencies)

        # Validate default currency
        assert isinstance(metadata.defaultCurrency, Currency)
        assert metadata.defaultCurrency.iso
        assert isinstance(metadata.defaultCurrency.rate, float)

        # Validate computed fields on metadata
        assert isinstance(metadata.currency_count, int)
        assert metadata.currency_count == len(metadata.customerCurrencies)
        assert isinstance(metadata.has_multi_currency, bool)
        assert isinstance(metadata.is_enterprise, bool)

        # Validate master currency
        master = metadata.master_currency
        if master:
            assert isinstance(master, Currency)
            assert master.is_master is True

        # Validate active currencies
        active = metadata.active_currencies
        assert isinstance(active, list)
        assert all(c.is_active for c in active)

        # Validate field definitions exist
        assert isinstance(metadata.standardFields, dict)
        assert len(metadata.standardFields) > 0

        # Validate required fields exist
        assert isinstance(metadata.requiredFields, dict)
        assert len(metadata.requiredFields) > 0

        print(
            f"[OK] Metadata parsed successfully: {metadata.version} "
            f"(Licenses: {metadata.licenses}, User: {metadata.user.name})"
        )


@pytest.mark.asyncio
@my_vcr.use_cassette("test_metadata_integration/test_get_currencies_real_response.yaml")
async def test_get_currencies_real_response():
    """
    Test getting currencies from metadata with real API response.

    Validates that currency list is correctly extracted and parsed.

    Cassette: tests/cassettes/integration/test_metadata_integration/test_get_currencies_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        # Get currencies (or replay from cassette)
        currencies = await upsales.metadata.get_currencies()

        assert isinstance(currencies, list)
        assert len(currencies) > 0
        assert all(isinstance(c, Currency) for c in currencies)

        # Check that at least one is master
        masters = [c for c in currencies if c.is_master]
        assert len(masters) == 1, "Should have exactly one master currency"

        # Validate currency fields
        for currency in currencies:
            assert isinstance(currency.iso, str)
            assert len(currency.iso) == 3  # ISO codes are 3 characters
            assert isinstance(currency.rate, float)
            assert currency.rate > 0
            assert isinstance(currency.active, bool)
            assert isinstance(currency.masterCurrency, bool)

        print(f"[OK] Currencies parsed successfully: {len(currencies)} currencies")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_metadata_integration/test_get_entity_fields_real_response.yaml")
async def test_get_entity_fields_real_response():
    """
    Test getting entity field definitions with real API response.

    Validates that field definitions are correctly extracted and parsed.

    Cassette: tests/cassettes/integration/test_metadata_integration/test_get_entity_fields_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        # Get Client entity fields (or replay from cassette)
        fields = await upsales.metadata.get_entity_fields("Client")

        assert isinstance(fields, dict)
        assert len(fields) > 0

        # Check that fields are FieldDefinition objects
        for field_name, field_def in fields.items():
            assert isinstance(field_name, str)
            assert isinstance(field_def, FieldDefinition)
            assert isinstance(field_def.id, int)
            assert isinstance(field_def.name, str)
            assert isinstance(field_def.type, str)
            assert isinstance(field_def.required, bool)
            assert isinstance(field_def.disabled, bool)
            assert isinstance(field_def.active, bool)
            assert isinstance(field_def.group, str)

            # Validate computed fields
            assert isinstance(field_def.is_required, bool)
            assert isinstance(field_def.is_active, bool)

        # Common fields should exist
        common_fields = ["Name", "Phone"]
        for field_name in common_fields:
            if field_name in fields:
                field = fields[field_name]
                assert field.name == field_name
                print(
                    f"[OK] Field '{field_name}' found: type={field.type}, required={field.is_required}"
                )

        print(f"[OK] Entity fields parsed successfully: {len(fields)} fields for Client")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_metadata_integration/test_field_required_check_real_response.yaml")
async def test_field_required_check_real_response():
    """
    Test checking if fields are required with real API response.

    Validates that required field checking works correctly.

    Cassette: tests/cassettes/integration/test_metadata_integration/test_field_required_check_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        # Check various fields (or replay from cassette)
        metadata = await upsales.metadata.get()

        # Check Client fields
        if "Client" in metadata.requiredFields:
            client_required = metadata.requiredFields["Client"]
            assert isinstance(client_required, dict)

            # Test is_field_required method
            for field_name, is_required in client_required.items():
                result = metadata.is_field_required("Client", field_name)
                assert result == is_required
                print(f"[OK] Client.{field_name} required: {result}")

        # Check Contact fields
        if "Contact" in metadata.requiredFields:
            contact_required = metadata.requiredFields["Contact"]
            assert isinstance(contact_required, dict)

            for field_name, is_required in contact_required.items():
                result = metadata.is_field_required("Contact", field_name)
                assert result == is_required
                print(f"[OK] Contact.{field_name} required: {result}")

        print("[OK] Field required checks validated successfully")
