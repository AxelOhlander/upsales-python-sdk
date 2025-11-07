"""
Integration tests for Role model with real API responses.

Uses VCR.py to record API responses on first run, then replay.
Validates that Role model correctly parses real Upsales API data.

To record cassettes:
    uv run pytest tests/integration/test_roles_integration.py -v
"""

import pytest
import vcr

from upsales import Upsales
from upsales.models.roles import Role

# Configure VCR for this test module
my_vcr = vcr.VCR(
    cassette_library_dir="tests/cassettes/integration",
    record_mode="once",  # Record once, then always replay
    match_on=["method", "scheme", "host", "port", "path", "query"],
    filter_headers=[("cookie", "REDACTED")],
    filter_post_data_parameters=[("password", "REDACTED")],
)


@pytest.mark.asyncio
@my_vcr.use_cassette("test_roles_integration/test_get_role_real_response.yaml")
async def test_get_role_real_response():
    """
    Test getting role with real API response structure.

    This test records the actual API response on first run, then
    replays it from cassette on future runs. Ensures our Role
    model correctly parses real Upsales API data.
    """
    async with Upsales.from_env() as upsales:
        # Get roles to find a valid ID
        roles = await upsales.roles.list(limit=1)

        assert len(roles) > 0, "Should have at least one role"
        role = roles[0]

        # Validate Role model with Pydantic v2 features
        assert isinstance(role, Role)
        assert isinstance(role.id, int)
        assert role.id > 0
        assert isinstance(role.name, str)
        assert len(role.name) > 0  # NonEmptyStr validator

        # Validate frozen fields (read-only)
        assert hasattr(role, "id")

        # Validate required fields
        assert isinstance(role.defaultCurrency, str)
        assert isinstance(role.template, int)
        assert isinstance(role.hasDiscount, bool)

        # Validate computed fields work
        assert isinstance(role.can_discount, bool)
        assert isinstance(role.has_parent, bool)

        # Validate computed field correctness
        assert role.can_discount == role.hasDiscount
        assert role.has_parent == (role.parent is not None and bool(role.parent))

        print(
            f"[OK] Role parsed successfully: {role.name} "
            f"(ID: {role.id}, Can discount: {role.can_discount})"
        )


@pytest.mark.asyncio
@my_vcr.use_cassette("test_roles_integration/test_list_roles_real_response.yaml")
async def test_list_roles_real_response():
    """Test listing roles with real API response structure."""
    async with Upsales.from_env() as upsales:
        roles = await upsales.roles.list(limit=10)

        assert isinstance(roles, list)
        assert len(roles) <= 10

        for role in roles:
            assert isinstance(role, Role)
            assert role.id > 0
            assert len(role.name) > 0
            # Required fields
            assert isinstance(role.defaultCurrency, str)
            assert isinstance(role.template, int)
            assert isinstance(role.hasDiscount, bool)
            # Computed fields
            assert isinstance(role.can_discount, bool)
            assert isinstance(role.has_parent, bool)

        print(f"[OK] Listed {len(roles)} roles successfully")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_roles_integration/test_role_serialization.yaml")
async def test_role_serialization_real_data():
    """
    Test to_api_dict() serialization with real role data.

    Validates that serialization excludes frozen fields using
    Pydantic v2 optimized serialization.
    """
    async with Upsales.from_env() as upsales:
        roles = await upsales.roles.list(limit=1)
        role = roles[0]

        # Get API dict (should exclude frozen fields)
        api_dict = role.to_api_dict()

        # Validate frozen fields excluded
        assert "id" not in api_dict or api_dict.get("id") is None

        # Validate computed fields excluded
        assert "can_discount" not in api_dict
        assert "has_parent" not in api_dict

        # Should include updatable fields
        assert "name" in api_dict
        assert "defaultCurrency" in api_dict
        assert "template" in api_dict

        # With overrides, should include changed fields
        api_dict_with_changes = role.to_api_dict(name="New Role Name", hasDiscount=True)
        assert api_dict_with_changes["name"] == "New Role Name"
        assert api_dict_with_changes["hasDiscount"] is True

        # Validate it's JSON serializable
        import json

        json_str = json.dumps(api_dict)  # Should not raise
        assert json_str

        print(f"[OK] Serialization validated for {role.name}")
        print(f"[OK] API payload has {len(api_dict)} fields")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_roles_integration/test_get_with_discounts.yaml")
async def test_get_with_discounts():
    """
    Test get_with_discounts() custom method with real data.

    Validates that custom methods work correctly with the roles endpoint.
    """
    async with Upsales.from_env() as upsales:
        # Get roles that can apply discounts (hasDiscount=True)
        discount_roles = await upsales.roles.get_with_discounts()

        assert isinstance(discount_roles, list)
        # All should have hasDiscount=True
        for role in discount_roles:
            assert role.hasDiscount is True
            assert role.can_discount  # Computed field check

        print(f"[OK] Found {len(discount_roles)} roles with discount permission")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_roles_integration/test_get_by_currency.yaml")
async def test_get_by_currency():
    """
    Test get_by_currency() custom method with real data.

    Validates that roles can be filtered by currency.
    """
    async with Upsales.from_env() as upsales:
        # Get all roles first to find what currencies exist
        all_roles = await upsales.roles.list_all()

        if all_roles:
            # Use the first role's currency to test
            test_currency = all_roles[0].defaultCurrency

            # Get roles with that currency
            currency_roles = await upsales.roles.get_by_currency(test_currency)

            assert isinstance(currency_roles, list)
            # All should have the test currency
            for role in currency_roles:
                assert role.defaultCurrency == test_currency

            print(f"[OK] Found {len(currency_roles)} roles with currency {test_currency}")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_roles_integration/test_get_top_level.yaml")
async def test_get_top_level():
    """
    Test get_top_level() custom method with real data.

    Validates that top-level roles (without parent) are correctly filtered.
    """
    async with Upsales.from_env() as upsales:
        # Get top-level roles (no parent)
        top_level = await upsales.roles.get_top_level()

        assert isinstance(top_level, list)
        # All should have no parent or empty parent
        for role in top_level:
            assert not role.has_parent  # Computed field check

        print(f"[OK] Found {len(top_level)} top-level roles (no parent)")
