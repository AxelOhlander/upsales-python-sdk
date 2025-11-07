"""
Category models for Upsales API.

Simple PartialCategory for nested objects (e.g., Product.category).
Provides type-safe access to category data in product responses.

Example:
    >>> product = await upsales.products.get(1)
    >>> if product.category:
    ...     print(f"Category: {product.category.name}")  # ✅ Type-safe!
"""

from typing import TYPE_CHECKING, Any

from pydantic import Field

from upsales.models.base import PartialModel
from upsales.validators import NonEmptyStr

if TYPE_CHECKING:
    from upsales.models.base import BaseModel


class PartialCategory(PartialModel):
    """
    Partial Category model for nested responses.

    Minimal category information included when category appears nested
    in product responses.

    Example:
        >>> product = await upsales.products.get(1)
        >>> if product.category:
        ...     print(f"Category: {product.category.name}")
        ...     category_id = product.category.id
    """

    id: int = Field(frozen=True, strict=True, description="Unique category ID")
    name: NonEmptyStr = Field(description="Category name")

    async def fetch_full(self) -> "BaseModel":
        """
        Fetch full category data.

        Note:
            Full Category model not yet implemented. This returns self.

        Returns:
            Self (partial category).
        """
        if not self._client:
            raise RuntimeError("No client available")
        raise NotImplementedError(
            "Full Category model not yet implemented. "
            "Add CategoriesResource to enable full CRUD operations."
        )

    async def edit(self, **kwargs: Any) -> "BaseModel":
        """
        Edit this category.

        Note:
            Full Category model not yet implemented.

        Raises:
            NotImplementedError: Until CategoriesResource is implemented.
        """
        if not self._client:
            raise RuntimeError("No client available")
        raise NotImplementedError("Full Category model not yet implemented.")
