"""ResetScore models for Upsales API.

This module provides models for the resetScore endpoint, which resets
marketing scores for clients or contacts.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field

from upsales.models.base import PartialModel


class ResetScoreRequest(PydanticBaseModel):
    """Request model for resetting marketing score.

    Attributes:
        userId: User ID who performs the reset (required)
        clientId: Client ID to reset score for (optional, mutually exclusive with contactId)
        contactId: Contact ID to reset score for (optional, mutually exclusive with clientId)
        sync: Whether to synchronize the operation (optional, defaults to False)

    Note:
        Either clientId or contactId must be provided, but not both.

    Example:
        >>> request = ResetScoreRequest(userId=1, clientId=100)
        >>> request = ResetScoreRequest(userId=1, contactId=200, sync=True)
    """

    userId: int = Field(description="User ID performing the reset")
    clientId: int | None = Field(None, description="Client ID to reset score for")
    contactId: int | None = Field(None, description="Contact ID to reset score for")
    sync: bool = Field(False, description="Synchronize the operation")


class ResetScoreResponse(PydanticBaseModel):
    """Response model for resetScore operation.

    Attributes:
        success: Whether the operation was successful
        message: Optional message about the operation

    Example:
        >>> response = ResetScoreResponse(success=True, message="Score reset successfully")
    """

    success: bool = Field(description="Operation success status")
    message: str | None = Field(None, description="Operation message")


class PartialResetScore(PartialModel):
    """Minimal ResetScore model for nested references.

    Attributes:
        success: Whether the operation was successful

    Example:
        >>> partial = PartialResetScore(success=True)
    """

    success: bool = Field(description="Operation success status")

    async def fetch_full(self) -> ResetScoreResponse:
        """Fetch full ResetScore details.

        Returns:
            Full ResetScore model

        Raises:
            RuntimeError: If no client is available
            NotImplementedError: This endpoint doesn't support fetching

        Note:
            The resetScore endpoint is action-only and doesn't support
            fetching individual records.
        """
        raise NotImplementedError("resetScore is an action endpoint and doesn't support fetching")

    async def edit(self, **kwargs: Any) -> ResetScoreResponse:
        """Edit this reset score.

        Args:
            **kwargs: Fields to update

        Returns:
            Updated ResetScore model

        Raises:
            RuntimeError: If no client is available
            NotImplementedError: This endpoint doesn't support editing

        Note:
            The resetScore endpoint is action-only and doesn't support editing.
        """
        raise NotImplementedError("resetScore is an action endpoint and doesn't support editing")
