"""SendBeam resource manager for push notifications.

This resource handles the /function/sendbeam endpoint which sends
push notifications to mobile devices. This is a function endpoint
that only supports POST operations.

Example:
    >>> async with Upsales(token="...") as upsales:
    ...     # Send push notification
    ...     await upsales.send_beam.send(
    ...         loc_key="NEW_MESSAGE",
    ...         loc_args=["John Doe"],
    ...         sound="notification.wav"
    ...     )
"""

from typing import Any

from upsales.http import HTTPClient


class SendBeamResource:
    """Resource manager for SendBeam endpoint.

    This is a function endpoint that only supports sending push notifications.
    Unlike standard CRUD resources, it does not support get, list, update, or delete.

    Example:
        >>> resource = SendBeamResource(http_client)
        >>> await resource.send(
        ...     loc_key="NEW_MESSAGE",
        ...     loc_args=["John Doe"],
        ...     sound="notification.wav",
        ...     category="message"
        ... )
    """

    def __init__(self, http: HTTPClient):
        """Initialize sendBeam resource manager.

        Args:
            http: HTTP client for API requests.
        """
        self.http = http
        self.endpoint = "/function/sendbeam"

    async def send(
        self,
        loc_key: str,
        loc_args: list[str] | None = None,
        sound: str | None = None,
        category: str | None = None,
    ) -> dict[str, Any]:
        """Send a push notification to mobile devices.

        Args:
            loc_key: Localization key for the notification message (required).
            loc_args: Arguments for localized string formatting.
            sound: Sound file name to play with notification.
            category: Notification category for custom actions.

        Returns:
            API response dictionary (structure depends on API implementation).

        Raises:
            ValidationError: If required fields are missing or invalid.
            ServerError: If the API request fails.

        Example:
            >>> await resource.send(
            ...     loc_key="NEW_MESSAGE",
            ...     loc_args=["John Doe", "Sales Team"],
            ...     sound="notification.wav",
            ...     category="message"
            ... )
            {"success": true}

        Note:
            Field names use hyphens in the API (loc-key, loc-args) but
            underscores in Python for consistency with PEP 8.
        """
        # Build payload with hyphenated keys for API
        payload: dict[str, Any] = {"loc-key": loc_key}

        if loc_args is not None:
            payload["loc-args"] = loc_args
        if sound is not None:
            payload["sound"] = sound
        if category is not None:
            payload["category"] = category

        response = await self.http.post(self.endpoint, json=payload)
        return response
