"""Models for clientIpInfo endpoint - Check client IP information for ad tracking.

This module provides models for the clientIpInfo endpoint which checks
client IP information for ad tracking purposes.
"""

from __future__ import annotations

from typing import Any

from pydantic import Field

from upsales.models.base import BaseModel


class ClientIpInfo(BaseModel):
    """Client IP information response.

    This model represents the response from checking client IP information
    for ad tracking purposes.

    Attributes:
        target: Array of target information
        allowed: Whether the IP is allowed for tracking
        message: Optional message about the IP status
    """

    id: int = Field(default=0, frozen=True, description="Static identifier for client IP info")
    target: list[Any] = Field(description="Array of target information")
    allowed: bool = Field(description="Whether the IP is allowed for tracking")
    message: str | None = Field(None, description="Optional message about IP status")

    async def edit(self, **kwargs: Any) -> ClientIpInfo:
        """Edit not supported for clientIpInfo.

        This endpoint is read-only and does not support updates.

        Raises:
            NotImplementedError: This endpoint does not support edit operations.
        """
        raise NotImplementedError("clientIpInfo endpoint does not support edit operations")
