"""Notification setting models for Upsales API.

This module defines models for notification settings (user notification preferences).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Unpack

from pydantic import Field, computed_field

from upsales.models.base import BaseModel, PartialModel
from upsales.models.custom_fields import CustomFields
from upsales.validators import CustomFieldsList

if TYPE_CHECKING:
    from upsales.types import NotificationSettingUpdateFields


class NotificationSetting(BaseModel):
    """Notification setting model.

    Represents user-specific notification preferences for reminders and notifications.

    Attributes:
        type: Notification type (read-only).
        entity: Entity type for notification (required for creation).
        userId: User ID (read-only).
        brandId: Brand ID (read-only).
        reminderTime: Reminder time value.
        reminderUnit: Reminder time unit.
        enabled: Whether notification is enabled (required for creation).
        mobile: Whether mobile notifications are enabled.
        title: Notification title (read-only).
        custom: Custom fields list.

    Example:
        ```python
        # Create notification setting
        setting = await upsales.notification_settings.create(
            entity="activity",
            enabled=True,
            mobile=True
        )

        # Update notification setting
        setting.enabled = False
        updated = await setting.edit()

        # Or use edit with parameters
        updated = await setting.edit(enabled=False, mobile=False)
        ```
    """

    # Read-only fields
    type: str | None = Field(None, frozen=True, description="Notification type")
    userId: int | None = Field(None, frozen=True, description="User ID")
    brandId: int | None = Field(None, frozen=True, description="Brand ID")
    title: str | None = Field(None, frozen=True, description="Notification title")

    # Updatable fields
    entity: str = Field(description="Entity type for notification")
    enabled: bool = Field(description="Notification enabled status")
    mobile: bool = Field(True, description="Mobile notifications enabled")
    reminderTime: int | None = Field(None, description="Reminder time value")
    reminderUnit: str | None = Field(None, description="Reminder time unit")
    custom: CustomFieldsList = Field(default=[], description="Custom fields")

    @computed_field
    @property
    def custom_fields(self) -> CustomFields:
        """Access custom fields with dict-like interface.

        Returns:
            CustomFields instance for accessing custom fields.

        Example:
            ```python
            setting = await upsales.notification_settings.get(1)
            value = setting.custom_fields.get(11)
            setting.custom_fields.set(11, "new_value")
            ```
        """
        return CustomFields(self.custom)

    @computed_field
    @property
    def is_enabled(self) -> bool:
        """Check if notification is enabled.

        Returns:
            True if enabled, False otherwise.

        Example:
            ```python
            if setting.is_enabled:
                print("Notifications are active")
            ```
        """
        return self.enabled is True

    async def edit(self, **kwargs: Unpack[NotificationSettingUpdateFields]) -> NotificationSetting:
        """Edit this notification setting with type-safe field updates.

        Args:
            **kwargs: Fields to update (entity, enabled, mobile, reminderTime,
                     reminderUnit, custom).

        Returns:
            Updated NotificationSetting instance.

        Raises:
            RuntimeError: If no client is available.
            ValidationError: If field validation fails.
            NotFoundError: If notification setting no longer exists.

        Example:
            ```python
            setting = await upsales.notification_settings.get(1)

            # Update single field
            updated = await setting.edit(enabled=False)

            # Update multiple fields
            updated = await setting.edit(
                enabled=True,
                mobile=True,
                reminderTime=30
            )
            ```
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.notification_settings.update(
            self.entity, **self.to_api_dict(**kwargs)
        )


class PartialNotificationSetting(PartialModel):
    """Partial notification setting model for nested responses.

    Used when notification settings appear as nested objects in API responses.

    Attributes:
        entity: Entity type for notification.
        enabled: Whether notification is enabled.

    Example:
        ```python
        # Fetch full notification setting from partial
        partial: PartialNotificationSetting = some_object.notification_setting
        full: NotificationSetting = await partial.fetch_full()

        # Edit through partial
        updated = await partial.edit(enabled=False)
        ```
    """

    entity: str = Field(description="Entity type for notification")
    enabled: bool = Field(description="Notification enabled status")

    async def fetch_full(self) -> NotificationSetting:
        """Fetch complete notification setting data.

        Returns:
            Full NotificationSetting instance.

        Raises:
            RuntimeError: If no client is available.
            NotFoundError: If notification setting not found.

        Example:
            ```python
            partial = PartialNotificationSetting(entity="activity", enabled=True)
            full = await partial.fetch_full()
            print(full.reminderTime)
            ```
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.notification_settings.get(self.entity)

    async def edit(self, **kwargs: Unpack[NotificationSettingUpdateFields]) -> NotificationSetting:
        """Edit this notification setting.

        Args:
            **kwargs: Fields to update.

        Returns:
            Updated NotificationSetting instance.

        Raises:
            RuntimeError: If no client is available.
            NotFoundError: If notification setting not found.

        Example:
            ```python
            partial = PartialNotificationSetting(entity="activity", enabled=True)
            updated = await partial.edit(mobile=False)
            ```
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.notification_settings.update(self.entity, **kwargs)
