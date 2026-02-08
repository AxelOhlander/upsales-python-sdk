"""LandingPageTemplate resource for Upsales API.

Landing page templates.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class LandingPageTemplateResource:
    """Landing page templates.

    Read-only endpoint at /landingPageTemplate.
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize resource.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/landingPageTemplate"

    async def list(self, **params: Any) -> dict[str, Any]:
        """List landing page templates.

        Args:
            **params: Query parameters for filtering.

        Returns:
            API response data.
        """
        return await self._http.get(self._endpoint, **params)
