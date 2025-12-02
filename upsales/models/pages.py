"""
Page models for Upsales API.

Landing pages are used for tracking marketing campaigns and web content.
This endpoint supports GET (list) and PUT (update) operations only.

Example:
    >>> async with Upsales.from_env() as upsales:
    ...     # Get all pages
    ...     pages = await upsales.pages.list()
    ...
    ...     # Update a page
    ...     page = await upsales.pages.get(1)
    ...     await page.edit(name="Updated Landing Page", hide=0)
"""

from typing import TypedDict, Unpack

from pydantic import Field, computed_field

from upsales.models.base import BaseModel, PartialModel
from upsales.validators import BinaryFlag


class PageUpdateFields(TypedDict, total=False):
    """
    Available fields for updating a Page.

    All fields are optional. Read-only fields (id, pageImpression) are excluded.

    Attributes:
        name: Page name.
        url: Landing page URL.
        state: Page state (e.g., "active", "inactive").
        lastUpdateDate: Last update date in YYYY-MM-DD format.
        score: Page score/rating.
        hide: Hide page (0=visible, 1=hidden).
        keywords: List of keywords for SEO.
    """

    name: str
    url: str
    state: str
    lastUpdateDate: str
    score: int
    hide: int
    keywords: list[str]


class Page(BaseModel):
    """
    Landing page model for tracking marketing campaigns and web content.

    Pages are used to track visitor impressions and engagement with landing pages.
    This model supports GET (list/get) and PUT (update) operations only.

    Attributes:
        id: Unique page identifier (read-only).
        name: Page name.
        url: Landing page URL.
        state: Page state (e.g., "active", "inactive").
        lastUpdateDate: Last update date in YYYY-MM-DD format.
        pageImpression: Total page impressions count (read-only).
        score: Page score/rating.
        hide: Hide page flag (0=visible, 1=hidden).
        keywords: List of keywords for SEO optimization.

    Example:
        >>> page = await upsales.pages.get(1)
        >>> print(f"{page.name}: {page.pageImpression} impressions")
        >>> await page.edit(hide=1)  # Hide the page
    """

    # Read-only fields
    id: int = Field(frozen=True, strict=True, description="Unique page ID")
    pageImpression: int = Field(frozen=True, description="Total page impressions (read-only)")

    # Updatable fields
    name: str = Field(description="Page name")
    url: str = Field(description="Landing page URL")
    state: str = Field(description="Page state (e.g., 'active', 'inactive')")
    lastUpdateDate: str = Field(description="Last update date (YYYY-MM-DD)")
    score: int = Field(default=0, description="Page score/rating")
    hide: BinaryFlag = Field(default=0, description="Hide page (0=visible, 1=hidden)")
    keywords: list[str] = Field(default=[], description="SEO keywords")

    @computed_field
    @property
    def is_hidden(self) -> bool:
        """Check if page is hidden."""
        return self.hide == 1

    @computed_field
    @property
    def is_visible(self) -> bool:
        """Check if page is visible."""
        return self.hide == 0

    async def edit(self, **kwargs: Unpack[PageUpdateFields]) -> "Page":
        """
        Edit this page with type-safe field updates.

        Uses Pydantic v2 optimized serialization (to_api_dict) for 5-50x faster
        performance compared to model_dump().

        Args:
            **kwargs: Fields to update. All fields are optional.
                - name: Page name
                - url: Landing page URL
                - state: Page state
                - lastUpdateDate: Last update date (YYYY-MM-DD)
                - score: Page score/rating
                - hide: Hide page (0=visible, 1=hidden)
                - keywords: SEO keywords list

        Returns:
            Updated Page instance with latest data from API.

        Raises:
            RuntimeError: If no client is available.

        Example:
            >>> page = await upsales.pages.get(1)
            >>> updated = await page.edit(
            ...     name="New Campaign Page",
            ...     hide=0,
            ...     keywords=["campaign", "offer"]
            ... )
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.pages.update(self.id, **self.to_api_dict(**kwargs))


class PartialPage(PartialModel):
    """
    Partial Page for nested responses.

    Contains minimal page data when pages appear as nested objects
    in other API responses.

    Attributes:
        id: Unique page identifier.
        name: Page name.
    """

    id: int = Field(description="Unique page ID")
    name: str = Field(description="Page name")

    async def fetch_full(self) -> Page:
        """
        Fetch complete page data from API.

        Returns:
            Full Page instance with all fields.

        Raises:
            RuntimeError: If no client is available.

        Example:
            >>> partial_page = some_object.page  # From nested response
            >>> full_page = await partial_page.fetch_full()
            >>> print(f"Impressions: {full_page.pageImpression}")
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.pages.get(self.id)

    async def edit(self, **kwargs: Unpack[PageUpdateFields]) -> Page:
        """
        Edit this page directly from partial instance.

        Args:
            **kwargs: Fields to update (see PageUpdateFields).

        Returns:
            Updated full Page instance.

        Raises:
            RuntimeError: If no client is available.

        Example:
            >>> partial_page = some_object.page
            >>> updated = await partial_page.edit(hide=1)
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.pages.update(self.id, **kwargs)
