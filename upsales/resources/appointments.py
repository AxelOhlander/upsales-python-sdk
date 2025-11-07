"""
Appointments resource manager for Upsales API.

Provides methods to interact with the /appointments endpoint using Appointment models.

Example:
    >>> async with Upsales(token="...") as upsales:
    ...     # Get single appointment
    ...     appointment = await upsales.appointments.get(1)
    ...     print(appointment.description, appointment.has_outcome)
    ...
    ...     # List appointments
    ...     appointments = await upsales.appointments.list(limit=10)
    ...
    ...     # Get completed appointments
    ...     completed = await upsales.appointments.get_completed()
    ...
    ...     # Get appointments for a specific user
    ...     user_appointments = await upsales.appointments.get_by_user(user_id=123)
    ...
    ...     # Get upcoming appointments
    ...     upcoming = await upsales.appointments.get_upcoming()
"""

from datetime import datetime

from upsales.http import HTTPClient
from upsales.models.appointments import Appointment, PartialAppointment
from upsales.resources.base import BaseResource


class AppointmentsResource(BaseResource[Appointment, PartialAppointment]):
    """
    Resource manager for Appointments endpoint.

    Inherits standard CRUD operations from BaseResource:
    - get(id) - Get single appointment
    - list(limit, offset, **params) - List appointments with pagination
    - list_all(**params) - Auto-paginated list of all appointments
    - create(**data) - Create new appointment
    - update(id, **data) - Update appointment
    - delete(id) - Delete appointment
    - bulk_update(ids, data, max_concurrent) - Parallel updates
    - bulk_delete(ids, max_concurrent) - Parallel deletes

    Example:
        >>> appointments = AppointmentsResource(http_client)
        >>> appointment = await appointments.get(1)
        >>> upcoming = await appointments.get_upcoming()
    """

    def __init__(self, http: HTTPClient):
        """
        Initialize appointments resource manager.

        Args:
            http: HTTP client for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/appointments",
            model_class=Appointment,
            partial_class=PartialAppointment,
        )

    async def get_by_company(self, company_id: int) -> list[Appointment]:
        """
        Get all appointments for a specific company.

        Args:
            company_id: Company ID to filter by.

        Returns:
            List of appointments associated with the company.

        Example:
            >>> appointments = await upsales.appointments.get_by_company(123)
            >>> len(appointments)
            15
        """
        all_appointments: list[Appointment] = await self.list_all()
        return [
            appointment
            for appointment in all_appointments
            if appointment.client and appointment.client.id == company_id
        ]

    async def get_by_user(self, user_id: int) -> list[Appointment]:
        """
        Get all appointments assigned to a specific user.

        Args:
            user_id: User ID to filter by.

        Returns:
            List of appointments where user is assigned as attendee.

        Example:
            >>> appointments = await upsales.appointments.get_by_user(5)
            >>> len(appointments)
            10
        """
        all_appointments: list[Appointment] = await self.list_all()
        return [
            appointment
            for appointment in all_appointments
            if any(user.id == user_id for user in appointment.users if user)
        ]

    async def get_by_contact(self, contact_id: int) -> list[Appointment]:
        """
        Get all appointments with a specific contact.

        Args:
            contact_id: Contact ID to filter by.

        Returns:
            List of appointments where contact is an attendee.

        Example:
            >>> appointments = await upsales.appointments.get_by_contact(42)
            >>> len(appointments)
            8
        """
        all_appointments: list[Appointment] = await self.list_all()
        return [
            appointment
            for appointment in all_appointments
            if any(contact.id == contact_id for contact in appointment.contacts if contact)
        ]

    async def get_completed(self) -> list[Appointment]:
        """
        Get all appointments with recorded outcomes (completed).

        Returns:
            List of appointments that have an outcome recorded.

        Example:
            >>> completed = await upsales.appointments.get_completed()
            >>> all(a.has_outcome for a in completed)
            True
        """
        all_appointments: list[Appointment] = await self.list_all()
        return [appointment for appointment in all_appointments if appointment.has_outcome]

    async def get_upcoming(self, from_date: str | None = None) -> list[Appointment]:
        """
        Get all upcoming appointments (future dates).

        Args:
            from_date: Optional start date in ISO 8601 format. Defaults to now.

        Returns:
            List of appointments with date >= from_date.

        Example:
            >>> upcoming = await upsales.appointments.get_upcoming()
            >>> # Get appointments from specific date
            >>> future = await upsales.appointments.get_upcoming("2025-12-01")
        """
        if from_date is None:
            from_date = datetime.now().isoformat()

        all_appointments: list[Appointment] = await self.list_all()
        return [appointment for appointment in all_appointments if appointment.date >= from_date]

    async def get_by_opportunity(self, opportunity_id: int) -> list[Appointment]:
        """
        Get all appointments associated with a specific opportunity/order.

        Args:
            opportunity_id: Opportunity/order ID to filter by.

        Returns:
            List of appointments linked to the opportunity.

        Example:
            >>> appointments = await upsales.appointments.get_by_opportunity(789)
            >>> len(appointments)
            3
        """
        all_appointments: list[Appointment] = await self.list_all()
        return [
            appointment
            for appointment in all_appointments
            if appointment.opportunity and appointment.opportunity.id == opportunity_id
        ]

    async def get_with_weblink(self) -> list[Appointment]:
        """
        Get all appointments that include a weblink (remote meetings).

        Returns:
            List of appointments with includeWeblink=1.

        Example:
            >>> weblink_appointments = await upsales.appointments.get_with_weblink()
            >>> all(a.has_weblink for a in weblink_appointments)
            True
        """
        all_appointments: list[Appointment] = await self.list_all()
        return [appointment for appointment in all_appointments if appointment.has_weblink]
