"""SignalsFeed resource for Upsales API.

Prospecting signals feed.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class SignalsFeedResource:
    """Prospecting signals feed.

    Read-only endpoint at /prospecting/signals.
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize resource.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/prospecting/signals"

    async def list(self, **params: Any) -> dict[str, Any]:
        """List prospecting signals.

        Args:
            **params: Query parameters for filtering.

        Returns:
            API response data.
        """
        return await self._http.get(self._endpoint, **params)
