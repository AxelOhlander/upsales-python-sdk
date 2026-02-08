"""EventsPrior resource for Upsales API.

Prior/historical events.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class EventsPriorResource:
    """Prior/historical events.

    Read-only endpoint at /events/prior.
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize resource.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/events/prior"

    async def list(self, **params: Any) -> dict[str, Any]:
        """List prior events.

        Args:
            **params: Query parameters for filtering.

        Returns:
            API response data.
        """
        return await self._http.get(self._endpoint, **params)
