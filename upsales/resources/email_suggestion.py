"""EmailSuggestion resource for Upsales API.

Email suggestion (alternate endpoint).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class EmailSuggestionResource:
    """Email suggestion (alternate endpoint).

    Read-only endpoint at /emailSuggestion.
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize resource.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/emailSuggestion"

    async def get(self, **params: Any) -> dict[str, Any]:
        """Get email suggestions for a contact.

        Args:
            **params: Query parameters for filtering.

        Returns:
            API response data.
        """
        return await self._http.get(self._endpoint, **params)
