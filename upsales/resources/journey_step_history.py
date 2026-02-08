"""JourneyStepHistory resource for Upsales API.

Journey step history records.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class JourneyStepHistoryResource:
    """Journey step history records.

    Read-only endpoint at /journeyStepHistory.
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize resource.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/journeyStepHistory"

    async def list(self, **params: Any) -> dict[str, Any]:
        """List journey step history records.

        Args:
            **params: Query parameters for filtering.

        Returns:
            API response data.
        """
        return await self._http.get(self._endpoint, **params)
