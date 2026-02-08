"""MailTemplatesUsedIn resource for Upsales API.

Template usage information — where templates are used.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class MailTemplatesUsedInResource:
    """Template usage information — where templates are used.

    Read-only endpoint at /mail/templates/usedIn.
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize resource.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/mail/templates/usedIn"

    async def get(self, **params: Any) -> dict[str, Any]:
        """Get template usage information.

        Args:
            **params: Query parameters for filtering.

        Returns:
            API response data.
        """
        return await self._http.get(self._endpoint, **params)
