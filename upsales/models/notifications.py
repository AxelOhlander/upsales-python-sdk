"""
Notification models for Upsales API.

Notifications are read-only system-generated events about changes in the CRM.
They track activities like order updates, contact changes, and other important events.

This endpoint only supports GET operations - notifications cannot be created,
updated, or deleted via the API.
"""

from typing import Any

from pydantic import Field

from upsales.models.base import BaseModel, PartialModel
from upsales.models.company import PartialCompany
from upsales.models.contacts import PartialContact
from upsales.models.user import PartialUser


class Notification(BaseModel):
    """
    System-generated notification about CRM activities.

    Notifications are created automatically by Upsales when certain events occur,
    such as order updates, contact changes, or other important activities.

    This is a read-only model - notifications cannot be created, updated, or
    deleted via the API.

    Attributes:
        id: Unique notification identifier.
        type: Notification type (e.g., "Order", "Contact", "Opportunity").
        action: Action that triggered the notification.
        entityId: ID of the entity that triggered the notification.
        client: Related company/account (if applicable).
        contact: Related contact (if applicable).
        userIds: List of users who received this notification and read status.
        opportunity: Related opportunity (if applicable).
        order: Related order (if applicable).
        visit: Related visit/appointment (if applicable).
        date: ISO 8601 timestamp when notification was created.
        message: Notification message text.
        registeredBy: User who triggered the notification.
        status: Notification status (0 = unread, 1 = read).
        esign: Related e-signature document (if applicable).
        brandId: Brand identifier.
        hasData: Whether the notification has associated data.

    Example:
        ```python
        # Fetch a notification
        notification = await upsales.notifications.get(1)
        print(f"Type: {notification.type}")
        print(f"Message: {notification.message}")
        print(f"Created: {notification.date}")

        # Check who registered it (properly typed!)
        if notification.registeredBy:
            print(f"By: {notification.registeredBy.name}")
            # Can fetch full user details
            full_user = await notification.registeredBy.fetch_full()

        # Check related entities (properly typed!)
        if notification.client:
            print(f"Company: {notification.client.name}")
            full_company = await notification.client.fetch_full()

        if notification.contact:
            print(f"Contact: {notification.contact.name}")
            full_contact = await notification.contact.fetch_full()

        # Check read status
        for user in notification.userIds:
            status = "read" if user.get('read') else "unread"
            print(f"User {user.get('userId')}: {status}")
        ```

    Note:
        This is a read-only resource. The edit() method is not available
        since notifications cannot be modified via the API.
    """

    # Read-only identifier
    id: int = Field(frozen=True, strict=True, description="Unique notification ID")

    # Core notification data (all read-only)
    type: str = Field(frozen=True, description="Notification type (Order, Contact, etc.)")
    action: str = Field(frozen=True, description="Action that triggered notification")
    entityId: int = Field(frozen=True, description="ID of entity that triggered notification")
    date: str = Field(frozen=True, description="ISO 8601 timestamp of creation")
    message: str = Field(frozen=True, description="Notification message text")
    status: int = Field(frozen=True, description="Status: 0=unread, 1=read")
    brandId: int = Field(frozen=True, description="Brand identifier")
    hasData: bool = Field(frozen=True, description="Whether notification has data")

    # User tracking
    userIds: list[dict[str, Any]] = Field(
        default_factory=list,
        frozen=True,
        description="Users who received this notification with read status",
    )
    registeredBy: PartialUser | None = Field(
        None, frozen=True, description="User who triggered the notification"
    )

    # Optional related entities (all read-only)
    client: PartialCompany | None = Field(None, frozen=True, description="Related company/account")
    contact: PartialContact | None = Field(None, frozen=True, description="Related contact")
    opportunity: dict[str, Any] | None = Field(None, frozen=True, description="Related opportunity")
    order: dict[str, Any] | None = Field(None, frozen=True, description="Related order")
    visit: dict[str, Any] | None = Field(None, frozen=True, description="Related visit/appointment")
    esign: dict[str, Any] | None = Field(None, frozen=True, description="Related e-signature")
    form: dict[str, Any] | None = Field(None, frozen=True, description="Related form submission")


class PartialNotification(PartialModel):
    """
    Minimal notification data for nested responses.

    Use fetch_full() to retrieve complete notification details.

    Attributes:
        id: Unique notification identifier.
        type: Notification type.
        message: Notification message.

    Example:
        ```python
        # If you have a partial notification from a nested response
        partial = some_object.notification

        # Fetch full details
        full = await partial.fetch_full()
        print(f"Created: {full.date}")
        if full.registeredBy:
            print(f"By: {full.registeredBy.name}")
        ```

    Note:
        Notifications are read-only, so the edit() method is not available.
    """

    id: int = Field(description="Unique notification ID")
    type: str | None = Field(None, description="Notification type")
    message: str | None = Field(None, description="Notification message")

    async def fetch_full(self) -> Notification:
        """
        Fetch complete notification data.

        Returns:
            Full Notification object with all fields.

        Raises:
            RuntimeError: If no client is available.
            NotFoundError: If notification doesn't exist.
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.notifications.get(self.id)
