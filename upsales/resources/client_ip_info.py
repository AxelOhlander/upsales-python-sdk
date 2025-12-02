"""Resource manager for clientIpInfo endpoint.

This module provides the resource manager for checking client IP information
for ad tracking purposes.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from upsales.models.client_ip_info import ClientIpInfo
from upsales.resources.base import BaseResource

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class ClientIpInfoResource(BaseResource[ClientIpInfo, ClientIpInfo]):
    """Resource manager for client IP information checks.

    This resource provides functionality to check client IP information
    for ad tracking purposes.

    Example:
        >>> async with Upsales.from_env() as upsales:
        ...     result = await upsales.client_ip_info.check(target=["192.168.1.1"])
        ...     print(result.allowed)
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize the ClientIpInfo resource manager.

        Args:
            http: HTTP client for making API requests.
        """
        super().__init__(
            http=http,
            endpoint="/function/clientIpInfo",
            model_class=ClientIpInfo,
            partial_class=ClientIpInfo,
        )

    async def check(self, target: list[str]) -> ClientIpInfo:
        """Check client IP information for ad tracking.

        Args:
            target: Array of IP addresses or identifiers to check.

        Returns:
            ClientIpInfo object containing the check results.

        Raises:
            ValidationError: If the request parameters are invalid.
            ServerError: If the server returns an error.

        Example:
            >>> result = await upsales.client_ip_info.check(
            ...     target=["192.168.1.1", "10.0.0.1"]
            ... )
            >>> if result.allowed:
            ...     print("IP tracking is allowed")
            >>> else:
            ...     print(f"IP tracking blocked: {result.message}")
        """
        request_kwargs = self._prepare_http_kwargs()
        response = await self._http.post(
            self._endpoint,
            **request_kwargs,
            json={"target": target},
        )
        return self._model_class(
            **response["data"],
            _client=self._http._upsales_client,
        )

    async def create(self, **data: Any) -> ClientIpInfo:
        """Create not supported for clientIpInfo.

        Use check() method instead.

        Raises:
            NotImplementedError: This endpoint does not support create operations.
        """
        raise NotImplementedError(
            "clientIpInfo does not support create. Use check() method instead."
        )

    async def get(self, id: int) -> ClientIpInfo:  # noqa: A002 - matches API naming
        """Get not supported for clientIpInfo.

        This endpoint is function-based and does not support retrieval by ID.

        Raises:
            NotImplementedError: This endpoint does not support get operations.
        """
        raise NotImplementedError("clientIpInfo does not support get operations")

    async def list(
        self,
        limit: int = 100,
        offset: int = 0,
        **params: Any,
    ) -> list[ClientIpInfo]:
        """List not supported for clientIpInfo.

        This endpoint is function-based and does not support listing.

        Raises:
            NotImplementedError: This endpoint does not support list operations.
        """
        raise NotImplementedError("clientIpInfo does not support list operations")

    async def update(self, id: int, **data: Any) -> ClientIpInfo:  # noqa: A002 - matches API naming
        """Update not supported for clientIpInfo.

        Raises:
            NotImplementedError: This endpoint does not support update operations.
        """
        raise NotImplementedError("clientIpInfo does not support update operations")

    async def delete(self, id: int) -> None:  # noqa: A002 - matches API naming
        """Delete not supported for clientIpInfo.

        Raises:
            NotImplementedError: This endpoint does not support delete operations.
        """
        raise NotImplementedError("clientIpInfo does not support delete operations")
