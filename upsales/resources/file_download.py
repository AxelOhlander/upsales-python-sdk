"""FileDownload resource for Upsales API.

File download access.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class FileDownloadResource:
    """File download access.

    Read-only endpoint at /file/download.
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize resource.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/file/download"

    async def get(self, **params: Any) -> dict[str, Any]:
        """Get file download URL or metadata.

        Args:
            **params: Query parameters for filtering.

        Returns:
            API response data.
        """
        return await self._http.get(self._endpoint, **params)
