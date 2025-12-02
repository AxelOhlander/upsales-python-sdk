"""SendBeam model for push notification API.

This module defines models for the sendBeam endpoint which sends push
notifications to mobile devices.
"""

from typing import TYPE_CHECKING, Any

from pydantic import Field

from upsales.models.base import BaseModel

if TYPE_CHECKING:
    from upsales.client import Upsales


class SendBeamCreateFields(dict[str, Any]):
    """Available fields for creating a SendBeam notification.

    Note: This uses dict instead of TypedDict because field names contain hyphens.

    Required:
        loc-key (str): Localization key for the notification message

    Optional:
        loc-args (list[str]): Arguments for localized string formatting
        sound (str): Sound file name to play with notification
        category (str): Notification category for custom actions
    """


class SendBeam(BaseModel):
    """Push notification sent to mobile devices.

    This is a write-only model used for sending push notifications.
    The API does not return structured data on success.

    Attributes:
        loc_key: Localization key for the notification message
        loc_args: Optional arguments for localized string formatting
        sound: Optional sound file name to play with notification
        category: Optional notification category for custom actions

    Example:
        ```python
        # Create notification
        notification = SendBeam(
            loc_key="NEW_MESSAGE",
            loc_args=["John Doe"],
            sound="notification.wav",
            category="message"
        )

        # Send via API
        await upsales.send_beam.create(
            loc_key="NEW_MESSAGE",
            loc_args=["John Doe"],
            sound="notification.wav"
        )
        ```
    """

    # Using underscores in Python, will alias to hyphens for API
    loc_key: str = Field(
        alias="loc-key", description="Localization key for the notification message"
    )
    loc_args: list[str] | None = Field(
        None, alias="loc-args", description="Arguments for localized string formatting"
    )
    sound: str | None = Field(None, description="Sound file name to play with notification")
    category: str | None = Field(None, description="Notification category for custom actions")

    # Optional client reference for instance methods
    _client: "Upsales | None" = None

    model_config = {
        "populate_by_name": True,
        "str_strip_whitespace": True,
        "validate_assignment": True,
        "use_enum_values": True,
        "json_schema_extra": {
            "example": {
                "loc-key": "NEW_MESSAGE",
                "loc-args": ["John Doe"],
                "sound": "notification.wav",
                "category": "message",
            }
        },
    }
