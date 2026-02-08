"""EmailDuplicates resource for Upsales API.

Detect duplicate email addresses across contacts.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class EmailDuplicatesResource:
    """Detect duplicate email addresses across contacts.

    Read-only endpoint at /function/email-duplicates.
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize resource.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/function/email-duplicates"

    async def check(self, **params: Any) -> dict[str, Any]:
        """Check for duplicate emails.

        Args:
            **params: Query parameters for filtering.

        Returns:
            API response data.
        """
        return await self._http.get(self._endpoint, **params)
