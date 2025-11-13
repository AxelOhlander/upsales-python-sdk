"""
ClientCategory models for Upsales API.

Generated from /api/v2/client_categories endpoint.
Analysis based on 2 samples.

Enhanced with Pydantic v2 features:
- Reusable validators
- Computed fields (@computed_field)
- Field serialization
- Strict type checking
- Field descriptions
- Optimized serialization
"""

from typing import Any, TypedDict, Unpack

from pydantic import Field, computed_field

from upsales.models.base import BaseModel, PartialModel
from upsales.models.roles import PartialRole
from upsales.validators import NonEmptyStr


class ClientCategoryUpdateFields(TypedDict, total=False):
    """
    Available fields for updating a ClientCategory.

    All fields are optional. Use with Unpack for IDE autocomplete.
    """

    name: str
    categoryType: int
    roles: list[dict[str, Any]]


class ClientCategory(BaseModel):
    """
    ClientCategory model from /api/v2/client_categories.

    Represents a client/company category in the Upsales system for organizing clients.
    Enhanced with Pydantic v2 validators, computed fields, and optimized serialization.

    Generated from 2 samples with field analysis.

    Example:
        >>> category = await upsales.client_categories.get(1)
        >>> category.name
        'Övrigt'
        >>> category.has_roles
        False
        >>> await category.edit(name="Updated Category")
    """

    # Read-only fields
    id: int = Field(frozen=True, strict=True, description="Unique client category ID")

    # Required fields with validators
    name: NonEmptyStr = Field(description="Category name")
    categoryType: int = Field(description="Category type identifier")

    # Optional fields
    roles: list[PartialRole] = Field(
        default_factory=list, description="Roles associated with this category"
    )

    @computed_field
    @property
    def has_roles(self) -> bool:
        """
        Check if category has associated roles.

        Returns:
            True if category has roles assigned, False otherwise.

        Example:
            >>> category.has_roles
            True
        """
        return len(self.roles) > 0

    @computed_field
    @property
    def role_count(self) -> int:
        """
        Count of roles associated with this category.

        Returns:
            Number of roles assigned to this category.

        Example:
            >>> category.role_count
            3
        """
        return len(self.roles)

    async def edit(self, **kwargs: Unpack[ClientCategoryUpdateFields]) -> "ClientCategory":
        """
        Edit this client category.

        Uses Pydantic v2's optimized serialization via to_api_dict().
        With Python 3.13 free-threaded mode, multiple edits can run
        in true parallel without GIL contention.

        Args:
            **kwargs: Fields to update (from ClientCategoryUpdateFields).

        Returns:
            Updated ClientCategory object from API.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> category = await upsales.client_categories.get(1)
            >>> updated = await category.edit(
            ...     name="Updated Category",
            ...     categoryType=1
            ... )
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.client_categories.update(self.id, **self.to_api_dict(**kwargs))


class PartialClientCategory(PartialModel):
    """
    Partial ClientCategory for nested responses.

    Contains minimal client category data when category appears nested in other objects
    (e.g., account.category). Use fetch_full() to get complete category data.

    Example:
        >>> account = await upsales.accounts.get(1)
        >>> account.category.name  # Partial data
        'Övrigt'
        >>> full_category = await account.category.fetch_full()  # Fetch complete
        >>> full_category.has_roles
        False
    """

    id: int = Field(description="Unique client category ID")
    name: str = Field(description="Category name")

    async def fetch_full(self) -> ClientCategory:
        """
        Fetch full client category data from API.

        Returns:
            Complete ClientCategory object with all fields.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> full_category = await partial_category.fetch_full()
            >>> full_category.has_roles
            True
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.client_categories.get(self.id)

    async def edit(self, **kwargs: Unpack[ClientCategoryUpdateFields]) -> ClientCategory:
        """
        Edit this client category.

        Args:
            **kwargs: Fields to update (from ClientCategoryUpdateFields).

        Returns:
            Updated ClientCategory object from API.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> updated = await partial_category.edit(name="Updated")
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.client_categories.update(self.id, **kwargs)
