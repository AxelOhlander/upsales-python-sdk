"""
Integration tests for ClientCategory model with real API responses.

Uses VCR.py to record API responses on first run, then replay.
Validates that ClientCategory model correctly parses real Upsales API data.

To record cassettes:
    uv run pytest tests/integration/test_client_categories_integration.py -v
"""

import pytest
import vcr

from upsales import Upsales
from upsales.models.client_categories import ClientCategory
from upsales.models.roles import PartialRole

# Configure VCR for this test module
my_vcr = vcr.VCR(
    cassette_library_dir="tests/cassettes/integration",
    record_mode="once",  # Record once, then always replay
    match_on=["method", "scheme", "host", "port", "path", "query"],
    filter_headers=[("cookie", "REDACTED")],
    filter_post_data_parameters=[("password", "REDACTED")],
)


@pytest.mark.asyncio
@my_vcr.use_cassette(
    "test_client_categories_integration/test_get_client_category_real_response.yaml"
)
async def test_get_client_category_real_response():
    """
    Test getting client category with real API response structure.

    This test records the actual API response on first run, then
    replays it from cassette on future runs. Ensures our ClientCategory
    model correctly parses real Upsales API data.
    """
    async with Upsales.from_env() as upsales:
        # Get client categories to find a valid ID
        categories = await upsales.client_categories.list(limit=1)

        assert len(categories) > 0, "Should have at least one client category"
        category = categories[0]

        # Validate ClientCategory model with Pydantic v2 features
        assert isinstance(category, ClientCategory)
        assert isinstance(category.id, int)
        assert category.id > 0
        assert isinstance(category.name, str)
        assert len(category.name) > 0  # NonEmptyStr validator

        # Validate frozen fields (read-only)
        assert hasattr(category, "id")

        # Validate required fields
        assert isinstance(category.categoryType, int)
        assert isinstance(category.roles, list)

        # Validate computed fields work
        assert isinstance(category.has_roles, bool)
        assert isinstance(category.role_count, int)

        # Validate computed field correctness
        assert category.has_roles == (len(category.roles) > 0)
        assert category.role_count == len(category.roles)

        # Validate nested PartialRole objects if present
        if category.roles:
            for role in category.roles:
                assert isinstance(role, PartialRole)
                assert isinstance(role.id, int)
                assert isinstance(role.name, str)

        print(
            f"[OK] ClientCategory parsed successfully: {category.name} "
            f"(ID: {category.id}, Type: {category.categoryType}, Roles: {category.role_count})"
        )


@pytest.mark.asyncio
@my_vcr.use_cassette(
    "test_client_categories_integration/test_list_client_categories_real_response.yaml"
)
async def test_list_client_categories_real_response():
    """Test listing client categories with real API response structure."""
    async with Upsales.from_env() as upsales:
        categories = await upsales.client_categories.list(limit=10)

        assert isinstance(categories, list)
        assert len(categories) <= 10

        for category in categories:
            assert isinstance(category, ClientCategory)
            assert category.id > 0
            assert len(category.name) > 0
            # Required fields
            assert isinstance(category.categoryType, int)
            assert isinstance(category.roles, list)
            # Computed fields
            assert isinstance(category.has_roles, bool)
            assert isinstance(category.role_count, int)
            # Validate computed correctness
            assert category.role_count == len(category.roles)

        print(f"[OK] Listed {len(categories)} client categories successfully")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_client_categories_integration/test_client_category_serialization.yaml")
async def test_client_category_serialization_real_data():
    """
    Test to_api_dict() serialization with real client category data.

    Validates that serialization excludes frozen fields using
    Pydantic v2 optimized serialization.
    """
    async with Upsales.from_env() as upsales:
        categories = await upsales.client_categories.list(limit=1)
        category = categories[0]

        # Get API dict (should exclude frozen fields)
        api_dict = category.to_api_dict()

        # Validate frozen fields excluded
        assert "id" not in api_dict or api_dict.get("id") is None

        # Validate computed fields excluded
        assert "has_roles" not in api_dict
        assert "role_count" not in api_dict

        # Should include updatable fields
        assert "name" in api_dict
        assert "categoryType" in api_dict

        # With overrides, should include changed fields
        api_dict_with_changes = category.to_api_dict(name="New Category Name", categoryType=1)
        assert api_dict_with_changes["name"] == "New Category Name"
        assert api_dict_with_changes["categoryType"] == 1

        # Validate it's JSON serializable
        import json

        json_str = json.dumps(api_dict)  # Should not raise
        assert json_str

        print(f"[OK] Serialization validated for {category.name}")
        print(f"[OK] API payload has {len(api_dict)} fields")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_client_categories_integration/test_get_by_name.yaml")
async def test_get_by_name():
    """
    Test get_by_name() custom method with real data.

    Validates that custom methods work correctly with the client_categories endpoint.
    """
    async with Upsales.from_env() as upsales:
        # Get all categories first to find a valid name
        all_categories = await upsales.client_categories.list_all()

        if all_categories:
            # Use the first category's name to test
            test_name = all_categories[0].name

            # Get category by name
            found_category = await upsales.client_categories.get_by_name(test_name)

            assert found_category is not None
            assert isinstance(found_category, ClientCategory)
            assert found_category.name.lower() == test_name.lower()

            print(f"[OK] Found category by name: {found_category.name} (ID: {found_category.id})")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_client_categories_integration/test_get_with_roles.yaml")
async def test_get_with_roles():
    """
    Test get_with_roles() custom method with real data.

    Validates that categories with roles are correctly filtered.
    """
    async with Upsales.from_env() as upsales:
        # Get categories that have roles assigned
        categories_with_roles = await upsales.client_categories.get_with_roles()

        assert isinstance(categories_with_roles, list)
        # All should have roles
        for category in categories_with_roles:
            assert category.has_roles is True
            assert category.role_count > 0
            assert len(category.roles) > 0

        print(f"[OK] Found {len(categories_with_roles)} categories with roles")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_client_categories_integration/test_get_by_type.yaml")
async def test_get_by_type():
    """
    Test get_by_type() custom method with real data.

    Validates that categories can be filtered by type.
    """
    async with Upsales.from_env() as upsales:
        # Get all categories first to find what types exist
        all_categories = await upsales.client_categories.list_all()

        if all_categories:
            # Use the first category's type to test
            test_type = all_categories[0].categoryType

            # Get categories with that type
            type_categories = await upsales.client_categories.get_by_type(test_type)

            assert isinstance(type_categories, list)
            # All should have the test type
            for category in type_categories:
                assert category.categoryType == test_type

            print(f"[OK] Found {len(type_categories)} categories with type {test_type}")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_client_categories_integration/test_nested_partial_roles.yaml")
async def test_nested_partial_roles():
    """
    Test that nested PartialRole objects are correctly parsed.

    Validates the nested object relationship between ClientCategory and Role.
    """
    async with Upsales.from_env() as upsales:
        # Get categories with roles
        categories = await upsales.client_categories.get_with_roles()

        if categories:
            category = categories[0]

            # Should have roles
            assert len(category.roles) > 0
            assert category.has_roles is True

            # Each role should be a PartialRole
            for role in category.roles:
                assert isinstance(role, PartialRole)
                assert role.id > 0
                assert isinstance(role.name, str)
                assert len(role.name) > 0

                # Test that PartialRole can fetch full data
                # (We won't actually fetch to avoid excessive API calls in tests)
                assert hasattr(role, "fetch_full")
                assert hasattr(role, "edit")

            print(
                f"[OK] Nested PartialRole validation successful for {category.name} "
                f"({category.role_count} roles)"
            )
