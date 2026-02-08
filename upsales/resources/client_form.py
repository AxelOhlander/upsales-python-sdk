"""ClientForm resource for Upsales API.

Client-facing forms.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class ClientFormResource:
    """Client-facing forms.

    Read-only endpoint at /clientform.
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize resource.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/clientform"

    async def list(self, **params: Any) -> dict[str, Any]:
        """List client forms.

        Args:
            **params: Query parameters for filtering.

        Returns:
            API response data.
        """
        return await self._http.get(self._endpoint, **params)
