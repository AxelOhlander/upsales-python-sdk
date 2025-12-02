"""Ad account models for Upsales API.

This module provides models for managing advertising account configuration.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Unpack

from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field

if TYPE_CHECKING:
    from typing import TypedDict

    class AdAccountUpdateFields(TypedDict, total=False):
        """Available fields for updating an AdAccount.

        All fields are optional to allow partial updates.
        """

        cpmAmount: float
        active: bool


class AdAccount(PydanticBaseModel):
    """Represents an advertising account configuration.

    This model contains configuration for advertising accounts including
    CPM amount and active status.

    Attributes:
        cpmAmount: Cost per thousand impressions amount (default: 300.0).
        active: Whether the account is active (default: True).
        values: Additional values associated with the account.

    Example:
        >>> account = AdAccount(cpmAmount=350.0, active=True)
        >>> print(account.cpmAmount)
        350.0
        >>> print(account.is_active)
        True
    """

    cpmAmount: float = Field(default=300.0, description="Cost per thousand impressions")
    active: bool = Field(default=True, description="Active status")
    values: dict[str, object] | None = Field(None, description="Additional values")
    _client: object | None = None

    @property
    def is_active(self) -> bool:
        """Check if the account is active.

        Returns:
            True if active, False otherwise.

        Example:
            >>> account = AdAccount(active=True)
            >>> account.is_active
            True
        """
        return self.active

    def to_api_dict(self, **overrides: object) -> dict[str, object]:
        """Convert model to API-compatible dictionary.

        Args:
            **overrides: Field values to override.

        Returns:
            Dictionary suitable for API requests.

        Example:
            >>> account = AdAccount(cpmAmount=300.0, active=True)
            >>> api_dict = account.to_api_dict(cpmAmount=400.0)
            >>> print(api_dict["cpmAmount"])
            400.0
        """
        data = self.model_dump(exclude={"_client"})
        data.update(overrides)
        return data

    async def edit(self, customer_id: int, **kwargs: Unpack[AdAccountUpdateFields]) -> AdAccount:
        """Edit this ad account with new field values.

        Allows updating any subset of allowed fields. Uses the configured
        client to perform the update operation.

        Args:
            customer_id: The customer ID for this account.
            **kwargs: Field values to update (cpmAmount, active).

        Returns:
            Updated AdAccount instance with new values from server.

        Raises:
            RuntimeError: If no client is available for the operation.

        Example:
            >>> account = await client.ad_accounts.get(customer_id=123)
            >>> updated = await account.edit(customer_id=123, cpmAmount=400.0)
            >>> print(updated.cpmAmount)
            400.0
        """
        if not self._client:
            raise RuntimeError("No client available")
        # Type ignore needed for dynamic client attribute
        return await self._client.ad_accounts.update(  # type: ignore[union-attr, return-value]
            customer_id=customer_id, **self.to_api_dict(**kwargs)
        )


class PartialAdAccount(PydanticBaseModel):
    """Partial ad account model for nested responses.

    Used when ad account data appears nested in other API responses
    with limited fields.

    Attributes:
        cpmAmount: Cost per thousand impressions amount.
        active: Whether the account is active.

    Example:
        >>> partial = PartialAdAccount(cpmAmount=300.0, active=True)
        >>> print(partial.cpmAmount)
        300.0
    """

    cpmAmount: float = Field(default=300.0, description="Cost per thousand impressions")
    active: bool = Field(default=True, description="Active status")
    _client: object | None = None

    async def fetch_full(self) -> AdAccount:
        """Fetch the complete ad account data.

        Returns:
            Full AdAccount instance with all fields populated.

        Raises:
            RuntimeError: If no client is available for the operation.

        Example:
            >>> partial = PartialAdAccount(cpmAmount=300.0)
            >>> full = await partial.fetch_full()
            >>> print(full.values)
        """
        # Note: adAccounts requires customer_id to fetch
        raise NotImplementedError("PartialAdAccount.fetch_full() requires customer_id parameter")

    async def edit(self, **kwargs: object) -> AdAccount:
        """Edit this ad account with new field values.

        Args:
            **kwargs: Field values to update.

        Returns:
            Updated AdAccount instance.

        Raises:
            RuntimeError: If no client is available for the operation.

        Example:
            >>> partial = PartialAdAccount(cpmAmount=300.0)
            >>> updated = await partial.edit(active=False)
        """
        # Note: adAccounts requires customer_id to update
        raise NotImplementedError("PartialAdAccount.edit() requires customer_id parameter")
