"""Market rejectlist models for Upsales API.

This module provides models for managing rejected companies for marketing campaigns.
"""

from __future__ import annotations

from typing import TypedDict, Unpack

from pydantic import Field, computed_field

from upsales.models.base import BaseModel, PartialModel


class MarketRejectlistUpdateFields(TypedDict, total=False):
    """Available fields for updating a MarketRejectlist entry.

    All fields are optional for updates. Use this TypedDict for IDE autocomplete
    and type checking in the edit() method.
    """

    name: str
    dunsNo: str
    organisationId: str
    clientId: int


class MarketRejectlist(BaseModel):
    """A market rejectlist entry for rejected companies in marketing campaigns.

    This model represents a company that should be excluded from marketing campaigns.
    Companies can be identified by name, DUNS number, organisation ID, or client ID.

    Attributes:
        id: Unique identifier for the rejectlist entry.
        name: Company name (optional).
        dunsNo: DUNS number for the company (optional).
        organisationId: Organisation identifier (optional).
        clientId: Client (account) ID (optional).

    Example:
        Create a new rejectlist entry:
        ```python
        entry = await upsales.market_rejectlist.create(
            name="ACME Corp",
            dunsNo="123456789"
        )
        print(f"Rejected: {entry.name}")
        ```

        Get and edit an entry:
        ```python
        entry = await upsales.market_rejectlist.get(1)
        await entry.edit(name="Updated Name")
        ```
    """

    # Read-only fields
    id: int = Field(frozen=True, strict=True, description="Unique rejectlist entry ID", gt=0)

    # Updatable fields - all optional since any combination can identify a company
    name: str | None = Field(None, description="Company name")
    dunsNo: str | None = Field(None, description="DUNS number")
    organisationId: str | None = Field(None, description="Organisation identifier")
    clientId: int | None = Field(None, description="Client (account) ID", gt=0)

    @computed_field
    @property
    def has_identifier(self) -> bool:
        """Check if entry has at least one identifier.

        Returns:
            True if at least one identifying field is set, False otherwise.

        Example:
            ```python
            entry = MarketRejectlist(id=1, name="ACME Corp")
            print(entry.has_identifier)  # True
            ```
        """
        return any([self.name, self.dunsNo, self.organisationId, self.clientId])

    async def edit(self, **kwargs: Unpack[MarketRejectlistUpdateFields]) -> MarketRejectlist:
        """Edit this rejectlist entry with provided fields.

        This method provides full IDE autocomplete for all updatable fields.

        Args:
            **kwargs: Fields to update (name, dunsNo, organisationId, clientId).

        Returns:
            Updated MarketRejectlist instance.

        Raises:
            RuntimeError: If no client is available.

        Example:
            ```python
            entry = await upsales.market_rejectlist.get(1)
            updated = await entry.edit(name="New Name", dunsNo="987654321")
            print(updated.name)  # "New Name"
            ```
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.market_rejectlist.update(self.id, **self.to_api_dict(**kwargs))

    async def delete(self) -> None:
        """Delete this rejectlist entry.

        Raises:
            RuntimeError: If no client is available.

        Example:
            ```python
            entry = await upsales.market_rejectlist.get(1)
            await entry.delete()
            ```
        """
        if not self._client:
            raise RuntimeError("No client available")
        await self._client.market_rejectlist.delete(self.id)


class PartialMarketRejectlist(PartialModel):
    """Partial market rejectlist entry returned in nested responses.

    This lightweight model is used when rejectlist entries appear as nested objects
    in other API responses. It contains only the essential identifying fields.

    Attributes:
        id: Unique identifier for the rejectlist entry.
        name: Company name (optional).

    Example:
        Fetch full details:
        ```python
        partial = PartialMarketRejectlist(id=1, name="ACME Corp")
        full = await partial.fetch_full()
        print(full.dunsNo)
        ```
    """

    id: int = Field(description="Unique rejectlist entry ID", gt=0)
    name: str | None = Field(None, description="Company name")

    async def fetch_full(self) -> MarketRejectlist:
        """Fetch the complete MarketRejectlist object.

        Returns:
            Full MarketRejectlist instance with all fields.

        Raises:
            RuntimeError: If no client is available.

        Example:
            ```python
            partial = PartialMarketRejectlist(id=1)
            full = await partial.fetch_full()
            print(full.dunsNo)
            ```
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.market_rejectlist.get(self.id)

    async def edit(self, **kwargs: Unpack[MarketRejectlistUpdateFields]) -> MarketRejectlist:
        """Edit this rejectlist entry with provided fields.

        Args:
            **kwargs: Fields to update.

        Returns:
            Updated MarketRejectlist instance.

        Raises:
            RuntimeError: If no client is available.

        Example:
            ```python
            partial = PartialMarketRejectlist(id=1)
            updated = await partial.edit(name="New Name")
            ```
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.market_rejectlist.update(self.id, **kwargs)

    async def delete(self) -> None:
        """Delete this rejectlist entry.

        Raises:
            RuntimeError: If no client is available.

        Example:
            ```python
            partial = PartialMarketRejectlist(id=1)
            await partial.delete()
            ```
        """
        if not self._client:
            raise RuntimeError("No client available")
        await self._client.market_rejectlist.delete(self.id)
