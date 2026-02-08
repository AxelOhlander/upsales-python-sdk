"""EmailSuggest resource for Upsales API.

Email address suggestions based on contact data.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class EmailSuggestResource:
    """Email address suggestions based on contact data.

    Read-only endpoint at /function/email-suggest.
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize resource.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/function/email-suggest"

    async def suggest(self, **params: Any) -> dict[str, Any]:
        """Get email suggestions.

        Args:
            **params: Query parameters for filtering.

        Returns:
            API response data.
        """
        return await self._http.get(self._endpoint, **params)
