"""
Productcategory models for Upsales API.

Generated from /api/v2/productcategories endpoint.
Analysis based on 4 samples.

Field optionality determined by:
- Required: Field present AND non-null in 100% of samples
- Optional: Field missing OR null in any sample
- Custom fields: Always optional with default []

TODO: Review and customize the generated models:
1. Mark read-only fields with Field(frozen=True)
2. Update field types if needed
3. Add custom_fields property if 'custom' field exists
4. Update docstrings with detailed descriptions
5. Add any custom methods
"""

from typing import Unpack, TypedDict, Any
from pydantic import Field
from upsales.models.base import BaseModel


class ProductcategoryUpdateFields(TypedDict, total=False):
    """
    Available fields for updating a Productcategory.

    All fields are optional.
    """
    roles: list[Any]
    orderRowFields: list[Any]
    inheritRoles: bool
    name: str
    sortId: int
    parentId: int


class Productcategory(BaseModel):
    """
    Productcategory model from /api/v2/productcategories.

    Generated from 4 samples.

    TODO: Review and update field types and docstrings.
    TODO: Mark read-only fields with Field(frozen=True).
    TODO: Add custom_fields property if model has 'custom' field.
    """

    id: int  # Present in 100% (4/4)
    inheritRoles: bool  # Present in 100% (4/4)
    name: str  # Present in 100% (4/4)
    orderRowFields: list[Any] = []  # Present in 100% (4/4)
    parentId: int  # Present in 100% (4/4)
    roles: list[Any] = []  # Present in 100% (4/4)
    sortId: int  # Present in 100% (4/4)

    async def edit(self, **kwargs: Unpack[ProductcategoryUpdateFields]) -> "Productcategory":
        """
        Edit this productcategory.

        Args:
            **kwargs: Fields to update.

        Returns:
            Updated productcategory.
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.productcategories.update(
            self.id,
            **self.to_update_dict(**kwargs)
        )
