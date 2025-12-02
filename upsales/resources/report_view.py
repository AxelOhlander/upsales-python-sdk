"""Report view resource for Upsales API."""

from __future__ import annotations

from typing import TYPE_CHECKING

from upsales.models.report_view import PartialReportView, ReportView
from upsales.resources.base import BaseResource

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class ReportViewsResource(BaseResource[ReportView, PartialReportView]):
    """Resource manager for report views.

    Handles CRUD operations for report views (custom report configurations).

    Example:
        ```python
        async with Upsales.from_env() as upsales:
            # Create report view
            view = await upsales.report_views.create(
                title="My Custom View",
                type="own",
                filters=[]
            )

            # Get report view
            view = await upsales.report_views.get("uuid")

            # List report views
            views = await upsales.report_views.list(limit=10)

            # Update report view
            updated = await upsales.report_views.update(
                "uuid",
                title="Updated Title",
                default=True
            )

            # Delete report view
            await upsales.report_views.delete("uuid")
        ```
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize report views resource.

        Args:
            http: HTTP client instance for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/reportView",
            model_class=ReportView,
            partial_class=PartialReportView,
        )
