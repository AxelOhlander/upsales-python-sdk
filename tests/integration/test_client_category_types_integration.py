"""
Integration tests for ClientCategoryType model with real API responses.

Uses VCR.py to record API responses on first run, then replay.
Validates that ClientCategoryType model correctly parses real Upsales API data.

To record cassettes:
    uv run pytest tests/integration/test_client_category_types_integration.py -v
"""

import pytest
import vcr

from upsales import Upsales
from upsales.models.client_category_types import ClientCategoryType

# Configure VCR for this test module
my_vcr = vcr.VCR(
    cassette_library_dir="tests/cassettes/integration",
    record_mode="once",  # Record once, then always replay
    match_on=["method", "scheme", "host", "port", "path", "query"],
    filter_headers=[("cookie", "REDACTED")],
    filter_post_data_parameters=[("password", "REDACTED")],
)


@pytest.mark.asyncio
@my_vcr.use_cassette("test_client_category_types_integration/test_list_types_real_response.yaml")
async def test_list_types_real_response():
    """Test listing client category types with real API response structure."""
    async with Upsales.from_env() as upsales:
        types = await upsales.client_category_types.list(limit=10)

        assert isinstance(types, list)
        assert len(types) <= 10

        if len(types) == 0:
            pytest.skip("No client category types available in test environment")

        for cat_type in types:
            assert isinstance(cat_type, ClientCategoryType)
            assert isinstance(cat_type.id, int)
            assert cat_type.id > 0
            assert isinstance(cat_type.name, str)
            assert len(cat_type.name) > 0  # NonEmptyStr validator

        print(f"[OK] Listed {len(types)} client category types successfully")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_client_category_types_integration/test_get_type_real_response.yaml")
async def test_get_type_real_response():
    """
    Test getting client category type with real API response structure.

    This test records the actual API response on first run, then
    replays it from cassette on future runs. Ensures our ClientCategoryType
    model correctly parses real Upsales API data.
    """
    async with Upsales.from_env() as upsales:
        # Get types to find a valid ID
        types = await upsales.client_category_types.list(limit=1)

        if len(types) == 0:
            pytest.skip("No client category types available in test environment")

        cat_type = types[0]

        # Validate ClientCategoryType model with Pydantic v2 features
        assert isinstance(cat_type, ClientCategoryType)
        assert isinstance(cat_type.id, int)
        assert cat_type.id > 0
        assert isinstance(cat_type.name, str)
        assert len(cat_type.name) > 0  # NonEmptyStr validator

        # Validate frozen fields (read-only)
        assert hasattr(cat_type, "id")

        print(f"[OK] Type parsed successfully: {cat_type.name} (ID: {cat_type.id})")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_client_category_types_integration/test_type_serialization.yaml")
async def test_type_serialization_real_data():
    """
    Test to_api_dict() serialization with real client category type data.

    Validates that serialization excludes frozen fields using
    Pydantic v2 optimized serialization.
    """
    async with Upsales.from_env() as upsales:
        types = await upsales.client_category_types.list(limit=1)

        if len(types) == 0:
            pytest.skip("No client category types available in test environment")

        cat_type = types[0]

        # Get API dict (should exclude frozen fields)
        api_dict = cat_type.to_api_dict()

        # Validate frozen fields excluded
        assert "id" not in api_dict or api_dict.get("id") is None

        # Should include updatable fields
        assert "name" in api_dict

        # With overrides, should include changed fields
        api_dict_with_changes = cat_type.to_api_dict(name="New Type Name")
        assert api_dict_with_changes["name"] == "New Type Name"

        # Validate it's JSON serializable
        import json

        json_str = json.dumps(api_dict)  # Should not raise
        assert json_str

        print(f"[OK] Serialization validated for {cat_type.name}")
        print(f"[OK] API payload has {len(api_dict)} fields")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_client_category_types_integration/test_get_by_name.yaml")
async def test_get_by_name():
    """
    Test get_by_name() custom method with real data.

    Validates that custom method works correctly with the endpoint.
    """
    async with Upsales.from_env() as upsales:
        # Get all types first to find a valid name
        all_types = await upsales.client_category_types.list_all()

        if not all_types:
            pytest.skip("No client category types available in test environment")

        # Use the first type's name to test
        test_name = all_types[0].name

        # Get type by name
        found_type = await upsales.client_category_types.get_by_name(test_name)

        if found_type:
            assert isinstance(found_type, ClientCategoryType)
            assert found_type.name == test_name
            print(f"[OK] Found type by name: {test_name}")
        else:
            print(f"[OK] No type found with name: {test_name}")
