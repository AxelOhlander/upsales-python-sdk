"""Soliditet matcher resource for Upsales API.

Matches Upsales client accounts with Soliditet/Bisnode company databases
for data enrichment and deduplication.

Example:
    ```python
    async with Upsales(token="...") as upsales:
        matches = await upsales.soliditet_matcher.list()
        await upsales.soliditet_matcher.buy(buy=[{"id": 100, "dunsNo": "123456789"}])
    ```
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class SoliditetMatcherResource:
    """Resource manager for Soliditet matching.

    Endpoint at /soliditet/matcher. Requires companiesAndContacts
    and soliditetMatcher features.

    Example:
        ```python
        resource = SoliditetMatcherResource(http_client)
        matches = await resource.list()
        ```
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize Soliditet matcher resource.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/soliditet/matcher"

    async def list(self, **params: Any) -> dict[str, Any]:
        """List clients with their Soliditet matches.

        Args:
            **params: Query parameters for filtering.

        Returns:
            API response with matched client data.

        Example:
            ```python
            matches = await upsales.soliditet_matcher.list()
            ```
        """
        return await self._http.get(self._endpoint, **params)

    async def search(
        self,
        client_id: int,
        search_string: str,
        countries: str | list[str],
        limit: int | None = None,
    ) -> dict[str, Any]:
        """Search for Soliditet matches for a specific client.

        Args:
            client_id: Client ID to search matches for.
            search_string: Search term.
            countries: ISO country codes (string or list).
            limit: Optional result limit.

        Returns:
            Search results from Soliditet.

        Example:
            ```python
            results = await upsales.soliditet_matcher.search(
                client_id=100, search_string="ACME", countries="SE"
            )
            ```
        """
        params: dict[str, Any] = {
            "id": client_id,
            "searchString": search_string,
            "countries": countries,
        }
        if limit is not None:
            params["limit"] = limit
        return await self._http.get(f"{self._endpoint}/search", **params)

    async def action(self, **data: Any) -> dict[str, Any]:
        """Perform match actions (buy, hide, merge, delete).

        Args:
            **data: Action arrays. Options:
                buy: List of {"id": clientId, "dunsNo": dunsNumber}
                hide: List of client IDs to hide
                merge: List of {"keep": keepId, "merge": mergeId}
                delete: List of client IDs to delete
                updateProspecting: List of prospecting updates

        Returns:
            Metadata with action counts.

        Example:
            ```python
            await upsales.soliditet_matcher.action(
                buy=[{"id": 100, "dunsNo": "123456789"}]
            )
            ```
        """
        return await self._http.put(self._endpoint, **data)
