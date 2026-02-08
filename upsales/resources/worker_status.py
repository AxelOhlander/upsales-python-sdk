"""WorkerStatus resource for Upsales API.

Background worker status.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class WorkerStatusResource:
    """Background worker status.

    Read-only endpoint at /worker/status.
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize resource.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/worker/status"

    async def get(self, **params: Any) -> dict[str, Any]:
        """Get background worker status.

        Args:
            **params: Query parameters for filtering.

        Returns:
            API response data.
        """
        return await self._http.get(self._endpoint, **params)
