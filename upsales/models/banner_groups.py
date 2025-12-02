"""Banner group models for Upsales API.

This module defines models for banner groups (ad banner management).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Unpack

from pydantic import Field, computed_field

from upsales.models.base import BaseModel, PartialModel
from upsales.models.custom_fields import CustomFields
from upsales.validators import CustomFieldsList

if TYPE_CHECKING:
    from upsales.types import BannerGroupUpdateFields


class BannerGroup(BaseModel):
    """Banner group model.

    Represents an ad banner group in Upsales.

    Attributes:
        id: Unique banner group ID (read-only).
        title: Banner group title (max 256 characters).
        regBy: User who created the banner group (read-only).
        draft: Whether banner group is in draft mode.
        body: Banner group body content.
        landingPage: Target landing page URL (required for creation).
        regDate: Registration date (read-only).
        modDate: Last modification date (read-only).
        pages: Pages configuration.
        formats: Banner formats configuration.
        availableFormats: Available banner formats.
        brandId: Associated brand ID (read-only).
        custom: Custom fields list.

    Example:
        ```python
        # Create banner group
        banner = await upsales.banner_groups.create(
            landingPage="https://example.com/campaign",
            title="Q4 Campaign",
            draft=False
        )

        # Update banner group
        banner.title = "Q4 2024 Campaign"
        updated = await banner.edit()

        # Or use edit with parameters
        updated = await banner.edit(title="New Title", draft=True)
        ```
    """

    # Read-only fields
    id: int = Field(frozen=True, strict=True, description="Unique banner group ID")
    regBy: dict | None = Field(None, frozen=True, description="User who created")
    regDate: str | None = Field(None, frozen=True, description="Registration date")
    modDate: str | None = Field(None, frozen=True, description="Modification date")
    brandId: int | None = Field(None, frozen=True, description="Associated brand ID")

    # Updatable fields
    title: str | None = Field(None, description="Banner group title (max 256 chars)")
    draft: bool = Field(True, description="Draft mode status")
    body: str | None = Field(None, description="Banner body content")
    landingPage: str = Field(description="Target landing page URL")
    pages: str | None = Field(None, description="Pages configuration")
    formats: str | None = Field(None, description="Banner formats")
    availableFormats: str | None = Field(None, description="Available formats")
    custom: CustomFieldsList = Field(default=[], description="Custom fields")

    @computed_field
    @property
    def custom_fields(self) -> CustomFields:
        """Access custom fields with dict-like interface.

        Returns:
            CustomFields instance for accessing custom fields.

        Example:
            ```python
            banner = await upsales.banner_groups.get(1)
            value = banner.custom_fields.get(11)
            banner.custom_fields.set(11, "new_value")
            ```
        """
        return CustomFields(self.custom)

    @computed_field
    @property
    def is_draft(self) -> bool:
        """Check if banner group is in draft mode.

        Returns:
            True if draft, False otherwise.

        Example:
            ```python
            if banner.is_draft:
                print("This is a draft banner")
            ```
        """
        return self.draft is True

    async def edit(self, **kwargs: Unpack[BannerGroupUpdateFields]) -> BannerGroup:
        """Edit this banner group with type-safe field updates.

        Args:
            **kwargs: Fields to update (title, draft, body, landingPage, pages,
                     formats, availableFormats, custom).

        Returns:
            Updated BannerGroup instance.

        Raises:
            RuntimeError: If no client is available.
            ValidationError: If field validation fails.
            NotFoundError: If banner group no longer exists.

        Example:
            ```python
            banner = await upsales.banner_groups.get(1)

            # Update single field
            updated = await banner.edit(title="New Title")

            # Update multiple fields
            updated = await banner.edit(
                title="New Title",
                draft=False,
                landingPage="https://example.com/new"
            )
            ```
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.banner_groups.update(self.id, **self.to_api_dict(**kwargs))


class PartialBannerGroup(PartialModel):
    """Partial banner group model for nested responses.

    Used when banner groups appear as nested objects in API responses.

    Attributes:
        id: Unique banner group ID.
        title: Banner group title.

    Example:
        ```python
        # Fetch full banner group from partial
        partial: PartialBannerGroup = some_object.banner_group
        full: BannerGroup = await partial.fetch_full()

        # Edit through partial
        updated = await partial.edit(title="New Title")
        ```
    """

    id: int = Field(description="Unique banner group ID")
    title: str | None = Field(None, description="Banner group title")

    async def fetch_full(self) -> BannerGroup:
        """Fetch complete banner group data.

        Returns:
            Full BannerGroup instance.

        Raises:
            RuntimeError: If no client is available.
            NotFoundError: If banner group not found.

        Example:
            ```python
            partial = PartialBannerGroup(id=1, title="Campaign")
            full = await partial.fetch_full()
            print(full.landingPage)
            ```
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.banner_groups.get(self.id)

    async def edit(self, **kwargs: Unpack[BannerGroupUpdateFields]) -> BannerGroup:
        """Edit this banner group.

        Args:
            **kwargs: Fields to update.

        Returns:
            Updated BannerGroup instance.

        Raises:
            RuntimeError: If no client is available.
            NotFoundError: If banner group not found.

        Example:
            ```python
            partial = PartialBannerGroup(id=1, title="Campaign")
            updated = await partial.edit(draft=False)
            ```
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.banner_groups.update(self.id, **kwargs)
