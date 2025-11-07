"""
Integration tests for User model with real API responses.

Uses VCR.py to record API responses on first run, then replay them.
Validates that our Pydantic v2 models correctly parse real API data.

To record cassettes:
    uv run pytest tests/integration/test_users_integration.py -v

To re-record (delete cassette first):
    rm tests/cassettes/integration/test_users_integration/*.yaml
    uv run pytest tests/integration/test_users_integration.py -v
"""

import pytest
import vcr

from upsales import Upsales
from upsales.models.user import User

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
@my_vcr.use_cassette("test_users_integration/test_get_user_real_response.yaml")
async def test_get_user_real_response():
    """
    Test getting a user with real API response structure.

    This test records the actual API response on first run, then
    replays it from cassette on future runs. This ensures our User
    model correctly parses real Upsales API data.

    Cassette: tests/cassettes/integration/test_users_integration/test_get_user_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        # Get a real user (or replay from cassette)
        users = await upsales.users.list(limit=1)

        assert len(users) > 0, "Should have at least one user"
        user = users[0]

        # Validate User model with Pydantic v2 features
        assert isinstance(user, User)
        assert isinstance(user.id, int)
        assert isinstance(user.name, str)
        assert isinstance(user.email, str)
        assert user.email == user.email.lower()  # EmailStr normalizes to lowercase

        # Validate BinaryFlag fields (0 or 1)
        assert user.active in (0, 1)
        assert user.administrator in (0, 1)
        assert user.billingAdmin in (0, 1)

        # Validate computed fields
        assert isinstance(user.is_active, bool)
        assert isinstance(user.is_admin, bool)
        assert isinstance(user.display_name, str)

        # Validate custom_fields property
        assert hasattr(user, "custom_fields")

        print(f"[OK] User parsed successfully: {user.name} (ID: {user.id})")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_users_integration/test_list_users_real_response.yaml")
async def test_list_users_real_response():
    """
    Test listing users with real API response structure.

    Validates pagination metadata and multiple user objects.

    Cassette: tests/cassettes/integration/test_users_integration/test_list_users_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        # Get users with limit
        users = await upsales.users.list(limit=5)

        assert isinstance(users, list)
        assert len(users) <= 5

        for user in users:
            assert isinstance(user, User)
            assert user.id > 0
            assert len(user.name) > 0
            assert "@" in user.email  # Email validation

        print(f"[OK] Listed {len(users)} users successfully")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_users_integration/test_user_computed_fields_with_real_data.yaml")
async def test_user_computed_fields_with_real_data():
    """
    Test computed fields work correctly with real API data.

    Validates all computed properties return expected types and values.

    Cassette: tests/cassettes/integration/test_users_integration/test_user_computed_fields_with_real_data.yaml
    """
    async with Upsales.from_env() as upsales:
        users = await upsales.users.list(limit=1)
        user = users[0]

        # Test computed fields
        assert isinstance(user.is_active, bool)
        assert user.is_active == (user.active == 1)

        assert isinstance(user.is_admin, bool)
        assert user.is_admin == (user.administrator == 1)

        assert isinstance(user.display_name, str)
        if user.is_admin:
            assert "[ADMIN]" in user.display_name
        else:
            assert "[ADMIN]" not in user.display_name

        print(f"[OK] Computed fields work: {user.display_name}")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_users_integration/test_user_custom_fields_with_real_data.yaml")
async def test_user_custom_fields_with_real_data():
    """
    Test custom fields parsing with real API data.

    Validates CustomFieldsList validator and CustomFields helper.

    Cassette: tests/cassettes/integration/test_users_integration/test_user_custom_fields_with_real_data.yaml
    """
    async with Upsales.from_env() as upsales:
        users = await upsales.users.list(limit=10)

        # Find a user with custom fields
        user_with_custom = None
        for user in users:
            if user.custom:
                user_with_custom = user
                break

        if user_with_custom:
            # Validate custom fields structure (CustomFieldsList validator)
            assert isinstance(user_with_custom.custom, list)
            for field in user_with_custom.custom:
                assert "fieldId" in field, "CustomFieldsList should validate fieldId presence"

            # Validate custom_fields helper
            cf = user_with_custom.custom_fields
            assert hasattr(cf, "__getitem__")

            print(f"[OK] Custom fields validated: {len(user_with_custom.custom)} fields")
        else:
            print("[SKIP] No users with custom fields found")
