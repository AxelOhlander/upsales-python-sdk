"""
Integration tests for ActivityListItem model with real API responses.

Uses VCR.py to record API responses on first run, then replay them.
Validates that our Pydantic v2 models correctly parse real API data from
the /api/v2/search/activitylist endpoint.

Note: This is a read-only search endpoint that returns heterogeneous
activity items (tasks, appointments, emails). It does not support
create/update/delete operations.

To record cassettes:
    uv run pytest tests/integration/test_activity_list_integration.py -v

To re-record (delete cassette first):
    rm tests/cassettes/integration/test_activity_list_integration/*.yaml
    uv run pytest tests/integration/test_activity_list_integration.py -v
"""

import pytest
import vcr

from upsales import Upsales
from upsales.models.activity_list_item import ActivityListItem
from upsales.models.company import PartialCompany
from upsales.models.contacts import PartialContact
from upsales.models.orders import PartialOrder
from upsales.models.projects import PartialProject
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
@my_vcr.use_cassette("test_activity_list_integration/test_list_activity_list_real_response.yaml")
async def test_list_activity_list_real_response():
    """
    Test listing activity list items with real API response structure.

    Validates that ActivityListItem model correctly parses list responses
    from the /search/activitylist endpoint.

    Cassette: tests/cassettes/integration/test_activity_list_integration/test_list_activity_list_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        # Get activity list items with limit
        items = await upsales.activity_list.list(limit=10)

        assert isinstance(items, list)
        # Note: API may return more items than requested limit
        assert len(items) > 0

        for item in items:
            assert isinstance(item, ActivityListItem)
            assert isinstance(item.id, int)
            # date can be None
            assert item.date is None or isinstance(item.date, str)

            # Validate boolean flags
            assert isinstance(item.userEditable, bool)
            assert isinstance(item.userRemovable, bool)

            # Validate required fields exist
            assert hasattr(item, "modDate")
            assert hasattr(item, "users")
            assert hasattr(item, "contacts")
            assert hasattr(item, "custom")

        print(f"[OK] Listed {len(items)} activity list items successfully")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_activity_list_integration/test_activity_list_heterogeneous_types.yaml")
async def test_activity_list_heterogeneous_types():
    """
    Test activity list with different activity types (task, appointment, email).

    Validates that the model correctly handles heterogeneous data where
    different activity types have different field sets.

    Cassette: tests/cassettes/integration/test_activity_list_integration/test_activity_list_heterogeneous_types.yaml
    """
    async with Upsales.from_env() as upsales:
        # Get activity list items
        items = await upsales.activity_list.list(limit=50)

        # Track what types we find
        found_email = False
        found_appointment = False
        found_task = False

        for item in items:
            assert isinstance(item, ActivityListItem)

            # Email activities should have subject, to, from
            if item.subject:
                found_email = True
                assert isinstance(item.subject, str)
                # to and from_ may be None
                if item.to:
                    assert isinstance(item.to, str)
                if item.from_:
                    assert isinstance(item.from_, str)

            # Appointment activities should have isAppointment=True
            if item.isAppointment is True:
                found_appointment = True
                # Should have description field
                assert item.description is None or isinstance(item.description, str)

            # Task activities (not appointment, not email)
            if item.isAppointment is False and not item.subject:
                found_task = True
                # Should have description field
                assert item.description is None or isinstance(item.description, str)

        # Report findings
        print("[OK] Activity types validated:")
        print(f"  - Emails: {found_email}")
        print(f"  - Appointments: {found_appointment}")
        print(f"  - Tasks: {found_task}")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_activity_list_integration/test_activity_list_computed_fields.yaml")
async def test_activity_list_computed_fields():
    """
    Test activity list computed fields with real API data.

    Validates is_email, is_appointment, is_task, display_title, has_company,
    has_contacts, is_closed computed properties.

    Cassette: tests/cassettes/integration/test_activity_list_integration/test_activity_list_computed_fields.yaml
    """
    async with Upsales.from_env() as upsales:
        # Get activity list items to test computed fields
        items = await upsales.activity_list.list(limit=50)

        found_email = False
        found_appointment = False
        found_task = False
        found_closed = False
        found_with_company = False
        found_with_contacts = False

        for item in items:
            # Test is_email
            assert isinstance(item.is_email, bool)
            if item.subject:
                assert item.is_email
                found_email = True

            # Test is_appointment
            assert isinstance(item.is_appointment, bool)
            if item.isAppointment is True:
                assert item.is_appointment
                found_appointment = True

            # Test is_task
            assert isinstance(item.is_task, bool)
            if not item.is_email and not item.is_appointment:
                assert item.is_task
                found_task = True

            # Test display_title
            assert isinstance(item.display_title, str)
            if item.subject:
                assert item.display_title == item.subject
            elif item.description:
                assert item.display_title == item.description
            else:
                assert item.display_title == ""

            # Test is_closed
            assert isinstance(item.is_closed, bool)
            if item.closeDate:
                assert item.is_closed
                found_closed = True
            else:
                assert not item.is_closed

            # Test has_company
            assert isinstance(item.has_company, bool)
            if item.client and item.client.id:
                assert item.has_company
                found_with_company = True
            else:
                assert not item.has_company

            # Test has_contacts
            assert isinstance(item.has_contacts, bool)
            if item.contacts and len(item.contacts) > 0:
                assert item.has_contacts
                found_with_contacts = True
            else:
                assert not item.has_contacts

        # Report findings
        print("[OK] Computed fields validated:")
        print(f"  - is_email: {found_email}")
        print(f"  - is_appointment: {found_appointment}")
        print(f"  - is_task: {found_task}")
        print(f"  - is_closed: {found_closed}")
        print(f"  - has_company: {found_with_company}")
        print(f"  - has_contacts: {found_with_contacts}")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_activity_list_integration/test_activity_list_nested_objects.yaml")
async def test_activity_list_nested_objects():
    """
    Test activity list nested objects with real API data.

    Validates PartialUser, PartialCompany, PartialContact, PartialOrder,
    and PartialProject parsing when they appear in activity list responses.

    Cassette: tests/cassettes/integration/test_activity_list_integration/test_activity_list_nested_objects.yaml
    """
    async with Upsales.from_env() as upsales:
        # Get activity list items and look for nested objects
        items = await upsales.activity_list.list(limit=50)

        # Track what we find
        found_users = False
        found_company = False
        found_contacts = False
        found_opportunity = False
        found_project = False
        found_reg_by = False

        for item in items:
            # Test users array
            assert isinstance(item.users, list)
            if item.users:
                found_users = True
                for user in item.users:
                    assert isinstance(user, PartialUser)
                    assert isinstance(user.id, int)

            # Test client (company)
            if item.client:
                assert isinstance(item.client, PartialCompany)
                assert isinstance(item.client.id, int)
                found_company = True

            # Test contacts array
            assert isinstance(item.contacts, list)
            if item.contacts:
                found_contacts = True
                for contact in item.contacts:
                    assert isinstance(contact, PartialContact)
                    assert isinstance(contact.id, int)

            # Test opportunity (order)
            if item.opportunity:
                assert isinstance(item.opportunity, PartialOrder)
                assert isinstance(item.opportunity.id, int)
                found_opportunity = True

            # Test project
            if item.project:
                assert isinstance(item.project, PartialProject)
                assert isinstance(item.project.id, int)
                found_project = True

            # Test regBy
            if item.regBy:
                assert isinstance(item.regBy, PartialUser)
                assert isinstance(item.regBy.id, int)
                found_reg_by = True

        # Report findings
        print("[OK] Nested objects validated:")
        print(f"  - PartialUser (users): {found_users}")
        print(f"  - PartialCompany (client): {found_company}")
        print(f"  - PartialContact (contacts): {found_contacts}")
        print(f"  - PartialOrder (opportunity): {found_opportunity}")
        print(f"  - PartialProject (project): {found_project}")
        print(f"  - PartialUser (regBy): {found_reg_by}")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_activity_list_integration/test_activity_list_custom_fields.yaml")
async def test_activity_list_custom_fields():
    """
    Test activity list custom fields parsing with real API data.

    Validates CustomFieldsList validator and access patterns.

    Cassette: tests/cassettes/integration/test_activity_list_integration/test_activity_list_custom_fields.yaml
    """
    async with Upsales.from_env() as upsales:
        # Get activity list items and look for custom fields
        items = await upsales.activity_list.list(limit=50)

        # Find an item with custom fields
        item_with_custom = None
        for item in items:
            if item.custom:
                item_with_custom = item
                break

        if item_with_custom:
            # Validate custom fields structure (CustomFieldsList validator)
            assert isinstance(item_with_custom.custom, list)
            for field in item_with_custom.custom:
                assert "fieldId" in field, "CustomFieldsList should validate fieldId presence"

            print(f"[OK] Custom fields validated: {len(item_with_custom.custom)} fields")
        else:
            print("[SKIP] No activity list items with custom fields found in sample")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_activity_list_integration/test_activity_list_filter_methods.yaml")
async def test_activity_list_filter_methods():
    """
    Test activity list filtering methods.

    Validates get_emails(), get_appointments(), get_tasks() methods.

    Cassette: tests/cassettes/integration/test_activity_list_integration/test_activity_list_filter_methods.yaml
    """
    async with Upsales.from_env() as upsales:
        # Test get_emails()
        emails = await upsales.activity_list.get_emails(limit=50)
        assert isinstance(emails, list)
        for email in emails:
            assert isinstance(email, ActivityListItem)
            assert email.is_email
            assert email.subject is not None

        # Test get_appointments()
        appointments = await upsales.activity_list.get_appointments(limit=50)
        assert isinstance(appointments, list)
        for appointment in appointments:
            assert isinstance(appointment, ActivityListItem)
            assert appointment.is_appointment
            assert appointment.isAppointment is True

        # Test get_tasks()
        tasks = await upsales.activity_list.get_tasks(limit=50)
        assert isinstance(tasks, list)
        for task in tasks:
            assert isinstance(task, ActivityListItem)
            assert task.is_task
            assert not task.is_email
            assert not task.is_appointment

        print("[OK] Filter methods validated:")
        print(f"  - get_emails(): {len(emails)} emails")
        print(f"  - get_appointments(): {len(appointments)} appointments")
        print(f"  - get_tasks(): {len(tasks)} tasks")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_activity_list_integration/test_activity_list_search.yaml")
async def test_activity_list_search():
    """
    Test activity list search method.

    Validates search() method with filters.

    Cassette: tests/cassettes/integration/test_activity_list_integration/test_activity_list_search.yaml
    """
    async with Upsales.from_env() as upsales:
        # Test search with limit
        items = await upsales.activity_list.search(limit=10)

        assert isinstance(items, list)
        # Note: API may return more items than requested limit
        assert len(items) > 0

        for item in items:
            assert isinstance(item, ActivityListItem)
            assert isinstance(item.id, int)

        print(f"[OK] Search validated: {len(items)} items found")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_activity_list_integration/test_activity_list_pagination.yaml")
async def test_activity_list_pagination():
    """
    Test activity list pagination with different offsets.

    Validates that pagination parameters work correctly.

    Cassette: tests/cassettes/integration/test_activity_list_integration/test_activity_list_pagination.yaml
    """
    async with Upsales.from_env() as upsales:
        # Get first page
        page1 = await upsales.activity_list.list(limit=10, offset=0)
        assert isinstance(page1, list)
        assert len(page1) > 0

        # Get second page (if enough data exists)
        page2 = await upsales.activity_list.list(limit=10, offset=10)
        assert isinstance(page2, list)

        # Validate all items are ActivityListItem instances
        for item in page1 + page2:
            assert isinstance(item, ActivityListItem)
            assert isinstance(item.id, int)

        print(f"[OK] Pagination validated: page1={len(page1)}, page2={len(page2)} items")
