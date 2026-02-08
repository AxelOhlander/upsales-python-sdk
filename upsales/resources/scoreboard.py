"""Scoreboard resource for Upsales API.

Scoreboard data for sales performance tracking.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class ScoreboardResource:
    """Scoreboard data for sales performance tracking.

    Read-only endpoint at /scoreboard.
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize resource.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/scoreboard"

    async def get(self, **params: Any) -> dict[str, Any]:
        """Get scoreboard data.

        Args:
            **params: Query parameters for filtering.

        Returns:
            API response data.
        """
        return await self._http.get(self._endpoint, **params)
