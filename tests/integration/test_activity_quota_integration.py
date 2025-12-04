"""
Integration tests for ActivityQuota model with real API responses.

Uses VCR.py to record API responses on first run, then replay them.
Validates that our Pydantic v2 models correctly parse real API data.

To record cassettes:
    uv run pytest tests/integration/test_activity_quota_integration.py -v

To re-record (delete cassette first):
    rm tests/cassettes/integration/test_activity_quota_integration/*.yaml
    uv run pytest tests/integration/test_activity_quota_integration.py -v
"""

import pytest
import vcr

from upsales import Upsales
from upsales.models.activity_quota import ActivityQuota
from upsales.models.activity_types import PartialActivityType
from upsales.models.user import PartialUser

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
@my_vcr.use_cassette("test_activity_quota_integration/test_list_activity_quotas_real_response.yaml")
async def test_list_activity_quotas_real_response():
    """
    Test listing activity quotas with real API response structure.

    Validates that ActivityQuota model correctly parses list responses.
    May return empty list if no quotas are configured.

    Cassette: tests/cassettes/integration/test_activity_quota_integration/test_list_activity_quotas_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        # Get activity quotas with limit
        quotas = await upsales.activity_quota.list(limit=5)

        assert isinstance(quotas, list)
        assert len(quotas) <= 5

        if not quotas:
            pytest.skip("No activity quotas found in system")

        for quota in quotas:
            assert isinstance(quota, ActivityQuota)
            assert isinstance(quota.id, int)

            # Validate required fields
            assert isinstance(quota.year, int)
            assert isinstance(quota.month, int)
            assert 1 <= quota.month <= 12, f"Month should be 1-12, got {quota.month}"

            # Validate user nested object
            assert isinstance(quota.user, PartialUser)
            assert isinstance(quota.user.id, int)

            # Validate activityType nested object
            assert isinstance(quota.activityType, PartialActivityType)
            assert isinstance(quota.activityType.id, int)

            # Validate optional numeric fields
            assert isinstance(quota.performed, int)
            assert isinstance(quota.created, int)
            assert quota.performed >= 0
            assert quota.created >= 0

            # Validate date field (read-only, may be None)
            assert quota.date is None or isinstance(quota.date, str)

        print(f"[OK] Listed {len(quotas)} activity quotas successfully")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_activity_quota_integration/test_get_activity_quota_real_response.yaml")
async def test_get_activity_quota_real_response():
    """
    Test getting a single activity quota with real API response structure.

    NOTE: The /activityQuota/:id GET endpoint is not implemented by the API.
    This test validates detailed parsing of a quota from the list response.

    Cassette: tests/cassettes/integration/test_activity_quota_integration/test_get_activity_quota_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        # Get quotas (API doesn't support GET by ID)
        quotas = await upsales.activity_quota.list(limit=5)

        if not quotas:
            pytest.skip("No activity quotas found in system")

        # Use first quota for detailed validation
        quota = quotas[0]

        # Validate ActivityQuota model with Pydantic v2 features
        assert isinstance(quota, ActivityQuota)
        assert isinstance(quota.id, int)

        # Validate required fields
        assert isinstance(quota.year, int)
        assert quota.year >= 2000  # Reasonable year validation

        assert isinstance(quota.month, int)
        assert 1 <= quota.month <= 12, f"Month should be 1-12, got {quota.month}"

        # Validate nested objects
        assert isinstance(quota.user, PartialUser)
        assert isinstance(quota.user.id, int)

        assert isinstance(quota.activityType, PartialActivityType)
        assert isinstance(quota.activityType.id, int)

        # Validate optional numeric fields
        assert isinstance(quota.performed, int)
        assert isinstance(quota.created, int)
        assert quota.performed >= 0
        assert quota.created >= 0

        # Validate read-only date field
        assert quota.date is None or isinstance(quota.date, str)
        if quota.date:
            # Basic date format validation (YYYY-MM-DD)
            assert len(quota.date) == 10
            assert quota.date[4] == "-"
            assert quota.date[7] == "-"

        print(
            f"[OK] Activity quota parsed successfully: Year={quota.year}, "
            f"Month={quota.month}, Performed={quota.performed}, Created={quota.created} (ID: {quota.id})"
        )


