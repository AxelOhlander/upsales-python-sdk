"""DeleteLog resource for Upsales API.

Deletion audit log.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class DeleteLogResource:
    """Deletion audit log.

    Read-only endpoint at /deleteLog.
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize resource.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/deleteLog"

    async def list(self, **params: Any) -> dict[str, Any]:
        """List deletion log entries.

        Args:
            **params: Query parameters for filtering.

        Returns:
            API response data.
        """
        return await self._http.get(self._endpoint, **params)
