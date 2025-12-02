"""
Integration tests for Appointment model with real API responses.

Uses VCR.py to record API responses on first run, then replay them.
Validates that our Pydantic v2 models correctly parse real API data.

To record cassettes:
    uv run pytest tests/integration/test_appointments_integration.py -v

To re-record (delete cassette first):
    rm tests/cassettes/integration/test_appointments_integration/*.yaml
    uv run pytest tests/integration/test_appointments_integration.py -v
"""

import pytest
import vcr

from upsales import Upsales
from upsales.models.appointments import Appointment
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
@my_vcr.use_cassette("test_appointments_integration/test_list_appointments_real_response.yaml")
async def test_list_appointments_real_response():
    """
    Test listing appointments with real API response structure.

    This test records the actual API response on first run, then
    replays it from cassette on future runs. This ensures our Appointment
    model correctly parses real Upsales API data.

    Cassette: tests/cassettes/integration/test_appointments_integration/test_list_appointments_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        # Get appointments (or replay from cassette)
        appointments = await upsales.appointments.list(limit=5)

        assert isinstance(appointments, list)
        assert len(appointments) > 0, "Should have at least one appointment"

        for appointment in appointments:
            # Validate Appointment model with Pydantic v2 features
            assert isinstance(appointment, Appointment)
            assert isinstance(appointment.id, int)
            assert isinstance(appointment.description, str)
            assert isinstance(appointment.date, str)
            assert isinstance(appointment.endDate, str)

            # Validate BinaryFlag fields (0 or 1)
            assert appointment.isAppointment in (0, 1)
            assert appointment.includeWeblink in (0, 1)

            # Validate boolean fields
            assert isinstance(appointment.private, bool)
            assert isinstance(appointment.isExternalHost, bool)
            assert isinstance(appointment.userEditable, bool)
            assert isinstance(appointment.userRemovable, bool)

        print(f"[OK] Listed {len(appointments)} appointments successfully")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_appointments_integration/test_get_appointment_real_response.yaml")
async def test_get_appointment_real_response():
    """
    Test getting a single appointment by ID with real API response structure.

    Validates that fetching a specific appointment returns complete data.

    Cassette: tests/cassettes/integration/test_appointments_integration/test_get_appointment_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        # First get an appointment ID from list
        appointments = await upsales.appointments.list(limit=1)
        assert len(appointments) > 0, "Should have at least one appointment"

        appointment_id = appointments[0].id

        # Now get that specific appointment
        appointment = await upsales.appointments.get(appointment_id)

        assert isinstance(appointment, Appointment)
        assert appointment.id == appointment_id
        assert isinstance(appointment.description, str)
        assert len(appointment.description) > 0

        # Validate read-only fields are frozen
        assert Appointment.model_fields["id"].frozen is True
        assert Appointment.model_fields["regDate"].frozen is True
        assert Appointment.model_fields["modDate"].frozen is True

        print(
            f"[OK] Appointment parsed successfully: {appointment.description} (ID: {appointment.id})"
        )


@pytest.mark.asyncio
@my_vcr.use_cassette("test_appointments_integration/test_appointment_nested_objects.yaml")
async def test_appointment_nested_objects():
    """
    Test that nested objects (users, contacts, company, etc.) parse correctly.

    Validates PartialUser, PartialCompany, PartialContact, PartialOrder, PartialProject.

    Cassette: tests/cassettes/integration/test_appointments_integration/test_appointment_nested_objects.yaml
    """
    async with Upsales.from_env() as upsales:
        # Get appointments and look for ones with nested objects
        appointments = await upsales.appointments.list(limit=20)

        # Test client (PartialCompany)
        appointments_with_client = [a for a in appointments if a.client is not None]
        if appointments_with_client:
            appointment = appointments_with_client[0]
            assert isinstance(appointment.client, PartialCompany)
            assert isinstance(appointment.client.id, int)
            assert isinstance(appointment.client.name, str)
            print(f"[OK] PartialCompany validated: {appointment.client.name}")

        # Test contacts (PartialContact list)
        appointments_with_contacts = [a for a in appointments if len(a.contacts) > 0]
        if appointments_with_contacts:
            appointment = appointments_with_contacts[0]
            contact = appointment.contacts[0]
            assert isinstance(contact, PartialContact)
            assert isinstance(contact.id, int)
            assert isinstance(contact.name, str)
            print(f"[OK] PartialContact validated: {contact.name}")

        # Test users (PartialUser list)
        appointments_with_users = [a for a in appointments if len(a.users) > 0]
        if appointments_with_users:
            appointment = appointments_with_users[0]
            user = appointment.users[0]
            assert isinstance(user, PartialUser)
            assert isinstance(user.id, int)
            assert isinstance(user.name, str)
            print(f"[OK] PartialUser validated: {user.name}")

        # Test regBy (PartialUser)
        appointments_with_regby = [a for a in appointments if a.regBy is not None]
        if appointments_with_regby:
            appointment = appointments_with_regby[0]
            assert isinstance(appointment.regBy, PartialUser)
            assert isinstance(appointment.regBy.id, int)
            assert isinstance(appointment.regBy.name, str)
            print(f"[OK] regBy PartialUser validated: {appointment.regBy.name}")

        # Test opportunity (PartialOrder)
        appointments_with_opportunity = [a for a in appointments if a.opportunity is not None]
        if appointments_with_opportunity:
            appointment = appointments_with_opportunity[0]
            assert isinstance(appointment.opportunity, PartialOrder)
            assert isinstance(appointment.opportunity.id, int)
            print(f"[OK] PartialOrder validated: ID {appointment.opportunity.id}")

        # Test project (PartialProject)
        appointments_with_project = [a for a in appointments if a.project is not None]
        if appointments_with_project:
            appointment = appointments_with_project[0]
            assert isinstance(appointment.project, PartialProject)
            assert isinstance(appointment.project.id, int)
            print(f"[OK] PartialProject validated: ID {appointment.project.id}")

        print(f"[OK] Nested objects validation complete")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_appointments_integration/test_appointment_computed_fields.yaml")
