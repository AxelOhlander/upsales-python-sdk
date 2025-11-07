"""
Appointment models for Upsales API.

Generated from /api/v2/appointments endpoint.
Analysis based on 382 samples.

Enhanced with Pydantic v2 features:
- Reusable validators (BinaryFlag, CustomFieldsList, PositiveInt)
- Computed fields (@computed_field)
- Field serialization (@field_serializer)
- Strict type checking
- Field descriptions (100% coverage)
- Optimized serialization via to_api_dict()
- TypedDict for IDE autocomplete

Field optionality determined by:
- Required: Field present AND non-null in 100% of samples
- Optional: Field missing OR null in any sample
- Custom fields: Always optional with default []
"""

from typing import Any, TypedDict, Unpack

from pydantic import Field, computed_field, field_serializer

from upsales.models.base import BaseModel, PartialModel
from upsales.models.company import PartialCompany
from upsales.models.contacts import PartialContact
from upsales.models.custom_fields import CustomFields
from upsales.models.orders import PartialOrder
from upsales.models.projects import PartialProject
from upsales.models.user import PartialUser
from upsales.validators import BinaryFlag, CustomFieldsList, PositiveInt


class AppointmentUpdateFields(TypedDict, total=False):
    """
    Available fields for updating an Appointment.

    All fields are optional. Use with Unpack for IDE autocomplete.
    Does not include read-only fields (id, regDate, modDate).
    """

    # Core appointment fields
    description: str
    notes: str
    agenda: str
    location: str
    date: str
    endDate: str

    # Outcome tracking
    outcome: str
    outcomeType: Any
    outcomeAction: Any
    outcomeExtra: Any
    outcomeCommentId: Any

    # Configuration
    isAppointment: int
    private: bool
    includeWeblink: int
    isExternalHost: bool
    userEditable: bool
    userRemovable: bool

    # Weblink and calendar
    weblinkUrl: str
    externalCalendarId: str
    bookedRooms: str

    # Relationships
    client: dict[str, Any]
    contacts: list[dict[str, Any]]
    opportunity: dict[str, Any]
    project: dict[str, Any]
    users: list[dict[str, Any]]
    regBy: dict[str, Any]

    # Activity type
    activityType: dict[str, Any]

    # AI and advanced
    aiNotes: Any
    emailAttendees: list[Any]
    clientConnection: Any
    projectPlan: Any
    seriesMasterId: Any

    # Custom fields
    custom: list[Any]


