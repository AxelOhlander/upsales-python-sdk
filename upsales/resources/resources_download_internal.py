"""sDownloadInternal resource for Upsales API.

Internal resource download.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class ResourcesDownloadInternalResource:
    """Internal resource download.

    Read-only endpoint at /resources/download/internal.
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize resource.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/resources/download/internal"

    async def get(self, **params: Any) -> dict[str, Any]:
        """Get internal resource download.

        Args:
            **params: Query parameters for filtering.

        Returns:
            API response data.
        """
        return await self._http.get(self._endpoint, **params)
