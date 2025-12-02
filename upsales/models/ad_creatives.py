"""Ad Creatives model for Upsales API.

This module provides models for managing ad creatives (banners, images, HTML5)
used in marketing campaigns.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, Unpack

from pydantic import Field, computed_field

from upsales.models.base import BaseModel, PartialModel
from upsales.validators import NonEmptyStr, PositiveInt  # noqa: TC001

if TYPE_CHECKING:
    from typing import TypedDict

    class AdCreativeUpdateFields(TypedDict, total=False):
        """Available fields for updating an AdCreative.

        All fields are optional for updates.
        """

        name: str
        type: Literal["image", "html5", "third_party_tag", "zip"]
        width: int
        height: int
        url: str
        fileId: int | None
        formatId: int | None
        body: str | None
        code: str | None


class AdCreative(BaseModel):
    """Represents an ad creative in Upsales.

    Ad creatives are marketing materials (banners, images, HTML5 ads) used in
    advertising campaigns.

    Attributes:
        id: Unique identifier (read-only).
        name: Creative name (max 100 chars).
        type: Creative type (image, html5, third_party_tag, zip).
        width: Width in pixels.
        height: Height in pixels.
        url: Creative URL (max 255 chars).
        fileId: Associated file ID (optional).
        formatId: Format identifier (optional).
        body: Creative body content (optional).
        code: HTML/code content (optional, max 65535 chars).
        sampleImageUrl: Preview image URL (read-only).
        state: Creative state/status (read-only).
        impressions: Total impressions count (read-only).
        clicks: Total clicks count (read-only).

    Example:
        >>> creative = await upsales.ad_creatives.get(123)
        >>> print(f"Creative: {creative.name} ({creative.width}x{creative.height})")
        >>> print(f"Performance: {creative.clicks}/{creative.impressions} clicks")
        >>> await creative.edit(name="Updated Banner")
    """

    # Read-only fields
    id: int = Field(frozen=True, strict=True, description="Unique creative ID")
    sampleImageUrl: str | None = Field(None, frozen=True, description="Preview image URL")
    state: str | None = Field(None, frozen=True, description="Creative state/status")
    impressions: int | None = Field(None, frozen=True, description="Total impressions count")
    clicks: int | None = Field(None, frozen=True, description="Total clicks count")

    # Required fields
    name: NonEmptyStr = Field(max_length=100, description="Creative name")
    type: Literal["image", "html5", "third_party_tag", "zip"] = Field(description="Creative type")
    width: PositiveInt = Field(description="Width in pixels")
    height: PositiveInt = Field(description="Height in pixels")
    url: NonEmptyStr = Field(max_length=255, description="Creative URL")

    # Optional fields
    fileId: int | None = Field(None, description="Associated file ID")
    formatId: int | None = Field(None, description="Format identifier")
    body: str | None = Field(None, description="Creative body content")
    code: str | None = Field(None, max_length=65535, description="HTML/code content")

    @computed_field
    @property
    def dimensions(self) -> str:
        """Get creative dimensions as formatted string.

        Returns:
            Dimensions in "WIDTHxHEIGHT" format.

        Example:
            >>> creative.dimensions
            "300x250"
        """
        return f"{self.width}x{self.height}"

    @computed_field
    @property
    def click_through_rate(self) -> float | None:
        """Calculate click-through rate (CTR).

        Returns:
            CTR as percentage (0-100), or None if no impressions.

        Example:
            >>> creative.click_through_rate
            2.5  # 2.5% CTR
        """
        if not self.impressions or self.impressions == 0:
            return None
        return (self.clicks or 0) / self.impressions * 100

    @computed_field
    @property
    def is_image(self) -> bool:
        """Check if creative is an image type.

        Returns:
            True if type is "image", False otherwise.

        Example:
            >>> creative.is_image
            True
        """
        return self.type == "image"

    @computed_field
    @property
    def is_html5(self) -> bool:
        """Check if creative is HTML5 type.

        Returns:
            True if type is "html5", False otherwise.

        Example:
            >>> creative.is_html5
            False
        """
        return self.type == "html5"

    async def edit(self, **kwargs: Unpack[AdCreativeUpdateFields]) -> AdCreative:
        """Update this ad creative with new values.

        Args:
            **kwargs: Fields to update (see AdCreativeUpdateFields).

        Returns:
            Updated AdCreative instance.

        Raises:
            RuntimeError: If no client is available.
            ValidationError: If field values are invalid.
            UpsalesError: If the API request fails.

        Example:
            >>> creative = await upsales.ad_creatives.get(123)
            >>> updated = await creative.edit(name="New Banner Name")
            >>> print(updated.name)
            "New Banner Name"
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.ad_creatives.update(self.id, **self.to_api_dict(**kwargs))


class PartialAdCreative(PartialModel):
    """Partial representation of an ad creative.

    Used when ad creatives appear as nested references in other API responses.
    Contains minimal identifying information.

    Attributes:
        id: Unique identifier.
        name: Creative name.
        type: Creative type (image, html5, third_party_tag, zip).

    Example:
        >>> # From a campaign response
        >>> creative_ref = campaign.creative  # PartialAdCreative
        >>> full_creative = await creative_ref.fetch_full()
        >>> print(full_creative.dimensions)
    """

    id: int = Field(description="Unique creative ID")
    name: str = Field(description="Creative name")
    type: Literal["image", "html5", "third_party_tag", "zip"] | None = Field(
        None, description="Creative type"
    )

    async def fetch_full(self) -> AdCreative:
        """Fetch the complete ad creative data.

        Returns:
            Full AdCreative instance with all fields.

        Raises:
            RuntimeError: If no client is available.
            NotFoundError: If the creative doesn't exist.
            UpsalesError: If the API request fails.

        Example:
            >>> partial = PartialAdCreative(id=123, name="Banner")
            >>> full = await partial.fetch_full()
            >>> print(full.dimensions)
            "300x250"
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.ad_creatives.get(self.id)

    async def edit(self, **kwargs: Unpack[AdCreativeUpdateFields]) -> AdCreative:
        """Update this ad creative with new values.

        Args:
            **kwargs: Fields to update (see AdCreativeUpdateFields).

        Returns:
            Updated AdCreative instance.

        Raises:
            RuntimeError: If no client is available.
            ValidationError: If field values are invalid.
            UpsalesError: If the API request fails.

        Example:
            >>> partial = PartialAdCreative(id=123, name="Banner")
            >>> updated = await partial.edit(name="Updated Banner")
            >>> print(updated.name)
            "Updated Banner"
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.ad_creatives.update(self.id, **kwargs)
