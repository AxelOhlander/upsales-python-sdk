"""Industries resource for Upsales API.

Industry list reference data.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class IndustriesResource:
    """Industry list reference data.

    Read-only endpoint at /industries.
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize resource.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/industries"

    async def list(self, **params: Any) -> dict[str, Any]:
        """List available industries.

        Args:
            **params: Query parameters for filtering.

        Returns:
            API response data.
        """
        return await self._http.get(self._endpoint, **params)
