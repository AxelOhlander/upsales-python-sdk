"""MailByThread resource for Upsales API.

Mail messages grouped by conversation thread.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class MailByThreadResource:
    """Mail messages grouped by conversation thread.

    Read-only endpoint at /mail/byThread.
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize resource.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/mail/byThread"

    async def list(self, **params: Any) -> dict[str, Any]:
        """List mail messages grouped by thread.

        Args:
            **params: Query parameters for filtering.

        Returns:
            API response data.
        """
        return await self._http.get(self._endpoint, **params)
