"""DoceboSSO resource for Upsales API.

Docebo SSO URL generation.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class DoceboSSOResource:
    """Docebo SSO URL generation.

    Read-only endpoint at /function/externalSSO/docebo.
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize resource.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/function/externalSSO/docebo"

    async def get_url(self, **params: Any) -> dict[str, Any]:
        """Get Docebo SSO URL.

        Args:
            **params: Query parameters for filtering.

        Returns:
            API response data.
        """
        return await self._http.get(self._endpoint, **params)
