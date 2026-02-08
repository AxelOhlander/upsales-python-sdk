"""Mail bounce resource for Upsales API.

Manages mail bounce records — remove bounced email addresses.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class MailBounceResource:
    """Manage mail bounce records.

    DELETE-only endpoint at /bounce. Removes a bounced email from the
    bounce list so mail can be sent to it again.
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize resource.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/bounce"

    async def delete(self, mail_base64: str) -> dict[str, Any]:
        """Remove a bounced email from the bounce list.

        Args:
            mail_base64: Base64-encoded email address.

        Returns:
            API response data.
        """
        return await self._http.delete(f"{self._endpoint}/{mail_base64}")
