"""Soliditet search buy resource for Upsales API.

Purchases/imports companies from Soliditet database.

Example:
    ```python
    async with Upsales(token="...") as upsales:
        client = await upsales.soliditet_search_buy.buy(
            duns="123456789",
            properties=[{"name": "User", "value": 42}],
        )
    ```
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class SoliditetSearchBuyResource:
    """Resource manager for purchasing companies from Soliditet.

    POST-only endpoint at /soliditet/search/buy.

    Example:
        ```python
        resource = SoliditetSearchBuyResource(http_client)
        client = await resource.buy(duns="123456789")
        ```
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize Soliditet search buy resource.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/soliditet/search/buy"

    async def buy(
        self,
        duns: str,
        options: dict[str, Any] | None = None,
        properties: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Purchase/import a company from Soliditet.

        Args:
            duns: DUNS number of the company to buy.
            options: Purchase options (can be empty dict).
            properties: Name/value pairs. Auto-adds current user if not present.

        Returns:
            Created/enriched client data.

        Example:
            ```python
            client = await upsales.soliditet_search_buy.buy(
                duns="123456789",
                properties=[{"name": "User", "value": 42}],
            )
            ```
        """
        return await self._http.post(
            self._endpoint,
            duns=duns,
            options=options or {},
            properties=properties or [],
        )
