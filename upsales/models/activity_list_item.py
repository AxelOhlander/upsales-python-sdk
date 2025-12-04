"""
Activity list item models for Upsales API search/activitylist endpoint.

The /api/v2/search/activitylist endpoint returns a heterogeneous list of
activities including tasks, appointments, emails, and other activity types.

This is a read-only search endpoint that aggregates different activity types,
so items have varying field sets depending on activity type.

Example:
    >>> items = await upsales.activity_list.search(limit=10)
    >>> for item in items:
    ...     if item.is_email:
    ...         print(f"Email: {item.subject}")
    ...     elif item.is_appointment:
    ...         print(f"Appointment: {item.description}")
"""

from typing import TYPE_CHECKING, Any

from pydantic import BaseModel as PydanticBase
from pydantic import ConfigDict, Field, computed_field

from upsales.models.company import PartialCompany
from upsales.models.contacts import PartialContact
from upsales.models.mail_templates import PartialMailTemplate
from upsales.models.orders import PartialOrder
from upsales.models.projects import PartialProject
from upsales.models.user import PartialUser
from upsales.validators import CustomFieldsList

if TYPE_CHECKING:
    from upsales.client import Upsales


class ActivityListItem(PydanticBase):
    """
    Activity list item from /api/v2/search/activitylist.

    Represents any type of activity in the activity list search results.
    Can be a task, appointment, email, or other activity type.

    Note: Field availability varies by activity type. Email activities have
    subject/to/from fields, while task/appointment activities have
    description/notes fields.

    Attributes:
        id: Unique activity ID
        date: Activity date
        modDate: Last modification date
        users: List of assigned users
        contacts: List of associated contacts
        client: Associated company/account
        project: Associated project
        opportunity: Associated opportunity
        custom: Custom fields
        userRemovable: Whether user can remove this activity
        userEditable: Whether user can edit this activity

        # Task/Appointment fields (may be None for emails)
        description: Activity description
        notes: Activity notes
        activityType: Type of activity
        isAppointment: Whether this is an appointment
        priority: Priority level
        time: Time of activity
        closeDate: Completion date
        regDate: Registration date
        regBy: User who created this
        private: Whether activity is private
        projectPlan: Associated project plan
        parentAppointmentId: Parent appointment ID
        parentActivityId: Parent activity ID
        ticketId: Associated ticket ID
        agreementId: Associated agreement ID
        clientConnection: Client connection info

        # Email fields (may be None for tasks/appointments)
        subject: Email subject
        to: Email recipient
        from: Email sender
        cc: Email CC recipients
        mailBodySnapshotId: Email body snapshot ID
        groupMailId: Group mail ID
        jobId: Email job ID
        templateId: Email template used
        type: Email type (out, in, pro)
        tags: Email tags

    Example:
        >>> items = await upsales.activity_list.search()
        >>> for item in items:
        ...     if item.is_email:
        ...         print(f"Email: {item.subject} to {item.to}")
        ...     elif item.is_appointment:
        ...         print(f"Appointment: {item.description}")
        ...     else:
        ...         print(f"Task: {item.description}")
    """

    model_config = ConfigDict(
        frozen=False,
        validate_assignment=True,
        extra="allow",
        populate_by_name=True,
    )

    # Common fields (present in all activity types)
    id: int = Field(description="Unique activity ID")
    date: str | None = Field(None, description="Activity date")
    modDate: str | None = Field(None, description="Last modification date")
    users: list[PartialUser] = Field(default_factory=list, description="Assigned users")
    contacts: list[PartialContact] = Field(default_factory=list, description="Associated contacts")
    client: PartialCompany | None = Field(None, description="Associated company/account")
    project: PartialProject | None = Field(None, description="Associated project")
    opportunity: PartialOrder | None = Field(None, description="Associated opportunity/order")
    custom: CustomFieldsList = Field(default_factory=list, description="Custom fields")
    userRemovable: bool = Field(description="Whether user can remove this activity")
    userEditable: bool = Field(description="Whether user can edit this activity")

    # Task/Appointment specific fields
    description: str | None = Field(None, description="Activity description")
    notes: str | None = Field(None, description="Activity notes")
    activityType: dict[str, Any] | None = Field(None, description="Type of activity")
    isAppointment: bool | None = Field(None, description="Whether this is an appointment")
    priority: int | None = Field(None, description="Priority level")
    time: str | None = Field(None, description="Time of activity")
    closeDate: str | None = Field(None, description="Completion date")
    regDate: str | None = Field(None, description="Registration date")
    regBy: PartialUser | None = Field(None, description="User who created this")
    private: bool | None = Field(None, description="Whether activity is private")
    projectPlan: dict[str, Any] | None = Field(None, description="Associated project plan")
    parentAppointmentId: int | None = Field(None, description="Parent appointment ID")
    parentActivityId: int | None = Field(None, description="Parent activity ID")
    ticketId: int | None = Field(None, description="Associated ticket ID")
    agreementId: int | None = Field(None, description="Associated agreement ID")
    clientConnection: dict[str, Any] | None = Field(None, description="Client connection info")

    # Email specific fields
    subject: str | None = Field(None, description="Email subject")
    to: str | None = Field(None, description="Email recipient")
    from_: str | None = Field(None, alias="from", description="Email sender")
    cc: list[str] | None = Field(None, description="Email CC recipients")
    mailBodySnapshotId: int | None = Field(None, description="Email body snapshot ID")
    groupMailId: int | None = Field(None, description="Group mail ID")
    jobId: int | None = Field(None, description="Email job ID")
    templateId: PartialMailTemplate | None = Field(None, description="Email template used")
    type: str | None = Field(None, description="Email type (out, in, pro)")
    tags: list[dict[str, Any]] | None = Field(None, description="Email tags")

    # Internal reference
    _client: "Upsales | None" = None

    @computed_field
    @property
    def is_email(self) -> bool:
        """
        Check if this is an email activity.

        Returns:
            True if this is an email activity, False otherwise.

        Example:
            >>> item.is_email
            True
        """
        return self.subject is not None

    @computed_field
    @property
    def is_appointment(self) -> bool:
        """
        Check if this is an appointment.

        Returns:
            True if this is an appointment, False otherwise.

        Example:
            >>> item.is_appointment
            True
        """
        return self.isAppointment is True

    @computed_field
    @property
    def is_task(self) -> bool:
        """
        Check if this is a task (not appointment, not email).

        Returns:
            True if this is a task, False otherwise.

        Example:
            >>> item.is_task
            True
        """
        return not self.is_email and not self.is_appointment

    @computed_field
    @property
    def display_title(self) -> str:
        """
        Get display title for this activity.

        Returns subject for emails, description for tasks/appointments.

        Returns:
            Display title string.

        Example:
            >>> item.display_title
            'Follow-up call'
        """
        if self.subject:
            return self.subject
        return self.description or ""

    @computed_field
    @property
    def has_company(self) -> bool:
        """
        Check if activity is linked to a company.

        Returns:
            True if linked to company, False otherwise.

        Example:
            >>> item.has_company
            True
        """
        return self.client is not None

    @computed_field
    @property
    def has_contacts(self) -> bool:
        """
        Check if activity has associated contacts.

        Returns:
            True if has contacts, False otherwise.

        Example:
            >>> item.has_contacts
            True
        """
        return len(self.contacts) > 0

    @computed_field
    @property
    def is_closed(self) -> bool:
        """
        Check if activity is closed/completed.

        Returns:
            True if activity has closeDate, False otherwise.

        Example:
            >>> item.is_closed
            False
        """
        return self.closeDate is not None


__all__ = ["ActivityListItem"]
