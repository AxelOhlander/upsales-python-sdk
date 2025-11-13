"""
Integration tests for API Key model with real API responses.

Uses VCR.py to record API responses on first run, then replay them.
Validates that our Pydantic v2 models correctly parse real API data.

To record cassettes:
    uv run pytest tests/integration/test_apikeys_integration.py -v

To re-record (delete cassette first):
    rm tests/cassettes/integration/test_apikeys_integration/*.yaml
    uv run pytest tests/integration/test_apikeys_integration.py -v
"""

import pytest
import vcr

from upsales import Upsales
from upsales.models.api_keys import ApiKey

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
@my_vcr.use_cassette("test_apikeys_integration/test_get_apikey_real_response.yaml")
async def test_get_apikey_real_response():
    """
    Test getting an API key with real API response structure.

    This test records the actual API response on first run, then
    replays it from cassette on future runs. This ensures our ApiKey
    model correctly parses real Upsales API data.

    Cassette: tests/cassettes/integration/test_apikeys_integration/test_get_apikey_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        # Get a real API key (or replay from cassette)
        apikeys = await upsales.apikeys.list(limit=1)

        assert len(apikeys) > 0, "Should have at least one API key"
        apikey = apikeys[0]

        # Validate ApiKey model with Pydantic v2 features
        assert isinstance(apikey, ApiKey)
        assert isinstance(apikey.id, int)
        assert isinstance(apikey.name, str)
        assert apikey.name  # Name should not be empty (NonEmptyStr validator)

        # Validate active field (bool)
        assert isinstance(apikey.active, bool)

        # Validate computed fields
        assert isinstance(apikey.is_active, bool)
        assert apikey.is_active == apikey.active

        print(
            f"[OK] API Key parsed successfully: {apikey.name} (ID: {apikey.id}, Active: {apikey.is_active})"
        )


@pytest.mark.asyncio
@my_vcr.use_cassette("test_apikeys_integration/test_list_apikeys_real_response.yaml")
async def test_list_apikeys_real_response():
    """
    Test listing API keys with real API response.

    Validates that list responses correctly parse and return multiple ApiKey objects.

    Cassette: tests/cassettes/integration/test_apikeys_integration/test_list_apikeys_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        # List API keys (or replay from cassette)
        apikeys = await upsales.apikeys.list(limit=10)

        assert isinstance(apikeys, list)
        assert all(isinstance(key, ApiKey) for key in apikeys)

        if len(apikeys) > 0:
            # Validate first API key
            apikey = apikeys[0]
            assert apikey.id > 0
            assert apikey.name
            assert isinstance(apikey.active, bool)

            print(f"[OK] Listed {len(apikeys)} API keys successfully")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_apikeys_integration/test_apikey_computed_fields.yaml")
async def test_apikey_computed_fields():
    """
    Test computed fields work with real data.

    Validates that computed properties (is_active) return correct values
    based on actual API data.

    Cassette: tests/cassettes/integration/test_apikeys_integration/test_apikey_computed_fields.yaml
    """
    async with Upsales.from_env() as upsales:
        apikeys = await upsales.apikeys.list(limit=5)

        for apikey in apikeys:
            # Test computed field: is_active
            if apikey.active:
                assert apikey.is_active is True
            else:
                assert apikey.is_active is False

        print(f"[OK] Computed fields validated for {len(apikeys)} API keys")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_apikeys_integration/test_apikey_custom_methods.yaml")
async def test_apikey_custom_methods():
    """
    Test custom resource methods with real data.

    Validates get_active(), get_inactive(), and get_by_name() methods
    work correctly with actual API responses.

    Cassette: tests/cassettes/integration/test_apikeys_integration/test_apikey_custom_methods.yaml
    """
    async with Upsales.from_env() as upsales:
        # Test get_active()
        active_keys = await upsales.apikeys.get_active()
        assert isinstance(active_keys, list)
        assert all(key.is_active for key in active_keys)

        # Test get_inactive()
        inactive_keys = await upsales.apikeys.get_inactive()
        assert isinstance(inactive_keys, list)
        assert all(not key.is_active for key in inactive_keys)

        # Test get_by_name() with first active key
        if len(active_keys) > 0:
            first_key = active_keys[0]
            found_key = await upsales.apikeys.get_by_name(first_key.name)
            assert found_key is not None
            assert found_key.id == first_key.id
            assert found_key.name == first_key.name

        print(
            f"[OK] Custom methods validated: {len(active_keys)} active, {len(inactive_keys)} inactive"
        )
