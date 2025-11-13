"""
Integration tests for SalesCoach model with real API responses.

Uses VCR.py to record API responses on first run, then replay.
Validates that SalesCoach model correctly parses real Upsales API data.

To record cassettes:
    uv run pytest tests/integration/test_sales_coaches_integration.py -v
"""

import pytest
import vcr

from upsales import Upsales
from upsales.models.sales_coaches import SalesCoach

# Configure VCR for this test module
my_vcr = vcr.VCR(
    cassette_library_dir="tests/cassettes/integration",
    record_mode="once",  # Record once, then always replay
    match_on=["method", "scheme", "host", "port", "path", "query"],
    filter_headers=[("cookie", "REDACTED")],
    filter_post_data_parameters=[("password", "REDACTED")],
)


@pytest.mark.asyncio
@my_vcr.use_cassette("test_sales_coaches_integration/test_get_coach_real_response.yaml")
async def test_get_coach_real_response():
    """
    Test getting sales coach with real API response structure.

    This test records the actual API response on first run, then
    replays it from cassette on future runs. Ensures our SalesCoach
    model correctly parses real Upsales API data.
    """
    async with Upsales.from_env() as upsales:
        # Get coaches to find a valid ID
        coaches = await upsales.sales_coaches.list(limit=1)

        assert len(coaches) > 0, "Should have at least one sales coach"
        coach = coaches[0]

        # Validate SalesCoach model with Pydantic v2 features
        assert isinstance(coach, SalesCoach)
        assert isinstance(coach.id, int)
        assert coach.id > 0
        assert isinstance(coach.name, str)
        assert len(coach.name) > 0  # NonEmptyStr validator

        # Validate frozen fields (read-only)
        assert hasattr(coach, "id")
        assert hasattr(coach, "regBy")
        assert hasattr(coach, "regDate")
        assert hasattr(coach, "modBy")

        # Validate required boolean fields
        assert isinstance(coach.active, bool)
        assert isinstance(coach.budgetActive, bool)
        assert isinstance(coach.decisionMakersActive, bool)
        assert isinstance(coach.solutionActive, bool)
        assert isinstance(coach.timeframeActive, bool)
        assert isinstance(coach.nextStepActive, bool)
        assert isinstance(coach.nextStepOnlyAppointments, bool)

        # Validate list fields
        assert isinstance(coach.budgetStages, list)
        assert isinstance(coach.decisionMakersStages, list)
        assert isinstance(coach.solutionStages, list)
        assert isinstance(coach.timeframeStages, list)
        assert isinstance(coach.users, list)
        assert isinstance(coach.roles, list)

        print(
            f"[OK] SalesCoach parsed successfully: {coach.name} "
            f"(ID: {coach.id}, Active: {coach.active})"
        )


@pytest.mark.asyncio
@my_vcr.use_cassette("test_sales_coaches_integration/test_list_coaches_real_response.yaml")
async def test_list_coaches_real_response():
    """Test listing sales coaches with real API response structure."""
    async with Upsales.from_env() as upsales:
        coaches = await upsales.sales_coaches.list(limit=10)

        assert isinstance(coaches, list)
        assert len(coaches) <= 10

        for coach in coaches:
            assert isinstance(coach, SalesCoach)
            assert coach.id > 0
            assert len(coach.name) > 0
            # Required boolean fields
            assert isinstance(coach.active, bool)
            assert isinstance(coach.budgetActive, bool)
            assert isinstance(coach.decisionMakersActive, bool)
            assert isinstance(coach.solutionActive, bool)
            assert isinstance(coach.timeframeActive, bool)
            # List fields
            assert isinstance(coach.users, list)
            assert isinstance(coach.roles, list)

        print(f"[OK] Listed {len(coaches)} sales coaches successfully")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_sales_coaches_integration/test_coach_serialization.yaml")
async def test_coach_serialization_real_data():
    """
    Test to_api_dict() serialization with real sales coach data.

    Validates that serialization excludes frozen fields using
    Pydantic v2 optimized serialization.
    """
    async with Upsales.from_env() as upsales:
        coaches = await upsales.sales_coaches.list(limit=1)
        coach = coaches[0]

        # Get API dict (should exclude frozen fields)
        api_dict = coach.to_api_dict()

        # Validate frozen fields excluded
        assert "id" not in api_dict or api_dict.get("id") is None
        assert "regBy" not in api_dict or api_dict.get("regBy") is None
        assert "regDate" not in api_dict or api_dict.get("regDate") is None
        assert "modBy" not in api_dict or api_dict.get("modBy") is None
        assert "modDate" not in api_dict or api_dict.get("modDate") is None

        # Should include updatable fields
        assert "name" in api_dict
        assert "active" in api_dict
        assert "budgetActive" in api_dict
        assert "decisionMakersActive" in api_dict
        assert "solutionActive" in api_dict
        assert "timeframeActive" in api_dict

        # With overrides, should include changed fields
        api_dict_with_changes = coach.to_api_dict(name="New Coach Name", active=False)
        assert api_dict_with_changes["name"] == "New Coach Name"
        assert api_dict_with_changes["active"] is False

        # Validate it's JSON serializable
        import json

        json_str = json.dumps(api_dict)  # Should not raise
        assert json_str

        print(f"[OK] Serialization validated for {coach.name}")
        print(f"[OK] API payload has {len(api_dict)} fields")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_sales_coaches_integration/test_list_active.yaml")
