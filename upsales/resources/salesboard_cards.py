"""Salesboard card resource for Upsales API."""

from __future__ import annotations

from typing import TYPE_CHECKING

from upsales.models.salesboard_cards import PartialSalesboardCard, SalesboardCard
from upsales.resources.base import BaseResource

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class SalesboardCardsResource(BaseResource[SalesboardCard, PartialSalesboardCard]):
    """Resource manager for salesboard cards.

    Handles CRUD operations for salesboard cards (custom salesboard view configurations).

    Note:
        Administrator permissions required for POST and PUT operations.

    Example:
        ```python
        async with Upsales.from_env() as upsales:
            # Create salesboard card (administrator only)
            card = await upsales.salesboard_cards.create(
                config={"type": "pipeline", "settings": {}}
            )

            # Get salesboard card
            card = await upsales.salesboard_cards.get(1)

            # List salesboard cards
            cards = await upsales.salesboard_cards.list(limit=10)

            # Update salesboard card (administrator only)
            updated = await upsales.salesboard_cards.update(
                1,
                config={"type": "pipeline", "settings": {"view": "compact"}}
            )

            # Delete salesboard card
            await upsales.salesboard_cards.delete(1)
        ```
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize salesboard cards resource.

        Args:
            http: HTTP client instance for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/salesboardCards",
            model_class=SalesboardCard,
            partial_class=PartialSalesboardCard,
        )
