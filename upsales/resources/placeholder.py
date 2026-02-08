"""Placeholder resource for Upsales API.

Feature placeholder data.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class PlaceholderResource:
    """Feature placeholder data.

    Read-only endpoint at /placeholder.
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize resource.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/placeholder"

    async def get(self, feature: str, **params: Any) -> dict[str, Any]:
        """Get placeholder data for a feature.

        Args:
            feature: Feature name.
            **params: Query parameters for filtering.

        Returns:
            API response data.
        """
        return await self._http.get(f"{self._endpoint}/{feature}", **params)
