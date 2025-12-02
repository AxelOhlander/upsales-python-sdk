"""Esign resource for Upsales API."""

from __future__ import annotations

from typing import TYPE_CHECKING

from upsales.models.esigns import Esign, PartialEsign
from upsales.resources.base import BaseResource

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class EsignsResource(BaseResource[Esign, PartialEsign]):
    """Resource manager for esigns.

    Handles CRUD operations for esigns (electronic signature documents).

    Example:
        ```python
        async with Upsales.from_env() as upsales:
            # Create esign
            esign = await upsales.esigns.create(
                userId=1,
                title="Contract Agreement"
            )

            # Get esign
            esign = await upsales.esigns.get(1)

            # List esigns
            esigns = await upsales.esigns.list(limit=10)

            # Update esign
            updated = await upsales.esigns.update(
                1,
                state="signed",
                signDate="2024-01-15"
            )

            # Delete esign
            await upsales.esigns.delete(1)
        ```
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize esigns resource.

        Args:
            http: HTTP client instance for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/esigns",
            model_class=Esign,
            partial_class=PartialEsign,
        )
