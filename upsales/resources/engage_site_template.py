"""EngageSiteTemplate resource for Upsales API.

Engage site templates.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class EngageSiteTemplateResource:
    """Engage site templates.

    Read-only endpoint at /engage/siteTemplate.
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize resource.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/engage/siteTemplate"

    async def list(self, **params: Any) -> dict[str, Any]:
        """List engage site templates.

        Args:
            **params: Query parameters for filtering.

        Returns:
            API response data.
        """
        return await self._http.get(self._endpoint, **params)
