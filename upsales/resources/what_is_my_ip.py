"""WhatIsMyIp resource for Upsales API.

IP address lookup utility.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class WhatIsMyIpResource:
    """IP address lookup utility.

    Read-only endpoint at /function/whatismyip.
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize resource.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/function/whatismyip"

    async def get(self) -> dict[str, Any]:
        """Get your current IP address.

        Returns:
            API response data.
        """
        return await self._http.get(self._endpoint)
