"""Models for engageCreditTransaction endpoint.

This module provides models for ad credit transaction history in the Upsales CRM API.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Unpack

from pydantic import Field, computed_field

from upsales.models.base import BaseModel, PartialModel
from upsales.models.custom_fields import CustomFields
from upsales.validators import CustomFieldsList, NonEmptyStr

if TYPE_CHECKING:
    from typing_extensions import TypedDict

    class EngageCreditTransactionUpdateFields(TypedDict, total=False):
        """Available fields for updating an EngageCreditTransaction.

        All fields are optional when updating. Only provided fields will be updated.
        """

        value: float
        description: str
        date: str
        campaignId: int
        custom: list[dict[str, Any]]


class EngageCreditTransaction(BaseModel):
    """Represents an ad credit transaction in the Upsales CRM system.

    This model includes all fields returned by the API for engage credit transactions,
    including transaction value, description, date, and associated campaign.

    Attributes:
        id: Unique transaction ID (read-only)
        value: Transaction value
        description: Transaction description
        date: Transaction date (format: YYYY-MM-DD)
        campaignId: Associated campaign ID
        custom: Custom fields list

    Example:
        >>> # Get a transaction
        >>> transaction = await upsales.engage_credit_transactions.get(123)
        >>> print(transaction.value)
        100.0
        >>> print(transaction.description)
        "Ad credit purchase"

        >>> # Update a transaction
        >>> await transaction.edit(description="Updated description")

        >>> # Access custom fields
        >>> transaction.custom_fields.get_by_id(11)
        "custom value"
    """

    # Read-only fields
    id: int = Field(frozen=True, strict=True, description="Unique transaction ID")

    # Updatable fields
    value: float = Field(description="Transaction value")
    description: NonEmptyStr = Field(description="Transaction description")
    date: str | None = Field(None, description="Transaction date (YYYY-MM-DD)")
    campaignId: int | None = Field(None, description="Associated campaign ID")
    custom: CustomFieldsList = Field(default=[], description="Custom fields")

    @computed_field
    @property
    def custom_fields(self) -> CustomFields:
        """Access custom fields with dict-like interface.

        Returns:
            CustomFields instance providing access by ID or alias.

        Example:
            >>> transaction.custom_fields.get_by_id(11)
            "custom value"
            >>> transaction.custom_fields.get_by_alias("FIELD_ALIAS")
            "custom value"
        """
        return CustomFields(self.custom)

    async def edit(
        self, **kwargs: Unpack[EngageCreditTransactionUpdateFields]
    ) -> EngageCreditTransaction:
        """Edit this engage credit transaction with type-safe field updates.

        Args:
            **kwargs: Fields to update (value, description, date, campaignId, custom)

        Returns:
            Updated EngageCreditTransaction instance

        Raises:
            RuntimeError: If no client is available
            ValidationError: If provided data fails validation
            NotFoundError: If transaction doesn't exist
            AuthenticationError: If API token is invalid

        Example:
            >>> transaction = await upsales.engage_credit_transactions.get(123)
            >>> # Update with full IDE autocomplete
            >>> updated = await transaction.edit(
            ...     description="Updated description",
            ...     value=150.0
            ... )
            >>> print(updated.description)
            "Updated description"

        Note:
            Only provided fields will be updated. Frozen fields (id) are
            automatically excluded from the update payload.
        """
        if not self._client:
            raise RuntimeError("No client available for this instance")
        return await self._client.engage_credit_transactions.update(
            self.id, **self.to_api_dict(**kwargs)
        )


class PartialEngageCreditTransaction(PartialModel):
    """Minimal representation of an engage credit transaction.

    Used when engage credit transactions appear as nested objects in other API responses.
    Contains only essential identifying information.

    Attributes:
        id: Unique transaction ID
        value: Transaction value
        description: Transaction description

    Example:
        >>> # From nested response
        >>> partial = some_object.transaction
        >>> print(partial.description)
        "Ad credit purchase"

        >>> # Fetch full details
        >>> full = await partial.fetch_full()
        >>> print(full.date)
        "2025-01-15"

        >>> # Edit directly
        >>> updated = await partial.edit(value=200.0)
    """

    id: int = Field(description="Unique transaction ID")
    value: float | None = Field(None, description="Transaction value")
    description: str | None = Field(None, description="Transaction description")

    async def fetch_full(self) -> EngageCreditTransaction:
        """Fetch complete engage credit transaction details from the API.

        Returns:
            Full EngageCreditTransaction instance with all fields

        Raises:
            RuntimeError: If no client is available
            NotFoundError: If transaction doesn't exist
            AuthenticationError: If API token is invalid

        Example:
            >>> partial = some_object.transaction
            >>> full = await partial.fetch_full()
            >>> print(full.campaignId)
            456
        """
        if not self._client:
            raise RuntimeError("No client available for this instance")
        return await self._client.engage_credit_transactions.get(self.id)

    async def edit(self, **kwargs: Any) -> EngageCreditTransaction:
        """Edit this engage credit transaction.

        Args:
            **kwargs: Fields to update

        Returns:
            Updated full EngageCreditTransaction instance

        Raises:
            RuntimeError: If no client is available
            ValidationError: If provided data fails validation
            NotFoundError: If transaction doesn't exist
            AuthenticationError: If API token is invalid

        Example:
            >>> partial = some_object.transaction
            >>> updated = await partial.edit(value=200.0)
            >>> print(updated.value)
            200.0
        """
        if not self._client:
            raise RuntimeError("No client available for this instance")
        return await self._client.engage_credit_transactions.update(self.id, **kwargs)
