"""MailTemplatesRecentlyUsed resource for Upsales API.

Recently used mail templates.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class MailTemplatesRecentlyUsedResource:
    """Recently used mail templates.

    Read-only endpoint at /mail/templates/recentlyUsed.
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize resource.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/mail/templates/recentlyUsed"

    async def list(self, **params: Any) -> dict[str, Any]:
        """List recently used mail templates.

        Args:
            **params: Query parameters for filtering.

        Returns:
            API response data.
        """
        return await self._http.get(self._endpoint, **params)
