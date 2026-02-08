"""Notification sending models for Upsales API.

Models for the /notify/* endpoints which send notifications to users.
Separate from the /notifications endpoint which reads existing notifications.

Example:
    ```python
    async with Upsales(token="...") as upsales:
        await upsales.notify.send_to_users(
            message="Your export is ready",
            from_name="Export Service",
            user_ids=[123, 456],
        )
    ```
"""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from upsales.models.base import BaseModel


class NotifyRequest(BaseModel):
    """Request body for sending a notification.

    Attributes:
        message: The notification message text displayed to users.
        from_name: Source/title of the notification (shown as sender name).
        type: Notification style - "info" (default) or "error".
        userIds: Array of user IDs to notify (required for /notify/users).
        entityId: Optional entity ID to link the notification to a record.
    """

    message: str = Field(description="Notification message text")
    from_name: str = Field(alias="from", description="Notification source/title")
    type: Literal["info", "error"] = Field(
        default="info", description="Notification style: info or error"
    )
    userIds: list[int] | None = Field(
        None, description="User IDs to notify (required for /notify/users)"
    )
    entityId: str | None = Field(None, description="Optional entity ID to link to")
