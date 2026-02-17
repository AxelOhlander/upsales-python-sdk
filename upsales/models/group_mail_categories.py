"""
Group mail category models for Upsales API.

Generated from /api/v2/groupMailCategories endpoint.
Analysis based on 4 samples and API specification.
"""

from typing import Any, TypedDict, Unpack

from pydantic import Field, computed_field

from upsales.models.base import BaseModel, PartialModel
from upsales.validators import BinaryFlag


class GroupMailCategoryUpdateFields(TypedDict, total=False):
    """
    Available fields for updating a GroupMailCategory.

    All fields are optional.
    """

    active: int
    title: str
    description: str
    languages: list[dict[str, str]]


class GroupMailCategory(BaseModel):
    """
    Group mail category model from /api/v2/groupMailCategories.

    Group mail categories organize email campaigns into logical groups.

    Attributes:
        id: Unique identifier for the category.
        title: Category title/name.
        description: Optional description of the category.
        active: Binary flag indicating if category is active (0 or 1).
        languages: List of language configurations with translations.
        relatedMailCampaigns: List of related campaigns (MailCampaign or Flow entities).

    Example:
        >>> async with Upsales(token="...") as upsales:
        ...     category = await upsales.group_mail_categories.get(1)
        ...     if category.is_active:
        ...         await category.edit(description="Updated description")
    """

    # Read-only fields
    id: int = Field(frozen=True, strict=True, description="Unique category ID")
    relatedMailCampaigns: list[int | dict[str, Any]] = Field(
        default=[],
        frozen=True,
        description="Related campaigns (IDs or MailCampaign/Flow entities)",
    )

    # Updatable fields
    title: str = Field(description="Category title")
    description: str | None = Field(default=None, description="Category description")
    active: BinaryFlag = Field(default=1, description="Active status (0 or 1)")
    languages: list[str | dict[str, str]] = Field(
        default=[], description="Language codes or configurations with translations"
    )

    @computed_field
    @property
    def is_active(self) -> bool:
        """Check if category is active."""
        return self.active == 1

    async def edit(self, **kwargs: Unpack[GroupMailCategoryUpdateFields]) -> "GroupMailCategory":
        """
        Edit this group mail category.

        Args:
            **kwargs: Fields to update (title, description, active, languages).

        Returns:
            Updated group mail category.

        Raises:
            RuntimeError: If no client is available.

        Example:
            >>> category = await upsales.group_mail_categories.get(1)
            >>> updated = await category.edit(
            ...     title="Newsletter Category",
            ...     active=1
            ... )
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.group_mail_categories.update(
            self.id, **self.to_api_dict(**kwargs)
        )


class PartialGroupMailCategory(PartialModel):
    """
    Partial GroupMailCategory for nested responses.

    Used when group mail categories appear as nested objects in other resources.

    Attributes:
        id: Unique category ID.
        title: Category title.

    Example:
        >>> campaign = await upsales.campaigns.get(1)
        >>> category = campaign.category  # PartialGroupMailCategory
        >>> full_category = await category.fetch_full()
    """

    id: int = Field(description="Unique category ID")
    title: str = Field(description="Category title")

    async def fetch_full(self) -> GroupMailCategory:
        """
        Fetch full group mail category data.

        Returns:
            Complete GroupMailCategory object.

        Raises:
            RuntimeError: If no client is available.
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.group_mail_categories.get(self.id)

    async def edit(self, **kwargs: Unpack[GroupMailCategoryUpdateFields]) -> GroupMailCategory:
        """
        Edit this group mail category.

        Args:
            **kwargs: Fields to update.

        Returns:
            Updated group mail category.

        Raises:
            RuntimeError: If no client is available.
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.group_mail_categories.update(self.id, **kwargs)
