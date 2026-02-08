"""ReportClientCompanyType resource for Upsales API.

Company type report data.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class ReportClientCompanyTypeResource:
    """Company type report data.

    Read-only endpoint at /report/clientCompanyType.
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize resource.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/report/clientCompanyType"

    async def get(self, **params: Any) -> dict[str, Any]:
        """Get company type report data.

        Args:
            **params: Query parameters for filtering.

        Returns:
            API response data.
        """
        return await self._http.get(self._endpoint, **params)
