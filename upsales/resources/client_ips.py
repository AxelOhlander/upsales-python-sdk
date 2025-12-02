"""
ClientIps resource manager for Upsales API.

Manages client IP address whitelist rules for API access control.

Example:
    >>> async with Upsales(token="...") as upsales:
    ...     # Create new IP rule
    ...     ip = await upsales.client_ips.create(
    ...         ipAddress="192.168.1.1",
    ...         rule="allow",
    ...         userId=1
    ...     )
    ...     # List all IP rules
    ...     ips = await upsales.client_ips.list_all()
    ...     # Get specific user's IP rules
    ...     user_ips = await upsales.client_ips.list_all(userId=1)
"""

from upsales.http import HTTPClient
from upsales.models.client_ips import ClientIp, PartialClientIp
from upsales.resources.base import BaseResource


class ClientIpsResource(BaseResource[ClientIp, PartialClientIp]):
    """
    Resource manager for ClientIp endpoint.

    Manages IP address whitelist rules for API access control. Each rule
    specifies an IP address, access rule (allow/deny), and associated user.

    Inherits standard CRUD operations from BaseResource:
        - create(**data): Create new IP rule
        - get(id): Get single IP rule
        - list(limit, offset, **params): List IP rules with pagination
        - list_all(**params): Auto-paginated list of all IP rules
        - update(id, **data): Update IP rule
        - delete(id): Delete IP rule
        - bulk_update(ids, data, max_concurrent): Parallel updates
        - bulk_delete(ids, max_concurrent): Parallel deletes

    Example:
        >>> resource = ClientIpsResource(http_client)
        >>> # Create IP rule
        >>> ip = await resource.create(
        ...     ipAddress="192.168.1.1",
        ...     rule="allow",
        ...     userId=1
        ... )
        >>> # Get user's IP rules
        >>> user_ips = await resource.list_all(userId=1)
    """

    def __init__(self, http: HTTPClient):
        """
        Initialize ClientIps resource manager.

        Args:
            http: HTTP client for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/clientIps",
            model_class=ClientIp,
            partial_class=PartialClientIp,
        )

    async def get_by_user(self, user_id: int) -> list[ClientIp]:
        """
        Get all IP rules for a specific user.

        Args:
            user_id: User ID to filter by.

        Returns:
            List of ClientIp rules for the user.

        Example:
            >>> user_ips = await upsales.client_ips.get_by_user(1)
        """
        return await self.list_all(userId=user_id)
