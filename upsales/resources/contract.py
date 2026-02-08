"""Contract resource for Upsales API.

Manages legal contract terms and versions. Administrator-only endpoint.

Example:
    ```python
    async with Upsales(token="...") as upsales:
        contracts = await upsales.contracts.list()
        await upsales.contracts.update(contract_id=5, terms="Updated terms...")
    ```
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class ContractsResource:
    """Resource manager for contract terms.

    Admin-only endpoint at /contract for managing legal contracts.

    Example:
        ```python
        resource = ContractsResource(http_client)
        contracts = await resource.list()
        ```
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize contracts resource.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/contract"

    async def list(self, **params: Any) -> dict[str, Any]:
        """List contracts for the current customer.

        Args:
            **params: Query parameters (id, type, type_entity_id).

        Returns:
            API response with contract list.

        Example:
            ```python
            contracts = await upsales.contracts.list(type="integration")
            ```
        """
        return await self._http.get(self._endpoint, **params)

    async def get(self, contract_id: int) -> dict[str, Any]:
        """Get a specific contract.

        Args:
            contract_id: The contract ID.

        Returns:
            Contract data.

        Example:
            ```python
            contract = await upsales.contracts.get(5)
            ```
        """
        return await self._http.get(f"{self._endpoint}/{contract_id}")

    async def update(self, contract_id: int, terms: str) -> dict[str, Any]:
        """Update contract terms.

        Only the terms field can be updated. Version is auto-incremented.

        Args:
            contract_id: The contract ID.
            terms: New contract terms text.

        Returns:
            Updated contract data.

        Example:
            ```python
            await upsales.contracts.update(5, terms="Updated contract terms...")
            ```
        """
        return await self._http.put(
            f"{self._endpoint}/{contract_id}",
            terms=terms,
        )
