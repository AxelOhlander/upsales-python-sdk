"""LeadSources2 resource for Upsales API.

Lead sources v2 endpoint.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class LeadSources2Resource:
    """Lead sources v2 endpoint.

    Read-only endpoint at /leadsources2.
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize resource.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/leadsources2"

    async def list(self, **params: Any) -> dict[str, Any]:
        """List lead sources (v2).

        Args:
            **params: Query parameters for filtering.

        Returns:
            API response data.
        """
        return await self._http.get(self._endpoint, **params)
