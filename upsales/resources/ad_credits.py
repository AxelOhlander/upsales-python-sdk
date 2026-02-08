"""AdCredits resource for Upsales API.

Engage ad credits.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class AdCreditsResource:
    """Engage ad credits.

    Read-only endpoint at /engage/credit.
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize resource.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/engage/credit"

    async def get(self, **params: Any) -> dict[str, Any]:
        """Get ad credit balance.

        Args:
            **params: Query parameters for filtering.

        Returns:
            API response data.
        """
        return await self._http.get(self._endpoint, **params)
