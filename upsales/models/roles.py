"""
Role models for Upsales API.

Generated from /api/v2/roles endpoint.
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
from upsales.validators import NonEmptyStr


class RoleUpdateFields(TypedDict, total=False):
    """
    Available fields for updating a Role.

    All fields are optional. Use with Unpack for IDE autocomplete.
    """

    name: str
    description: str
    defaultCurrency: str | None
    defaultSalesboardId: Any
    template: int
    hasDiscount: bool
    parent: dict[str, Any]


class Role(BaseModel):
    """
    Role model from /api/v2/roles.

    Represents a user role in the Upsales system with permissions and settings.
    Enhanced with Pydantic v2 validators, computed fields, and optimized serialization.

    Generated from 2 samples with field analysis.

    Example:
        >>> role = await upsales.roles.get(1)
        >>> role.name
        'Sales Manager'
        >>> role.has_discount
        True
        >>> await role.edit(description="Updated role")
    """

    # Read-only fields
    id: int = Field(frozen=True, strict=True, description="Unique role ID")

    # Required fields with validators
    name: NonEmptyStr = Field(description="Role name")
    description: str = Field(default="", description="Role description")

    # Role settings
    defaultCurrency: str | None = Field(
        default=None, description="Default currency code for this role (null for some roles)"
    )
    template: int = Field(description="Template ID for role configuration")
    hasDiscount: bool = Field(default=False, description="Whether role can apply discounts")

    # Optional fields
    defaultSalesboardId: int | None = Field(
        default=None, description="Default salesboard ID for this role"
    )
    parent: dict[str, Any] | None = Field(
        default=None, description="Parent role information (structure varies)"
    )

    @computed_field
    @property
    def has_parent(self) -> bool:
        """
        Check if role has a parent role.

        Returns:
            True if role has parent role defined, False otherwise.

        Example:
            >>> role.has_parent
            True
        """
        return self.parent is not None and bool(self.parent)

    @computed_field
    @property
    def can_discount(self) -> bool:
        """
        Check if role can apply discounts.

        Returns:
            True if hasDiscount is True, False otherwise.

        Example:
            >>> role.can_discount
            True
        """
        return self.hasDiscount

    async def edit(self, **kwargs: Unpack[RoleUpdateFields]) -> "Role":
        """
        Edit this role.

        Uses Pydantic v2's optimized serialization via to_api_dict().

        Args:
            **kwargs: Fields to update (from RoleUpdateFields).

        Returns:
            Updated Role object from API.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> role = await upsales.roles.get(1)
            >>> updated = await role.edit(
            ...     name="Updated Role",
            ...     description="New description"
            ... )
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.roles.update(self.id, **self.to_api_dict(**kwargs))


class PartialRole(PartialModel):
    """
    Partial Role for nested responses.

    Contains minimal role data when role appears nested in other objects
    (e.g., user.role). Use fetch_full() to get complete role data.

    Example:
        >>> user = await upsales.users.get(1)
        >>> user.role.name  # Partial data
        'Sales Manager'
        >>> full_role = await user.role.fetch_full()  # Fetch complete
        >>> full_role.hasDiscount
        True
    """

    id: int = Field(description="Unique role ID")
    name: str = Field(description="Role name")

    async def fetch_full(self) -> Role:
        """
        Fetch full role data from API.

        Returns:
            Complete Role object with all fields.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> full_role = await partial_role.fetch_full()
            >>> full_role.hasDiscount
            True
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.roles.get(self.id)

    async def edit(self, **kwargs: Unpack[RoleUpdateFields]) -> Role:
        """
        Edit this role.

        Args:
            **kwargs: Fields to update (from RoleUpdateFields).

        Returns:
            Updated Role object from API.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> updated = await partial_role.edit(description="Updated")
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.roles.update(self.id, **kwargs)
