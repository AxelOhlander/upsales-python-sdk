"""MailCampaignInfo resource for Upsales API.

Mail campaign information and statistics.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class MailCampaignInfoResource:
    """Mail campaign information and statistics.

    Read-only endpoint at /mailCampaignInfo.
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize resource.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/mailCampaignInfo"

    async def get(self, **params: Any) -> dict[str, Any]:
        """Get mail campaign info.

        Args:
            **params: Query parameters for filtering.

        Returns:
            API response data.
        """
        return await self._http.get(self._endpoint, **params)

    async def preview(self, **params: Any) -> dict[str, Any]:
        """Get mail campaign preview.

        Args:
            **params: Query parameters for filtering.

        Returns:
            API response data.
        """
        return await self._http.get(f"{self._endpoint}/preview", **params)
