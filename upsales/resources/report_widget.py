"""ReportWidget resource for Upsales API.

Report widget data.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class ReportWidgetResource:
    """Report widget data.

    Read-only endpoint at /report/widget.
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize resource.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/report/widget"

    async def get(self, **params: Any) -> dict[str, Any]:
        """Get report widget data.

        Args:
            **params: Query parameters for filtering.

        Returns:
            API response data.
        """
        return await self._http.get(self._endpoint, **params)