@pytest.mark.asyncio
@my_vcr.use_cassette("test_activity_quota_integration/test_activity_quota_nested_objects.yaml")
async def test_activity_quota_nested_objects():
    """
    Test activity quota nested objects with real API data.

    Validates PartialUser and PartialActivityType parsing when they
    appear in activity quota responses.

    Cassette: tests/cassettes/integration/test_activity_quota_integration/test_activity_quota_nested_objects.yaml
    """
    async with Upsales.from_env() as upsales:
        # Get activity quotas
        quotas = await upsales.activity_quota.list(limit=10)

        if not quotas:
            pytest.skip("No activity quotas found in system")

        # All quotas should have user and activityType
        for quota in quotas:
            # Validate user nested object (required)
            assert quota.user is not None, "User should always be present"
            assert isinstance(quota.user, PartialUser)
            assert isinstance(quota.user.id, int)
            assert quota.user.id > 0

            # Validate activityType nested object (required)
            assert quota.activityType is not None, "ActivityType should always be present"
            assert isinstance(quota.activityType, PartialActivityType)
            assert isinstance(quota.activityType.id, int)
            assert quota.activityType.id > 0

        print("[OK] Nested objects validated:")
        print(f"  - PartialUser (user): {len(quotas)} quotas")
        print(f"  - PartialActivityType (activityType): {len(quotas)} quotas")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_activity_quota_integration/test_activity_quota_validation.yaml")
async def test_activity_quota_validation():
    """
    Test activity quota field validation with real API data.

    Validates month range (1-12) and numeric field constraints.

    Cassette: tests/cassettes/integration/test_activity_quota_integration/test_activity_quota_validation.yaml
    """
    async with Upsales.from_env() as upsales:
        # Get activity quotas
        quotas = await upsales.activity_quota.list(limit=10)

        if not quotas:
            pytest.skip("No activity quotas found in system")

        for quota in quotas:
            # Validate month is in valid range
            assert 1 <= quota.month <= 12, f"Month should be 1-12, got {quota.month}"

            # Validate year is reasonable
            assert 2000 <= quota.year <= 2100, f"Year should be reasonable, got {quota.year}"

            # Validate numeric fields are non-negative
            assert quota.performed >= 0, f"Performed should be >= 0, got {quota.performed}"
            assert quota.created >= 0, f"Created should be >= 0, got {quota.created}"

            # Validate frozen fields are present
            assert hasattr(quota, "id")
            assert hasattr(quota, "date")

        print(f"[OK] Validation passed for {len(quotas)} quotas:")
        print("  - Month range: 1-12")
        print("  - Year range: 2000-2100")
        print("  - Numeric fields: >= 0")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_activity_quota_integration/test_activity_quota_list_all_pagination.yaml")
async def test_activity_quota_list_all_pagination():
    """
    Test activity quota list_all with pagination.

    Validates that list_all() correctly handles pagination and
    returns all available quotas.

    Cassette: tests/cassettes/integration/test_activity_quota_integration/test_activity_quota_list_all_pagination.yaml
    """
    async with Upsales.from_env() as upsales:
        # Get all activity quotas using list_all
        all_quotas = await upsales.activity_quota.list_all()

        assert isinstance(all_quotas, list)

        if not all_quotas:
            pytest.skip("No activity quotas found in system")

        # Validate all items are ActivityQuota instances
        for quota in all_quotas:
            assert isinstance(quota, ActivityQuota)
            assert isinstance(quota.id, int)
            assert isinstance(quota.year, int)
            assert isinstance(quota.month, int)

        print(f"[OK] list_all() returned {len(all_quotas)} quotas")
