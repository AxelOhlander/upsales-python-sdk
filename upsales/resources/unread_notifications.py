"""UnreadNotifications resource for Upsales API.

Unread notification count.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class UnreadNotificationsResource:
    """Unread notification count.

    Read-only endpoint at /notificationsUnread.
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize resource.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/notificationsUnread"

    async def get(self, user_id: int) -> dict[str, Any]:
        """Get unread notification count for a user.

        Args:
            user_id: User ID.

        Returns:
            API response data.
        """
        return await self._http.get(f"{self._endpoint}/{user_id}")
