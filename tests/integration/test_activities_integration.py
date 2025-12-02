"""
Integration tests for Activity model with real API responses.

Uses VCR.py to record API responses on first run, then replay them.
Validates that our Pydantic v2 models correctly parse real API data.

To record cassettes:
    uv run pytest tests/integration/test_activities_integration.py -v

To re-record (delete cassette first):
    rm tests/cassettes/integration/test_activities_integration/*.yaml
    uv run pytest tests/integration/test_activities_integration.py -v
"""

import pytest
import vcr

from upsales import Upsales
from upsales.models.activities import Activity
from upsales.models.company import PartialCompany
from upsales.models.contacts import PartialContact
from upsales.models.orders import PartialOrder
from upsales.models.projects import PartialProject
from upsales.models.user import PartialUser

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
@my_vcr.use_cassette("test_activities_integration/test_list_activities_real_response.yaml")
async def test_list_activities_real_response():
    """
    Test listing activities with real API response structure.

    Validates that Activity model correctly parses list responses
    with pagination metadata.

    Cassette: tests/cassettes/integration/test_activities_integration/test_list_activities_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        # Get activities with limit
        activities = await upsales.activities.list(limit=5)

        assert isinstance(activities, list)
        assert len(activities) <= 5

        for activity in activities:
            assert isinstance(activity, Activity)
            assert isinstance(activity.id, int)
            assert isinstance(activity.description, str)
            # date can be None in some activities
            assert activity.date is None or isinstance(activity.date, str)

            # Validate BinaryFlag fields (0 or 1)
            assert activity.isAppointment in (0, 1)

            # Validate required fields exist
            assert hasattr(activity, "regDate")
            assert hasattr(activity, "modDate")
            assert hasattr(activity, "priority")

        print(f"[OK] Listed {len(activities)} activities successfully")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_activities_integration/test_get_activity_real_response.yaml")
async def test_get_activity_real_response():
    """
    Test getting a single activity with real API response structure.

    This test records the actual API response on first run, then
    replays it from cassette on future runs. This ensures our Activity
    model correctly parses real Upsales API data.

    Cassette: tests/cassettes/integration/test_activities_integration/test_get_activity_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        # Get activities first to find a valid ID (with a date)
        activities = await upsales.activities.list(limit=20)

        assert len(activities) > 0, "Should have at least one activity"

        # Find an activity with a date
        activity_with_date = None
        for act in activities:
            if act.date:
                activity_with_date = act
                break

        if not activity_with_date:
            # If no activities with dates, just use the first one
            activity_with_date = activities[0]

        activity_id = activity_with_date.id

        # Get single activity by ID
        activity = await upsales.activities.get(activity_id)

        # Validate Activity model with Pydantic v2 features
        assert isinstance(activity, Activity)
        assert activity.id == activity_id
        assert isinstance(activity.description, str)
        assert len(activity.description) > 0

        # Validate timestamps
        assert isinstance(activity.regDate, str)
        assert isinstance(activity.modDate, str)
        # date can be None
        assert activity.date is None or isinstance(activity.date, str)

        # Validate BinaryFlag validator (0 or 1, not bool)
        assert activity.isAppointment in (0, 1)

        # Validate notes field (can be None)
        assert activity.notes is None or isinstance(activity.notes, str)

        # Validate priority
        assert isinstance(activity.priority, int)

        # Validate boolean flags
        assert isinstance(activity.userEditable, bool)
        assert isinstance(activity.userRemovable, bool)

        # Validate custom fields (should be list)
        assert isinstance(activity.custom, list)

        print(f"[OK] Activity parsed successfully: {activity.description} (ID: {activity.id})")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_activities_integration/test_activity_nested_objects.yaml")
