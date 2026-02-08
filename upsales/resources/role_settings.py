"""RoleSettings resource for Upsales API.

Role settings configuration.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class RoleSettingsResource:
    """Role settings configuration.

    Read-only endpoint at /roleSettings.
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize resource.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/roleSettings"

    async def list(self, **params: Any) -> dict[str, Any]:
        """List role settings.

        Args:
            **params: Query parameters for filtering.

        Returns:
            API response data.
        """
        return await self._http.get(self._endpoint, **params)
