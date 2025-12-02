"""Visit resource for Upsales API."""

from __future__ import annotations

from typing import TYPE_CHECKING

from upsales.models.visits import PartialVisit, Visit
from upsales.resources.base import BaseResource

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class VisitsResource(BaseResource[Visit, PartialVisit]):
    """Resource manager for visits.

    Handles CRUD operations for visits (website visit tracking).

    Note:
        Administrator or mailAdmin permissions required for most operations.

    Example:
        ```python
        async with Upsales.from_env() as upsales:
            # Create visit (administrator or mailAdmin only)
            visit = await upsales.visits.create(
                referer="https://google.com",
                score=10
            )

            # Get visit
            visit = await upsales.visits.get(1)

            # List visits
            visits = await upsales.visits.list(limit=10)

            # Update visit (administrator or mailAdmin only)
            updated = await upsales.visits.update(
                1,
                score=20
            )

            # Delete visit (administrator or mailAdmin only)
            await upsales.visits.delete(1)
        ```
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize visits resource.

        Args:
            http: HTTP client instance for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/visits",
            model_class=Visit,
            partial_class=PartialVisit,
        )
