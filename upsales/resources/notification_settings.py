"""Notification setting resource for Upsales API."""

from __future__ import annotations

from typing import TYPE_CHECKING

from upsales.models.notification_settings import NotificationSetting, PartialNotificationSetting
from upsales.resources.base import BaseResource

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class NotificationSettingsResource(BaseResource[NotificationSetting, PartialNotificationSetting]):
    """Resource manager for notification settings.

    Handles CRUD operations for notification settings (user notification preferences).

    Example:
        ```python
        async with Upsales.from_env() as upsales:
            # Create notification setting
            setting = await upsales.notification_settings.create(
                entity="activity",
                enabled=True,
                mobile=True
            )

            # Get notification setting
            setting = await upsales.notification_settings.get("activity")

            # List notification settings
            settings = await upsales.notification_settings.list(limit=10)

            # Update notification setting
            updated = await upsales.notification_settings.update(
                "activity",
                enabled=False,
                mobile=False
            )

            # Delete notification setting
            await upsales.notification_settings.delete("activity")
        ```
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize notification settings resource.

        Args:
            http: HTTP client instance for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/notificationSettings",
            model_class=NotificationSetting,
            partial_class=PartialNotificationSetting,
        )