async def test_list_active():
    """
    Test list_active() custom method with real data.

    Validates that only active coaches are returned.
    """
    async with Upsales.from_env() as upsales:
        # Get active coaches
        active_coaches = await upsales.sales_coaches.list_active()

        assert isinstance(active_coaches, list)
        # All should have active=True
        for coach in active_coaches:
            assert coach.active is True

        print(f"[OK] Found {len(active_coaches)} active sales coaches")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_sales_coaches_integration/test_list_with_budget_tracking.yaml")
async def test_list_with_budget_tracking():
    """
    Test list_with_budget_tracking() custom method with real data.

    Validates that coaches with budget tracking enabled are returned.
    """
    async with Upsales.from_env() as upsales:
        # Get coaches with budget tracking
        budget_coaches = await upsales.sales_coaches.list_with_budget_tracking()

        assert isinstance(budget_coaches, list)
        # All should have budgetActive=True
        for coach in budget_coaches:
            assert coach.budgetActive is True

        print(f"[OK] Found {len(budget_coaches)} coaches with budget tracking")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_sales_coaches_integration/test_list_with_decision_maker_tracking.yaml")
async def test_list_with_decision_maker_tracking():
    """
    Test list_with_decision_maker_tracking() custom method with real data.

    Validates that coaches with decision maker tracking enabled are returned.
    """
    async with Upsales.from_env() as upsales:
        # Get coaches with decision maker tracking
        dm_coaches = await upsales.sales_coaches.list_with_decision_maker_tracking()

        assert isinstance(dm_coaches, list)
        # All should have decisionMakersActive=True
        for coach in dm_coaches:
            assert coach.decisionMakersActive is True

        print(f"[OK] Found {len(dm_coaches)} coaches with decision maker tracking")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_sales_coaches_integration/test_list_with_full_bant.yaml")
async def test_list_with_full_bant():
    """
    Test list_with_full_bant() custom method with real data.

    Validates that coaches with all BANT dimensions enabled are returned.
    """
    async with Upsales.from_env() as upsales:
        # Get coaches with full BANT
        full_bant_coaches = await upsales.sales_coaches.list_with_full_bant()

        assert isinstance(full_bant_coaches, list)
        # All should have all BANT dimensions enabled
        for coach in full_bant_coaches:
            assert coach.budgetActive is True
            assert coach.decisionMakersActive is True
            assert coach.solutionActive is True
            assert coach.timeframeActive is True

        print(f"[OK] Found {len(full_bant_coaches)} coaches with full BANT methodology")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_sales_coaches_integration/test_get_by_name.yaml")
async def test_get_by_name():
    """
    Test get_by_name() custom method with real data.

    Validates that coaches can be retrieved by name.
    """
    async with Upsales.from_env() as upsales:
        # Get all coaches first to find an existing name
        all_coaches = await upsales.sales_coaches.list_all()

        if all_coaches:
            # Use the first coach's name to test
            test_name = all_coaches[0].name

            # Get coach by name
            coach = await upsales.sales_coaches.get_by_name(test_name)

            assert coach is not None
            assert isinstance(coach, SalesCoach)
            assert coach.name.lower() == test_name.lower()

            print(f"[OK] Found coach by name: {coach.name}")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_sales_coaches_integration/test_list_assigned_to_user.yaml")
async def test_list_assigned_to_user():
    """
    Test list_assigned_to_user() custom method with real data.

    Validates that coaches assigned to a specific user can be retrieved.
    """
    async with Upsales.from_env() as upsales:
        # Get all coaches first to find a user ID
        all_coaches = await upsales.sales_coaches.list_all()

        # Find a coach with users assigned
        test_user_id = None
        for coach in all_coaches:
            if coach.users:
                test_user_id = coach.users[0]
                break

        if test_user_id:
            # Get coaches for that user
            user_coaches = await upsales.sales_coaches.list_assigned_to_user(test_user_id)

            assert isinstance(user_coaches, list)
            # All should have the test user ID
            for coach in user_coaches:
                assert test_user_id in coach.users

            print(f"[OK] Found {len(user_coaches)} coaches for user {test_user_id}")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_sales_coaches_integration/test_list_assigned_to_role.yaml")
async def test_list_assigned_to_role():
    """
    Test list_assigned_to_role() custom method with real data.

    Validates that coaches assigned to a specific role can be retrieved.
    """
    async with Upsales.from_env() as upsales:
        # Get all coaches first to find a role ID
        all_coaches = await upsales.sales_coaches.list_all()

        # Find a coach with roles assigned
        test_role_id = None
        for coach in all_coaches:
            if coach.roles:
                test_role_id = coach.roles[0]
                break

        if test_role_id:
            # Get coaches for that role
            role_coaches = await upsales.sales_coaches.list_assigned_to_role(test_role_id)

            assert isinstance(role_coaches, list)
            # All should have the test role ID
            for coach in role_coaches:
                assert test_role_id in coach.roles

            print(f"[OK] Found {len(role_coaches)} coaches for role {test_role_id}")
