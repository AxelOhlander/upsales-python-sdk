"""LookerSSO resource for Upsales API.

Looker SSO URL generation.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class LookerSSOResource:
    """Looker SSO URL generation.

    Read-only endpoint at /function/externalSSO/looker.
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize resource.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/function/externalSSO/looker"

    async def get_url(self, type: str, id: str, **params: Any) -> dict[str, Any]:
        """Get Looker SSO URL.

        Args:
            type: Looker resource type (explore, look, dashboard).
            id: Looker resource ID.
            **params: Query parameters for filtering.

        Returns:
            API response data.
        """
        return await self._http.get(f"{self._endpoint}/{type}/{id}", **params)
