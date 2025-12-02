"""
Provisioning resource manager for Upsales API.

Provides methods to interact with the /provisioning endpoint.
This is a pass-through/proxy endpoint that forwards requests to the provisioning service.

Note:
    This endpoint does not follow standard CRUD patterns.
    It primarily supports GET (with query params) and POST (with request body).

Example:
    >>> async with Upsales(token="...") as upsales:
    ...     # Forward GET request with query params
    ...     response = await upsales.provisioning.forward_get(action="status")
    ...     # Forward POST request with body
    ...     response = await upsales.provisioning.forward_post({"action": "provision"})
"""

from typing import Any

from upsales.http import HTTPClient
from upsales.models.provisioning import PartialProvisioningRequest, ProvisioningRequest
from upsales.resources.base import BaseResource


class ProvisioningResource(BaseResource[ProvisioningRequest, PartialProvisioningRequest]):
    """
    Resource manager for Provisioning endpoint.

    This is a special pass-through endpoint that forwards requests to the provisioning service.
    It does not support standard CRUD operations like get(id), update(id), delete(id).

    Use forward_get() and forward_post() methods instead.

    Example:
        >>> resource = ProvisioningResource(http_client)
        >>> response = await resource.forward_get(action="status")
        >>> response = await resource.forward_post({"action": "provision", "data": {...}})
    """

    def __init__(self, http: HTTPClient):
        """
        Initialize provisioning resource manager.

        Args:
            http: HTTP client for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/provisioning",
            model_class=ProvisioningRequest,
            partial_class=PartialProvisioningRequest,
        )

    async def forward_get(self, **params: Any) -> dict[str, Any]:
        """
        Forward GET request to provisioning service.

        Sends query parameters directly to the provisioning service.

        Args:
            **params: Query parameters to forward (e.g., action="status").

        Returns:
            Response data from provisioning service.

        Example:
            >>> response = await resource.forward_get(action="status", id=123)
            >>> print(response)
        """
        response = await self._http.get(self._endpoint, params=params)
        data: dict[str, Any] = response.get("data", {})
        return data

    async def forward_post(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Forward POST request to provisioning service.

        Sends request body directly to the provisioning service.

        Args:
            data: Request body to forward to provisioning service.

        Returns:
            Response data from provisioning service.

        Example:
            >>> response = await resource.forward_post({
            ...     "action": "provision",
            ...     "customerId": 123,
            ...     "config": {...}
            ... })
            >>> print(response)
        """
        response = await self._http.post(self._endpoint, json=data)
        result: dict[str, Any] = response.get("data", {})
        return result
