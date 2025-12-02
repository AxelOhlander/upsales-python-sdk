"""Unsub model for Upsales API.

This module provides models for managing contact unsubscribe/resubscribe operations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Unpack

from pydantic import Field

from upsales.models.base import BaseModel, PartialModel

if TYPE_CHECKING:
    from typing import TypedDict

    class UnsubUpdateFields(TypedDict, total=False):
        """Available fields for updating an Unsub record.

        All fields are optional for updates.
        """

        pass  # No updatable fields for this endpoint


class Unsub(BaseModel):
    """Represents an unsubscribe record in Upsales.

    This model represents a contact's unsubscribe status for email communications.
    Use POST to unsubscribe and DELETE to resubscribe.

    Attributes:
        id: Unique identifier (contact ID).

    Example:
        ```python
        # Unsubscribe a contact
        unsub = await upsales.unsub.create(id=123)

        # Resubscribe a contact
        await upsales.unsub.delete(123)
        ```
    """

    id: int = Field(
        frozen=True,
        strict=True,
        description="Contact ID for unsubscribe record",
    )

    async def edit(self, **kwargs: Unpack[UnsubUpdateFields]) -> Unsub:
        """Edit this unsub record.

        This endpoint does not support updates. Use create() to unsubscribe
        or delete() to resubscribe.

        Args:
            **kwargs: Not applicable for this endpoint.

        Returns:
            Updated Unsub instance.

        Raises:
            RuntimeError: If no client is available.
            NotImplementedError: This endpoint does not support updates.
        """
        raise NotImplementedError(
            "Unsub endpoint does not support updates. "
            "Use create() to unsubscribe or delete() to resubscribe."
        )


class PartialUnsub(PartialModel):
    """Partial Unsub model for nested references.

    Used when an unsub record appears in API responses as a nested object.

    Attributes:
        id: Contact ID.

    Example:
        ```python
        # Fetch full unsub record
        full = await partial_unsub.fetch_full()
        ```
    """

    id: int = Field(description="Contact ID")

    async def fetch_full(self) -> Unsub:
        """Fetch the complete Unsub object.

        Returns:
            Full Unsub instance with all fields populated.

        Raises:
            RuntimeError: If no client is available.
            NotFoundError: If the unsub record does not exist.
        """
        if not self._client:
            raise RuntimeError("No client available for this partial model")
        return await self._client.unsub.get(self.id)

    async def edit(self, **kwargs: Unpack[UnsubUpdateFields]) -> Unsub:
        """Edit this unsub record.

        This endpoint does not support updates. Use create() to unsubscribe
        or delete() to resubscribe.

        Args:
            **kwargs: Not applicable for this endpoint.

        Returns:
            Updated Unsub instance.

        Raises:
            RuntimeError: If no client is available.
            NotImplementedError: This endpoint does not support updates.
        """
        raise NotImplementedError(
            "Unsub endpoint does not support updates. "
            "Use create() to unsubscribe or delete() to resubscribe."
        )
