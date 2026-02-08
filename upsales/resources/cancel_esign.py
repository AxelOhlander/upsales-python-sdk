"""Cancel e-sign resource for Upsales API.

Cancels/revokes pending e-signature documents.

Example:
    ```python
    async with Upsales(token="...") as upsales:
        result = await upsales.cancel_esign.cancel(esign_id=123)
    ```
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class CancelEsignResource:
    """Resource manager for cancelling e-sign documents.

    Function endpoint at /function/cancelEsign/:id.

    Example:
        ```python
        resource = CancelEsignResource(http_client)
        result = await resource.cancel(esign_id=123)
        ```
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize cancel e-sign resource.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/function/cancelEsign"

    async def cancel(self, esign_id: int) -> dict[str, Any]:
        """Cancel an e-signature document.

        Args:
            esign_id: The e-sign document ID to cancel.

        Returns:
            Updated Esign object data.

        Raises:
            NotFoundError: If the e-sign document is not found.

        Example:
            ```python
            result = await upsales.cancel_esign.cancel(esign_id=123)
            ```
        """
        return await self._http.put(f"{self._endpoint}/{esign_id}")
