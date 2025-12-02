"""Banner group resource for Upsales API."""

from __future__ import annotations

from typing import TYPE_CHECKING

from upsales.models.banner_groups import BannerGroup, PartialBannerGroup
from upsales.resources.base import BaseResource

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class BannerGroupsResource(BaseResource[BannerGroup, PartialBannerGroup]):
    """Resource manager for banner groups.

    Handles CRUD operations for banner groups (ad banner management).

    Example:
        ```python
        async with Upsales.from_env() as upsales:
            # Create banner group
            banner = await upsales.banner_groups.create(
                landingPage="https://example.com/campaign",
                title="Q4 Campaign"
            )

            # Get banner group
            banner = await upsales.banner_groups.get(1)

            # List banner groups
            banners = await upsales.banner_groups.list(limit=10)

            # Update banner group
            updated = await upsales.banner_groups.update(
                1,
                title="Updated Title",
                draft=False
            )

            # Delete banner group
            await upsales.banner_groups.delete(1)
        ```
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize banner groups resource.

        Args:
            http: HTTP client instance for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/bannerGroups",
            model_class=BannerGroup,
            partial_class=PartialBannerGroup,
        )
