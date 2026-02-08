"""Lookup resource for Upsales API.

Entity lookup by various criteria.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class LookupResource:
    """Entity lookup by various criteria.

    Read-only endpoint at /lookup.
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize resource.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/lookup"

    async def lookup(self, **params: Any) -> dict[str, Any]:
        """Look up entities by criteria.

        Args:
            **params: Query parameters for filtering.

        Returns:
            API response data.
        """
        return await self._http.get(self._endpoint, **params)