async def test_appointment_computed_fields():
    """
    Test computed fields work correctly with real API data.

    Validates: is_appointment, has_outcome, has_weblink, has_attendees, attendee_count.

    Cassette: tests/cassettes/integration/test_appointments_integration/test_appointment_computed_fields.yaml
    """
    async with Upsales.from_env() as upsales:
        appointments = await upsales.appointments.list(limit=10)

        for appointment in appointments:
            # Test is_appointment computed field
            assert isinstance(appointment.is_appointment, bool)
            assert appointment.is_appointment == (appointment.isAppointment == 1)

            # Test has_outcome computed field
            assert isinstance(appointment.has_outcome, bool)
            if appointment.outcome and appointment.outcome.strip():
                assert appointment.has_outcome is True
            else:
                assert appointment.has_outcome is False

            # Test has_weblink computed field
            assert isinstance(appointment.has_weblink, bool)
            assert appointment.has_weblink == (appointment.includeWeblink == 1)

            # Test has_attendees computed field
            assert isinstance(appointment.has_attendees, bool)
            expected_has_attendees = len(appointment.users) > 0 or len(appointment.contacts) > 0
            assert appointment.has_attendees == expected_has_attendees

            # Test attendee_count computed field
            assert isinstance(appointment.attendee_count, int)
            expected_count = len(appointment.users) + len(appointment.contacts)
            assert appointment.attendee_count == expected_count

        print(f"[OK] Computed fields validated for {len(appointments)} appointments")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_appointments_integration/test_appointment_custom_fields.yaml")
async def test_appointment_custom_fields():
    """
    Test custom fields parsing with real API data.

    Validates CustomFieldsList validator and CustomFields helper.

    Cassette: tests/cassettes/integration/test_appointments_integration/test_appointment_custom_fields.yaml
    """
    async with Upsales.from_env() as upsales:
        appointments = await upsales.appointments.list(limit=20)

        # Find an appointment with custom fields
        appointment_with_custom = None
        for appointment in appointments:
            if appointment.custom:
                appointment_with_custom = appointment
                break

        if appointment_with_custom:
            # Validate custom fields structure (CustomFieldsList validator)
            assert isinstance(appointment_with_custom.custom, list)
            for field in appointment_with_custom.custom:
                assert "fieldId" in field, "CustomFieldsList should validate fieldId presence"

            # Validate custom_fields helper
            cf = appointment_with_custom.custom_fields
            assert hasattr(cf, "__getitem__")

            print(f"[OK] Custom fields validated: {len(appointment_with_custom.custom)} fields")
        else:
            print("[SKIP] No appointments with custom fields found")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_appointments_integration/test_appointment_optional_fields.yaml")
async def test_appointment_optional_fields():
    """
    Test that optional fields are correctly handled (can be None).

    Validates that fields like notes, agenda, location, outcome, weblinkUrl, etc.
    can be None without causing validation errors.

    Cassette: tests/cassettes/integration/test_appointments_integration/test_appointment_optional_fields.yaml
    """
    async with Upsales.from_env() as upsales:
        appointments = await upsales.appointments.list(limit=20)

        # Check that optional fields can be None
        for appointment in appointments:
            # These fields should be Optional (can be None)
            assert appointment.notes is None or isinstance(appointment.notes, str)
            assert appointment.agenda is None or isinstance(appointment.agenda, str)
            assert appointment.location is None or isinstance(appointment.location, str)
            assert appointment.outcome is None or isinstance(appointment.outcome, str)
            assert appointment.weblinkUrl is None or isinstance(appointment.weblinkUrl, str)
            assert appointment.externalCalendarId is None or isinstance(
                appointment.externalCalendarId, str
            )
            assert appointment.bookedRooms is None or isinstance(appointment.bookedRooms, str)

            # Nested objects should be optional
            assert appointment.client is None or isinstance(appointment.client, PartialCompany)
            assert appointment.opportunity is None or isinstance(
                appointment.opportunity, PartialOrder
            )
            assert appointment.project is None or isinstance(appointment.project, PartialProject)
            assert appointment.regBy is None or isinstance(appointment.regBy, PartialUser)

        print(f"[OK] Optional fields validated for {len(appointments)} appointments")
