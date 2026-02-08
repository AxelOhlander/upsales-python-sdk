"""FormsExternalLeadSource resource for Upsales API.

External lead source forms.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class FormsExternalLeadSourceResource:
    """External lead source forms.

    Read-only endpoint at /forms/external-lead-source.
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize resource.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/forms/external-lead-source"

    async def list(self, **params: Any) -> dict[str, Any]:
        """List external lead source forms.

        Args:
            **params: Query parameters for filtering.

        Returns:
            API response data.
        """
        return await self._http.get(self._endpoint, **params)
