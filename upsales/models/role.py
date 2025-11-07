"""
Role models for Upsales API.

Simple PartialRole for nested objects (e.g., User.role).
Provides type-safe access to role data in user responses.

Note:
    This is a minimal model for nested role objects. For full Role CRUD
    operations, would need to implement full Role model and RolesResource.

Example:
    >>> user = await upsales.users.get(1)
    >>> if user.role:
    ...     print(f"Role: {user.role.name}")  # ✅ Type-safe!
"""

from typing import TYPE_CHECKING, Any

from pydantic import Field

from upsales.models.base import PartialModel
from upsales.validators import NonEmptyStr

if TYPE_CHECKING:
    from upsales.models.base import BaseModel


class PartialRole(PartialModel):
    """
    Partial Role model for nested responses.

    Minimal role information included when role appears nested
    in other API responses (e.g., User.role).

    Typically includes just id and name from the API.

    Example:
        >>> user = await upsales.users.get(1)
        >>> if user.role:
        ...     print(f"User role: {user.role.name}")
        ...     print(f"Role ID: {user.role.id}")
    """

    id: int = Field(frozen=True, strict=True, description="Unique role ID")
    name: NonEmptyStr = Field(description="Role name")
    description: str | None = Field(None, description="Role description")

    async def fetch_full(self) -> "BaseModel":
        """
        Fetch full role data.

        Note:
            Full Role model not yet implemented. This returns self.
            Implement full Role model and RolesResource for full CRUD.

        Returns:
            Self (partial role).

        Example:
            >>> role = user.role  # PartialRole
            >>> # full_role = await role.fetch_full()  # Would need RolesResource
        """
        # TODO: Implement when RolesResource is created
        if not self._client:
            raise RuntimeError("No client available")
        raise NotImplementedError(
            "Full Role model not yet implemented. Add RolesResource to enable full CRUD operations."
        )

    async def edit(self, **kwargs: Any) -> "BaseModel":
        """
        Edit this role.

        Note:
            Full Role model not yet implemented. This raises NotImplementedError.
            Implement full Role model and RolesResource for full CRUD.

        Args:
            **kwargs: Fields to update.

        Returns:
            Updated role.

        Raises:
            NotImplementedError: Until RolesResource is implemented.
        """
        # TODO: Implement when RolesResource is created
        if not self._client:
            raise RuntimeError("No client available")
        raise NotImplementedError(
            "Full Role model not yet implemented. Add RolesResource to enable role updates."
        )
