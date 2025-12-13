"""
Activity models for Upsales API.

Generated from /api/v2/activities endpoint.
Analysis based on 2 samples.

Enhanced with Pydantic v2 features:
- Reusable validators (BinaryFlag, CustomFieldsList, NonEmptyStr)
- Computed fields (@computed_field)
- Field serialization (@field_serializer)
- Strict type checking
- Field descriptions
- Optimized serialization

Activities represent tasks, appointments, and interactions in Upsales.
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
from upsales.validators import BinaryFlag, CustomFieldsList, NonEmptyStr


class ActivityUpdateFields(TypedDict, total=False):
    """
    Available fields for updating an Activity.

    All fields are optional. Use with Unpack for IDE autocomplete.
    """

    notes: str
    isAppointment: int
    custom: list[Any]
    closeDate: str | None
    opportunity: dict[str, Any] | None
    agreementId: int | None
    priority: int
    ticketId: int | None
    contacts: list[dict[str, Any]]
    outcomes: list[dict[str, Any]]
    userRemovable: bool
    client: dict[str, Any] | None
    activityType: dict[str, Any]
    project: dict[str, Any] | None
    callList: dict[str, Any] | None
    users: list[dict[str, Any]]
    projectPlan: dict[str, Any] | None
    time: str | None
    parentActivityId: int | None
    closeTime: str | None
    lastOutcome: dict[str, Any]
    description: str
    date: str
    parentAppointmentId: int | None
    userEditable: bool


class Activity(BaseModel):
    """
    Activity model from /api/v2/activities.

    Represents activities, tasks, and appointments in Upsales. Enhanced with
    Pydantic v2 validators, computed fields, and optimized serialization.

    Activities can be:
    - Tasks (isAppointment=0)
    - Appointments (isAppointment=1)
    - Linked to companies, opportunities, projects, tickets, agreements

    Example:
        >>> # Get activity
        >>> activity = await upsales.activities.get(1)
        >>> activity.description
        'Follow-up call with client'
        >>>
        >>> # Use computed fields
        >>> activity.is_appointment
        True
        >>> activity.custom_fields[11]
        'Meeting notes'
        >>>
        >>> # Edit activity (IDE autocomplete!)
        >>> await activity.edit(
        ...     description="Updated description",
        ...     priority=2,
        ...     closeDate="2025-11-15"
        ... )
    """

    # Read-only fields (frozen=True, strict=True)
    id: int = Field(frozen=True, strict=True, description="Unique activity ID")
    regDate: str = Field(frozen=True, description="Registration date (ISO 8601)")
    modDate: str = Field(frozen=True, description="Last modification date (ISO 8601)")

    # Required fields with validators
    description: NonEmptyStr = Field(description="Activity description")
    notes: str | None = Field(default=None, description="Activity notes/content")
    date: str | None = Field(default=None, description="Activity date (ISO 8601 format)")

    # Binary flags (validated 0 or 1)
    isAppointment: BinaryFlag = Field(
        default=0, description="Is this an appointment? (0=task, 1=appointment)"
    )

    # Priority field (1-5 typically, but stored as int)
    priority: int = Field(default=0, description="Activity priority (higher = more urgent)")

    # Boolean flags
    userEditable: bool = Field(default=True, description="Can user edit this activity?")
    userRemovable: bool = Field(default=True, description="Can user remove this activity?")

    # Custom fields (validated structure)
    custom: CustomFieldsList = Field(
        default=[], description="Custom fields with validated structure"
    )

    # Related entities (use dict for flexible nested structures)
    activityType: dict[str, Any] = Field(
        default_factory=dict,
        description="Activity type definition (complex structure, not PartialActivity)",
    )
    client: PartialCompany | None = Field(None, description="Linked company/client")
    regBy: PartialUser | None = Field(None, description="Created by user")
    lastOutcome: dict[str, Any] | None = Field(None, description="Last outcome record")

    # Arrays of related entities
    contacts: list[PartialContact] = Field(default=[], description="Linked contacts")
    users: list[PartialUser] = Field(default=[], description="Assigned users")
    outcomes: list[dict[str, Any]] = Field(default=[], description="Activity outcomes")

    # Optional related entities
    opportunity: PartialOrder | None = Field(None, description="Linked opportunity/order")
    project: PartialProject | None = Field(None, description="Linked project")
    projectPlan: dict[str, Any] | None = Field(None, description="Linked project plan")
    callList: dict[str, Any] | None = Field(None, description="Linked call list")

    # Optional ID references
    agreementId: int | None = Field(None, description="Linked agreement ID")
    ticketId: int | None = Field(None, description="Linked ticket ID")
    parentActivityId: int | None = Field(None, description="Parent activity ID (for sub-tasks)")
    parentAppointmentId: int | None = Field(
        None, description="Parent appointment ID (for recurring)"
    )

    # Optional date/time fields
    closeDate: str | None = Field(None, description="Close date (ISO 8601)")
    closeTime: str | None = Field(None, description="Close time (ISO 8601)")
    time: str | None = Field(None, description="Activity time (ISO 8601)")

    @computed_field
    @property
    def custom_fields(self) -> CustomFields:
        """
        Access custom fields with dict-like interface.

        Returns:
            CustomFields helper for easy access by ID or alias.

        Example:
            >>> activity.custom_fields[11]  # By field ID
            'value'
            >>> activity.custom_fields.get(11, "default")
            'value'
        """
        return CustomFields(self.custom)

    @computed_field
    @property
    def is_appointment(self) -> bool:
        """
        Check if activity is an appointment.

        Returns:
            True if isAppointment flag is 1, False otherwise (task).

        Example:
            >>> activity.is_appointment
            True  # This is an appointment
            >>> task.is_appointment
            False  # This is a task
        """
        return self.isAppointment == 1

    @computed_field
    @property
    def is_task(self) -> bool:
        """
        Check if activity is a task (not appointment).

        Returns:
            True if isAppointment flag is 0, False otherwise.

        Example:
            >>> activity.is_task
            False  # This is an appointment
            >>> task.is_task
            True  # This is a task
        """
        return self.isAppointment == 0

    @computed_field
    @property
    def is_closed(self) -> bool:
        """
        Check if activity is closed.

        Returns:
            True if closeDate is set, False otherwise.

        Example:
            >>> activity.is_closed
            True
            >>> activity.closeDate
            '2025-11-01T10:00:00Z'
        """
        return self.closeDate is not None

    @computed_field
    @property
    def has_company(self) -> bool:
        """
        Check if activity is linked to a company.

        Returns:
            True if client field contains data, False otherwise.

        Example:
            >>> activity.has_company
            True
            >>> activity.client
            {'id': 1, 'name': 'ACME Corp'}
        """
        return bool(self.client and self.client.id)

    @computed_field
    @property
    def has_opportunity(self) -> bool:
        """
        Check if activity is linked to an opportunity.

        Returns:
            True if opportunity field contains data, False otherwise.

        Example:
            >>> activity.has_opportunity
            True
            >>> activity.opportunity.id
            5
        """
        return bool(self.opportunity and self.opportunity.id)

    @field_serializer("custom", when_used="json")
    def serialize_custom_fields(self, custom: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Serialize custom fields for API requests.

        Removes any fields without values to keep API payloads clean.

        Args:
            custom: List of custom field dicts.

        Returns:
            Cleaned list with only fields that have values.

        Example:
            >>> # Removes items without 'value' key
            >>> [{"fieldId": 11, "value": "data"}]  # Kept
            >>> [{"fieldId": 12}]  # Removed (no value)
        """
        return [
            {"fieldId": item["fieldId"], "value": item.get("value")}
            for item in custom
            if "value" in item and item.get("value") is not None
        ]

    async def edit(self, **kwargs: Unpack[ActivityUpdateFields]) -> "Activity":
        """
        Edit this activity.

        Uses Pydantic v2's optimized serialization via to_api_dict().

        Args:
            **kwargs: Fields to update (from ActivityUpdateFields TypedDict).

        Returns:
            Updated Activity object with fresh data from API.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> activity = await upsales.activities.get(1)
            >>> updated = await activity.edit(
            ...     description="Follow-up complete",
            ...     closeDate="2025-11-15",
            ...     priority=1
            ... )
            >>> print(updated.is_closed)  # Fresh from API
            True
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.activities.update(self.id, **self.to_api_dict(**kwargs))


class PartialActivity(PartialModel):
    """
    Partial Activity for nested responses.

    Contains minimal fields for when Activity appears nested in other
    API responses (e.g., as recent activity, related activity, etc.).

    Use fetch_full() to get complete Activity object with all fields.

    Example:
        >>> opportunity = await upsales.opportunities.get(1)
        >>> recent = opportunity.recent_activity  # PartialActivity
        >>> full = await recent.fetch_full()  # Now Activity
        >>> full.description
        'Follow-up call scheduled'
    """

    # Minimum fields for identification
    id: int = Field(frozen=True, strict=True, description="Unique activity ID")
    description: NonEmptyStr = Field(description="Activity description")
    date: str = Field(description="Activity date (ISO 8601)")
    isAppointment: BinaryFlag = Field(
        default=0, description="Is this an appointment? (0=task, 1=appointment)"
    )

    @computed_field
    @property
    def is_appointment(self) -> bool:
        """
        Check if activity is an appointment.

        Returns:
            True if isAppointment flag is 1, False otherwise.

        Example:
            >>> partial.is_appointment
            True
        """
        return self.isAppointment == 1

    async def fetch_full(self) -> Activity:
        """
        Fetch complete activity data from API.

        Returns:
            Full Activity object with all fields populated.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> partial = opportunity.recent_activity  # PartialActivity
            >>> full = await partial.fetch_full()  # Activity
            >>> full.notes  # Now available
            'Meeting notes here'
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.activities.get(self.id)

    async def edit(self, **kwargs: Unpack[ActivityUpdateFields]) -> Activity:
        """
        Edit activity via partial reference.

        Args:
            **kwargs: Fields to update.

        Returns:
            Updated full Activity object from API.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> partial = opportunity.recent_activity  # PartialActivity
            >>> updated = await partial.edit(priority=3)  # Returns Activity
            >>> updated.priority
            3
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.activities.update(self.id, **kwargs)
