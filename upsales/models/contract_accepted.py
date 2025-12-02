"""
Contract Accepted models for Upsales API.

Records of user acceptance of contract terms at /api/v2/contractAccepted.

Note:
    This endpoint records contract acceptance events. Most fields are
    auto-populated by the system including user details, IP, version, etc.
    Only contractId is required when creating a new acceptance record.

Enhanced with Pydantic v2 features:
- Field descriptions for all fields
- Computed field for date parsing
- Strict type checking for read-only fields
- Optimized serialization
"""

from typing import TypedDict, Unpack

from pydantic import Field, computed_field

from upsales.models.base import BaseModel, PartialModel


class ContractAcceptedUpdateFields(TypedDict, total=False):
    """
    Available fields for updating a Contract Accepted record.

    All fields are optional. Use with Unpack for IDE autocomplete.

    Note:
        Most fields are auto-populated and read-only. Updates are rare.
    """

    contractId: int
    customerId: int
    userId: int
    body: str
    version: str


class ContractAccepted(BaseModel):
    """
    Contract Accepted model from /api/v2/contractAccepted.

    Represents a record of a user accepting contract terms. These records
    are typically created automatically when users accept agreements, with
    most fields auto-populated by the system.

    Auto-populated fields include: version, body, user_id, master_user_id,
    customer_id, user_email, user_name, user_ip, and date.

    Example:
        >>> contract = await upsales.contract_accepted.get(1)
        >>> contract.contractId
        123
        >>> contract.date
        '2024-01-15 10:30:45'
        >>> contract.has_date
        True
    """

    # Read-only fields (frozen=True, strict=True)
    id: int = Field(frozen=True, strict=True, description="Unique contract acceptance record ID")

    # Required fields
    contractId: int = Field(description="ID of the contract that was accepted")

    # Optional fields (most are auto-populated)
    customerId: int | None = Field(None, description="Customer ID (auto-populated)")
    userId: int | None = Field(None, description="User ID who accepted (auto-populated)")
    body: str | None = Field(None, description="Contract body text (auto-populated)")
    version: str | None = Field(None, description="Contract version (auto-populated)")
    date: str | None = Field(None, description="Acceptance date/time (auto-populated)")

    @computed_field
    @property
    def has_date(self) -> bool:
        """
        Check if acceptance date is recorded.

        Returns:
            True if date field is present and non-empty.

        Example:
            >>> contract.has_date
            True
        """
        return bool(self.date)

    async def edit(self, **kwargs: Unpack[ContractAcceptedUpdateFields]) -> "ContractAccepted":
        """
        Edit this contract acceptance record.

        Uses Pydantic v2's optimized serialization via to_api_dict().

        Args:
            **kwargs: Fields to update (full IDE autocomplete support).

        Returns:
            Updated contract acceptance record with fresh data from API.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> contract = await upsales.contract_accepted.get(1)
            >>> updated = await contract.edit(
            ...     version="2.0"
            ... )
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.contract_accepted.update(self.id, **self.to_api_dict(**kwargs))


class PartialContractAccepted(PartialModel):
    """
    Partial Contract Accepted for nested responses.

    Contains minimal fields for when contract acceptance records appear
    nested in other API responses.

    Use fetch_full() to get complete ContractAccepted object with all fields.

    Example:
        >>> # If contract acceptance appeared nested somewhere
        >>> partial = some_object.contract_accepted  # PartialContractAccepted
        >>> full = await partial.fetch_full()  # Now ContractAccepted
    """

    id: int = Field(frozen=True, strict=True, description="Unique contract acceptance record ID")
    contractId: int = Field(description="ID of the contract that was accepted")
    date: str | None = Field(None, description="Acceptance date/time (auto-populated)")

    async def fetch_full(self) -> ContractAccepted:
        """
        Fetch complete contract acceptance record data.

        Returns:
            Full ContractAccepted object with all fields populated.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> partial = some_object.contract_accepted  # PartialContractAccepted
            >>> full = await partial.fetch_full()  # ContractAccepted
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.contract_accepted.get(self.id)

    async def edit(self, **kwargs: Unpack[ContractAcceptedUpdateFields]) -> ContractAccepted:
        """
        Edit this contract acceptance record.

        Returns full ContractAccepted object after update.

        Args:
            **kwargs: Fields to update (full IDE autocomplete support).

        Returns:
            Updated full ContractAccepted object.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> partial = some_object.contract_accepted  # PartialContractAccepted
            >>> updated = await partial.edit(version="2.0")  # Returns ContractAccepted
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.contract_accepted.update(self.id, **kwargs)


__all__ = [
    "ContractAccepted",
    "ContractAcceptedUpdateFields",
    "PartialContractAccepted",
]
