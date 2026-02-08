"""Notification sending resource for Upsales API.

Provides methods to send notifications to specific users, admins, or all users.
Separate from the /notifications endpoint which reads existing notifications.

Example:
    ```python
    async with Upsales(token="...") as upsales:
        # Notify specific users
        await upsales.notify.send_to_users(
            message="Export ready",
            from_name="Export Service",
            user_ids=[123, 456],
        )

        # Notify all admins
        await upsales.notify.send_to_admins(
            message="System alert",
            from_name="Monitor",
            notification_type="error",
        )

        # Notify everyone
        await upsales.notify.send_to_all(
            message="Maintenance in 1 hour",
            from_name="IT Department",
        )
    ```
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class NotifyResource:
    """Resource manager for sending notifications.

    Provides three methods matching the three /notify/* endpoints:
    - send_to_users() - Send to specific user IDs
    - send_to_admins() - Send to all admin users
    - send_to_all() - Send to all users in the account

    Example:
        ```python
        resource = NotifyResource(http_client)
        await resource.send_to_users(
            message="Your report is ready",
            from_name="Reports",
            user_ids=[1, 2, 3],
        )
        ```
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize notify resource.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http

    async def _send(
        self,
        endpoint: str,
        message: str,
        from_name: str,
        notification_type: Literal["info", "error"] = "info",
        user_ids: list[int] | None = None,
        entity_id: str | None = None,
    ) -> dict[str, Any]:
        """Send a notification via the specified endpoint.

        Args:
            endpoint: API endpoint path.
            message: Notification message text.
            from_name: Source/title shown as sender name.
            notification_type: "info" (default) or "error".
            user_ids: User IDs to notify (for /notify/users only).
            entity_id: Optional entity ID to link notification to a record.

        Returns:
            API response data.
        """
        payload: dict[str, Any] = {
            "message": message,
            "from": from_name,
            "type": notification_type,
        }
        if user_ids is not None:
            payload["userIds"] = user_ids
        if entity_id is not None:
            payload["entityId"] = entity_id

        return await self._http.post(endpoint, **payload)

    async def send_to_users(
        self,
        message: str,
        from_name: str,
        user_ids: list[int],
        notification_type: Literal["info", "error"] = "info",
        entity_id: str | None = None,
    ) -> dict[str, Any]:
        """Send notification to specific users.

        Args:
            message: Notification message text.
            from_name: Source/title shown as sender name.
            user_ids: List of user IDs to notify.
            notification_type: "info" (default) or "error".
            entity_id: Optional entity ID to link notification to a record.

        Returns:
            API response data.

        Raises:
            ValidationError: If user_ids is empty or fields are invalid.
            AuthenticationError: If authentication fails.

        Example:
            ```python
            await upsales.notify.send_to_users(
                message="Your export is ready",
                from_name="Export Service",
                user_ids=[123, 456],
            )
            ```
        """
        return await self._send(
            "/notify/users",
            message=message,
            from_name=from_name,
            notification_type=notification_type,
            user_ids=user_ids,
            entity_id=entity_id,
        )

    async def send_to_admins(
        self,
        message: str,
        from_name: str,
        notification_type: Literal["info", "error"] = "info",
        entity_id: str | None = None,
    ) -> dict[str, Any]:
        """Send notification to all admin users.

        Args:
            message: Notification message text.
            from_name: Source/title shown as sender name.
            notification_type: "info" (default) or "error".
            entity_id: Optional entity ID to link notification to a record.

        Returns:
            API response data.

        Raises:
            AuthenticationError: If authentication fails.

        Example:
            ```python
            await upsales.notify.send_to_admins(
                message="Critical system alert",
                from_name="Monitor",
                notification_type="error",
            )
            ```
        """
        return await self._send(
            "/notify/admins",
            message=message,
            from_name=from_name,
            notification_type=notification_type,
            entity_id=entity_id,
        )

    async def send_to_all(
        self,
        message: str,
        from_name: str,
        notification_type: Literal["info", "error"] = "info",
        entity_id: str | None = None,
    ) -> dict[str, Any]:
        """Send notification to all users in the account.

        Args:
            message: Notification message text.
            from_name: Source/title shown as sender name.
            notification_type: "info" (default) or "error".
            entity_id: Optional entity ID to link notification to a record.

        Returns:
            API response data.

        Raises:
            AuthenticationError: If authentication fails.

        Example:
            ```python
            await upsales.notify.send_to_all(
                message="Maintenance in 1 hour",
                from_name="IT Department",
            )
            ```
        """
        return await self._send(
            "/notify/all",
            message=message,
            from_name=from_name,
            notification_type=notification_type,
            entity_id=entity_id,
        )
