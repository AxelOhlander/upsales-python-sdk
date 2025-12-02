"""
ClientIp models for Upsales API.

Manages client IP address whitelist rules for API access control.

Example:
    >>> async with Upsales(token="...") as upsales:
    ...     # Create new IP rule
    ...     ip = await upsales.client_ips.create(
    ...         ipAddress="192.168.1.1",
    ...         rule="allow",
    ...         userId=1
    ...     )
    ...     # Update rule
    ...     await ip.edit(rule="deny")
"""

from typing import TypedDict, Unpack

from pydantic import Field

from upsales.models.base import BaseModel, PartialModel
from upsales.validators import PositiveInt


class ClientIpUpdateFields(TypedDict, total=False):
    """
    Available fields for updating a ClientIp.

    All fields are optional when updating.
    """

    rule: str
    ipAddress: str
    userId: int
    sortIdx: int


class ClientIp(BaseModel):
    """
    Client IP address whitelist rule.

    Used to control API access by IP address. Each rule specifies an IP address,
    whether it should be allowed or denied, and which user it belongs to.

    Attributes:
        id: Unique identifier for the IP rule.
        ipAddress: IP address (max 16 chars, supports IPv4).
        rule: Access rule type, either "allow" or "deny" (max 8 chars).
        userId: User ID this IP rule belongs to.
        sortIdx: Sort index for display ordering.
        clientId: Client (account) ID this IP rule belongs to.
    """

    # Read-only fields
    id: int = Field(frozen=True, strict=True, description="Unique identifier")
    clientId: int | None = Field(None, frozen=True, description="Client account ID")

    # Updatable fields
    ipAddress: str = Field(max_length=16, description="IP address")
    rule: str = Field(max_length=8, description="Access rule (allow/deny)")
    userId: int = Field(description="User ID")
    sortIdx: PositiveInt = Field(default=0, description="Sort index")

    async def edit(self, **kwargs: Unpack[ClientIpUpdateFields]) -> "ClientIp":
        """
        Edit this client IP rule.

        Args:
            **kwargs: Fields to update (rule, ipAddress, userId, sortIdx).

        Returns:
            Updated ClientIp instance.

        Raises:
            RuntimeError: If no client is available.

        Example:
            >>> ip = await upsales.client_ips.get(1)
            >>> await ip.edit(rule="deny")
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.client_ips.update(self.id, **self.to_api_dict(**kwargs))


class PartialClientIp(PartialModel):
    """
    Partial ClientIp for nested responses.

    Contains minimal fields for ClientIp references in other resources.

    Attributes:
        id: Unique identifier.
        ipAddress: IP address.
    """

    id: int = Field(description="Unique identifier")
    ipAddress: str | None = Field(None, description="IP address")

    async def fetch_full(self) -> ClientIp:
        """
        Fetch complete ClientIp data.

        Returns:
            Full ClientIp instance.

        Raises:
            RuntimeError: If no client is available.
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.client_ips.get(self.id)

    async def edit(self, **kwargs: Unpack[ClientIpUpdateFields]) -> ClientIp:
        """
        Edit this client IP rule.

        Args:
            **kwargs: Fields to update.

        Returns:
            Updated ClientIp instance.

        Raises:
            RuntimeError: If no client is available.
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.client_ips.update(self.id, **kwargs)