class Appointment(BaseModel):
    """
    Appointment model from /api/v2/appointments.

    Represents an appointment (meeting/call/activity) in the Upsales system with full data.
    Enhanced with Pydantic v2 validators, computed fields, and optimized serialization.

    Generated from 382 samples with field analysis.

    Example:
        >>> appointment = await upsales.appointments.get(1)
        >>> appointment.description
        'Client Meeting - Q1 Review'
        >>> appointment.is_appointment  # Computed property
        True
        >>> appointment.has_outcome  # Check if outcome recorded
        True
        >>> appointment.custom_fields[11]  # Access custom fields
        'value'
        >>> await appointment.edit(
        ...     description="Client Meeting - Q1 Review Updated",
        ...     outcome="Completed"
        ... )  # IDE autocomplete
    """

    # Read-only fields (frozen=True, strict=True)
    id: PositiveInt = Field(frozen=True, strict=True, description="Unique appointment ID")
    regDate: str = Field(frozen=True, description="Registration date (ISO 8601)")
    modDate: str = Field(frozen=True, description="Last modification date (ISO 8601)")

    # Core appointment fields
    description: str = Field(description="Appointment description/title")
    date: str = Field(description="Appointment start date and time (ISO 8601)")
    endDate: str = Field(description="Appointment end date and time (ISO 8601)")

    # Optional descriptive fields
    notes: str | None = Field(None, description="Appointment notes/comments")
    agenda: str | None = Field(None, description="Meeting agenda")
    location: str | None = Field(None, description="Meeting location/venue")

    # Outcome tracking
    outcome: str | None = Field(
        None, description="Appointment outcome (e.g., 'Completed', 'Cancelled')"
    )
    outcomeType: Any | None = Field(None, description="Outcome type classification")
    outcomeAction: Any | None = Field(None, description="Follow-up action from outcome")
    outcomeExtra: Any | None = Field(None, description="Extra outcome data")
    outcomeCommentId: Any | None = Field(None, description="Associated outcome comment ID")

    # Configuration flags
    isAppointment: BinaryFlag = Field(
        default=1, description="Whether this is an appointment (0=activity, 1=appointment)"
    )
    private: bool = Field(default=False, description="Whether appointment is private")
    includeWeblink: BinaryFlag = Field(
        default=0, description="Whether to include weblink for remote meeting (0=no, 1=yes)"
    )
    isExternalHost: bool = Field(
        default=False, description="Whether host is external to organization"
    )
    userEditable: bool = Field(default=True, description="Whether users can edit this appointment")
    userRemovable: bool = Field(
        default=True, description="Whether users can delete this appointment"
    )

    # Weblink and calendar integration
    weblinkUrl: str | None = Field(None, description="URL for remote meeting/weblink")
    externalCalendarId: str | None = Field(
        None, description="External calendar system ID (e.g., Google Calendar, Outlook)"
    )
    bookedRooms: str | None = Field(None, description="Booked meeting rooms")
    seriesMasterId: Any | None = Field(
        None, description="Master ID for recurring appointment series"
    )

    # Relationships (nested objects - use dict for complex/varying structures)
    client: PartialCompany | None = Field(None, description="Associated company/account")
    contacts: list[PartialContact] = Field(
        default_factory=list, description="Contacts attending the appointment"
    )
    opportunity: PartialOrder | None = Field(None, description="Associated opportunity/order")
    project: PartialProject | None = Field(None, description="Associated project")
    users: list[PartialUser] = Field(
        default_factory=list, description="Users attending/assigned to appointment"
    )
    regBy: PartialUser | None = Field(None, description="User who created the appointment")

    # Activity type (complex nested object, use dict)
    activityType: dict[str, Any] = Field(
        default_factory=dict, description="Activity type classification"
    )
    source: dict[str, Any] | None = Field(None, description="Appointment source information")

    # Advanced features
    aiNotes: Any | None = Field(None, description="AI-generated notes from appointment")
    emailAttendees: list[Any] = Field(
        default_factory=list, description="Email addresses of external attendees"
    )
    clientConnection: Any | None = Field(None, description="Client connection data")
    projectPlan: Any | None = Field(None, description="Associated project plan")

    # Custom fields (always include for all models)
    custom: CustomFieldsList = Field(default_factory=list, description="Custom field values")

    @computed_field
    @property
    def custom_fields(self) -> CustomFields:
        """
        Access custom fields with dict-like interface.

        Returns:
            CustomFields helper for accessing custom field values by ID or alias.

        Example:
            >>> appointment.custom_fields[11]  # By field ID
            'Conference Room A'
            >>> appointment.custom_fields["MEETING_TYPE"]  # By alias
            'In-Person'
        """
        return CustomFields(self.custom)

    @computed_field
    @property
    def is_appointment(self) -> bool:
        """
        Check if this is an appointment (vs generic activity).

        Returns:
            True if isAppointment flag is 1, False otherwise.

        Example:
            >>> appointment.is_appointment
            True
        """
        return self.isAppointment == 1

    @computed_field
    @property
    def has_outcome(self) -> bool:
        """
        Check if appointment has a recorded outcome.

        Returns:
            True if outcome is not None and not empty, False otherwise.

        Example:
            >>> appointment.has_outcome
            True
        """
        return bool(self.outcome and self.outcome.strip())

    @computed_field
    @property
    def has_weblink(self) -> bool:
        """
        Check if appointment includes a weblink for remote meeting.

        Returns:
            True if includeWeblink is 1, False otherwise.

        Example:
            >>> appointment.has_weblink
            True
        """
        return self.includeWeblink == 1

    @computed_field
    @property
    def has_attendees(self) -> bool:
        """
        Check if appointment has any attendees (users or contacts).

        Returns:
            True if at least one user or contact is assigned, False otherwise.

        Example:
            >>> appointment.has_attendees
            True
        """
        return len(self.users) > 0 or len(self.contacts) > 0

    @computed_field
    @property
    def attendee_count(self) -> int:
        """
        Get total number of attendees (users + contacts).

        Returns:
            Total count of users and contacts assigned to appointment.

        Example:
            >>> appointment.attendee_count
            5
        """
        return len(self.users) + len(self.contacts)

    @field_serializer("custom", when_used="json")
    def serialize_custom_fields(self, custom: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Clean custom fields for API requests.

        Only includes fields with non-null values and removes extra metadata.
        Uses Pydantic v2 field serializer for automatic application during
        model_dump(mode='json').

        Args:
            custom: Raw custom fields list.

        Returns:
            Cleaned list with only fieldId and value.

        Example:
            >>> appointment.model_dump(mode='json')
            {'custom': [{'fieldId': 11, 'value': 'test'}]}
        """
        return [
            {"fieldId": item["fieldId"], "value": item.get("value")}
            for item in custom
            if "value" in item and item.get("value") is not None
        ]

    async def edit(self, **kwargs: Unpack[AppointmentUpdateFields]) -> "Appointment":
        """
        Edit this appointment with type-safe field updates.

        Provides full IDE autocomplete for available fields via TypedDict.
        Automatically excludes read-only fields (id, regDate, modDate) using to_api_dict().

        Args:
            **kwargs: Fields to update (see AppointmentUpdateFields for available options).

        Returns:
            Updated appointment with new values.

        Raises:
            RuntimeError: If no client is available (model not fetched via SDK).

        Example:
            >>> appointment = await upsales.appointments.get(1)
            >>> updated = await appointment.edit(
            ...     description="Updated Meeting Title",
            ...     outcome="Completed",
            ...     notes="Great discussion about Q1 targets"
            ... )
            >>> updated.description
            'Updated Meeting Title'

        Note:
            Uses optimized Pydantic v2 serialization (5-50x faster than v1).
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.appointments.update(self.id, **self.to_api_dict(**kwargs))


class PartialAppointment(PartialModel):
    """
    Partial Appointment for nested responses.

    Contains minimal appointment information when appointments appear as nested
    objects in other API responses.

    Example:
        >>> activity = await upsales.activities.get(1)
        >>> if activity.appointment:
        ...     print(activity.appointment.description)  # Access partial data
        ...     full = await activity.appointment.fetch_full()  # Fetch full details
    """

    id: PositiveInt = Field(description="Unique appointment ID")
    description: str = Field(description="Appointment description/title")
    date: str = Field(description="Appointment start date and time (ISO 8601)")

    async def fetch_full(self) -> Appointment:
        """
        Fetch full appointment data from the API.

        Returns:
            Complete Appointment object with all fields.

        Raises:
            RuntimeError: If no client is available (model not fetched via SDK).

        Example:
            >>> partial_appointment = activity.appointment
            >>> full_appointment = await partial_appointment.fetch_full()
            >>> full_appointment.location
            'Conference Room A'
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.appointments.get(self.id)

    async def edit(self, **kwargs: Unpack[AppointmentUpdateFields]) -> Appointment:
        """
        Edit this appointment directly from partial reference.

        Args:
            **kwargs: Fields to update (see AppointmentUpdateFields for available options).

        Returns:
            Updated full Appointment object.

        Raises:
            RuntimeError: If no client is available (model not fetched via SDK).

        Example:
            >>> partial_appointment = activity.appointment
            >>> updated = await partial_appointment.edit(outcome="Completed")
            >>> updated.has_outcome
            True
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.appointments.update(self.id, **kwargs)
