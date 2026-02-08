"""Social events default templates resource for Upsales API.

Default email templates for social events (invitations, reminders, etc.).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class SocialEventsDefaultTemplatesResource:
    """Manage default email templates for social events.

    Endpoint at /socialEvents/defaultTemplates. Supports GET by type
    and DELETE by type + id.
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize resource.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/socialEvents/defaultTemplates"

    async def get(self, type: str, **params: Any) -> dict[str, Any]:
        """Get default templates for a social event type.

        Args:
            type: Template type (e.g., invitation, reminder).
            **params: Query parameters for filtering.

        Returns:
            API response with template data.
        """
        return await self._http.get(f"{self._endpoint}/{type}", **params)

    async def delete(self, type: str, template_id: int) -> dict[str, Any]:
        """Delete a default template.

        Args:
            type: Template type.
            template_id: Template ID to delete.

        Returns:
            API response data.
        """
        return await self._http.delete(f"{self._endpoint}/{type}/{template_id}")
