"""QuickSearch resource for Upsales API.

Cross-entity search across clients, contacts, orders, etc.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class QuickSearchResource:
    """Cross-entity search across clients, contacts, orders, etc.

    Read-only endpoint at /quicksearch.
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize resource.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/quicksearch"

    async def search(self, query: str, **params: Any) -> dict[str, Any]:
        """Search across multiple entity types.

        Args:
            query: Search query string.
            **params: Query parameters for filtering.

        Returns:
            API response data.
        """
        return await self._http.get(self._endpoint, q=query, **params)