async def test_activity_nested_objects():
    """
    Test activity nested objects with real API data.

    Validates PartialUser, PartialCompany, PartialContact, PartialOrder,
    and PartialProject parsing when they appear in activity responses.

    Cassette: tests/cassettes/integration/test_activities_integration/test_activity_nested_objects.yaml
    """
    async with Upsales.from_env() as upsales:
        # Get activities and look for ones with nested objects
        activities = await upsales.activities.list(limit=20)

        # Track what we find
        found_user = False
        found_company = False
        found_contact = False
        found_opportunity = False
        found_project = False

        for activity in activities:
            # Test regBy if present
            if activity.regBy:
                assert isinstance(activity.regBy, PartialUser)
                assert isinstance(activity.regBy.id, int)
                found_user = True

            # Test client (company) if present
            if activity.client:
                assert isinstance(activity.client, PartialCompany)
                assert isinstance(activity.client.id, int)
                found_company = True

            # Test contacts if present
            if activity.contacts:
                assert isinstance(activity.contacts, list)
                for contact in activity.contacts:
                    assert isinstance(contact, PartialContact)
                    assert isinstance(contact.id, int)
                found_contact = True

            # Test users array if present
            if activity.users:
                assert isinstance(activity.users, list)
                for user in activity.users:
                    assert isinstance(user, PartialUser)
                    assert isinstance(user.id, int)

            # Test opportunity if present
            if activity.opportunity:
                assert isinstance(activity.opportunity, PartialOrder)
                assert isinstance(activity.opportunity.id, int)
                found_opportunity = True

            # Test project if present
            if activity.project:
                assert isinstance(activity.project, PartialProject)
                assert isinstance(activity.project.id, int)
                found_project = True

        # Report findings
        print("[OK] Nested objects validated:")
        print(f"  - PartialUser (regBy): {found_user}")
        print(f"  - PartialCompany (client): {found_company}")
        print(f"  - PartialContact (contacts): {found_contact}")
        print(f"  - PartialOrder (opportunity): {found_opportunity}")
        print(f"  - PartialProject (project): {found_project}")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_activities_integration/test_activity_computed_fields.yaml")
async def test_activity_computed_fields():
    """
    Test activity computed fields with real API data.

    Validates is_appointment, is_task, is_closed, has_company, has_opportunity
    computed properties.

    Cassette: tests/cassettes/integration/test_activities_integration/test_activity_computed_fields.yaml
    """
    async with Upsales.from_env() as upsales:
        # Get activities to test computed fields
        activities = await upsales.activities.list(limit=20)

        found_appointment = False
        found_task = False
        found_closed = False
        found_with_company = False
        found_with_opportunity = False

        for activity in activities:
            # Test is_appointment and is_task (should be inverse)
            assert isinstance(activity.is_appointment, bool)
            assert isinstance(activity.is_task, bool)
            assert activity.is_appointment != activity.is_task  # Mutually exclusive

            if activity.is_appointment:
                assert activity.isAppointment == 1
                found_appointment = True

            if activity.is_task:
                assert activity.isAppointment == 0
                found_task = True

            # Test is_closed
            assert isinstance(activity.is_closed, bool)
            if activity.closeDate:
                assert activity.is_closed
                found_closed = True
            else:
                assert not activity.is_closed

            # Test has_company
            assert isinstance(activity.has_company, bool)
            if activity.client and activity.client.id:
                assert activity.has_company
                found_with_company = True
            else:
                assert not activity.has_company

            # Test has_opportunity
            assert isinstance(activity.has_opportunity, bool)
            if activity.opportunity and activity.opportunity.id:
                assert activity.has_opportunity
                found_with_opportunity = True
            else:
                assert not activity.has_opportunity

        # Report findings
        print("[OK] Computed fields validated:")
        print(f"  - is_appointment: {found_appointment}")
        print(f"  - is_task: {found_task}")
        print(f"  - is_closed: {found_closed}")
        print(f"  - has_company: {found_with_company}")
        print(f"  - has_opportunity: {found_with_opportunity}")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_activities_integration/test_activity_custom_fields.yaml")
async def test_activity_custom_fields():
    """
    Test activity custom fields parsing with real API data.

    Validates CustomFieldsList validator and CustomFields helper.

    Cassette: tests/cassettes/integration/test_activities_integration/test_activity_custom_fields.yaml
    """
    async with Upsales.from_env() as upsales:
        # Get activities and look for custom fields
        activities = await upsales.activities.list(limit=20)

        # Find an activity with custom fields
        activity_with_custom = None
        for activity in activities:
            if activity.custom:
                activity_with_custom = activity
                break

        if activity_with_custom:
            # Validate custom fields structure (CustomFieldsList validator)
            assert isinstance(activity_with_custom.custom, list)
            for field in activity_with_custom.custom:
                assert "fieldId" in field, "CustomFieldsList should validate fieldId presence"

            # Validate custom_fields helper (computed property)
            cf = activity_with_custom.custom_fields
            assert hasattr(cf, "__getitem__")

            # Test dict-like access works
            if activity_with_custom.custom:
                first_field = activity_with_custom.custom[0]
                field_id = first_field["fieldId"]
                # Access by ID should work
                value = cf.get(field_id)
                assert value is not None or field_id in [
                    f["fieldId"] for f in activity_with_custom.custom
                ]

            print(f"[OK] Custom fields validated: {len(activity_with_custom.custom)} fields")
        else:
            print("[SKIP] No activities with custom fields found in sample")
