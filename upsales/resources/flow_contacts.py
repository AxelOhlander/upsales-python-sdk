"""FlowContacts resource for Upsales API.

Contacts within flow steps.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class FlowContactsResource:
    """Contacts within flow steps.

    Read-only endpoint at /flows.
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize resource.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/flows"

    async def list(
        self, flow_id: int, step_id: int, stats_type: str, **params: Any
    ) -> dict[str, Any]:
        """List contacts in a flow step.

        Args:
            flow_id: Flow ID.
            step_id: Step ID.
            stats_type: Stats type (e.g., 'waiting', 'completed').
            **params: Query parameters for filtering.

        Returns:
            API response data.
        """
        return await self._http.get(
            f"{self._endpoint}/{flow_id}/{step_id}/contacts/{stats_type}", **params
        )
