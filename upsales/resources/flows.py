"""Flows resource manager for Upsales API.

This module provides the resource manager for marketing automation flow operations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from upsales.models.flows import Flow, PartialFlow
from upsales.resources.base import BaseResource

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class FlowsResource(BaseResource[Flow, PartialFlow]):
    """Resource manager for flow operations.

    Handles all marketing automation flow-related API operations including:
    - Standard CRUD (create, read, update, delete)
    - List and search operations
    - Flow status management

    Examples:
        Basic operations:

        >>> upsales = Upsales(token="...")
        >>>
        >>> # Create flow
        >>> flow = await upsales.flows.create(
        ...     name="Welcome Campaign",
        ...     segmentId=5,
        ...     status="draft"
        ... )
        >>>
        >>> # Get flow
        >>> flow = await upsales.flows.get(1)
        >>>
        >>> # List all flows
        >>> flows = await upsales.flows.list_all()
        >>>
        >>> # Update flow
        >>> updated = await upsales.flows.update(
        ...     1,
        ...     status="active",
        ...     skipWeekends=True
        ... )
        >>>
        >>> # Delete flow
        >>> await upsales.flows.delete(1)

        Status operations:

        >>> # Get active flows
        >>> active_flows = await upsales.flows.get_active_flows()
        >>>
        >>> # Get flows by segment
        >>> segment_flows = await upsales.flows.get_by_segment(5)
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize the flows resource manager.

        Args:
            http: HTTP client instance for API communication.
        """
        super().__init__(
            http=http,
            endpoint="/flows",
            model_class=Flow,
            partial_class=PartialFlow,
        )

    async def get_by_name(self, name: str) -> Flow | None:
        """Get flow by name.

        Args:
            name: Flow name to search for (case-insensitive).

        Returns:
            Flow object if found, None otherwise.

        Examples:
            >>> flow = await upsales.flows.get_by_name("Welcome Campaign")
            >>> if flow:
            ...     print(flow.id)
        """
        all_flows: list[Flow] = await self.list_all()
        for flow in all_flows:
            if flow.name and flow.name.lower() == name.lower():
                return flow
        return None

    async def get_active_flows(self) -> list[Flow]:
        """Get all active flows.

        Returns:
            List of Flow objects with status='active'.

        Examples:
            >>> active_flows = await upsales.flows.get_active_flows()
            >>> for flow in active_flows:
            ...     print(f"{flow.name} is running")
        """
        all_flows: list[Flow] = await self.list_all()
        return [flow for flow in all_flows if flow.status == "active"]

    async def get_draft_flows(self) -> list[Flow]:
        """Get all draft flows.

        Returns:
            List of Flow objects with status='draft'.

        Examples:
            >>> draft_flows = await upsales.flows.get_draft_flows()
            >>> print(f"Found {len(draft_flows)} drafts")
        """
        all_flows: list[Flow] = await self.list_all()
        return [flow for flow in all_flows if flow.status == "draft"]

    async def get_by_segment(self, segment_id: int) -> list[Flow]:
        """Get all flows for a specific segment.

        Args:
            segment_id: The segment ID to find flows for.

        Returns:
            List of Flow objects targeting this segment.

        Examples:
            >>> flows = await upsales.flows.get_by_segment(5)
            >>> for flow in flows:
            ...     print(f"{flow.name} targets segment {segment_id}")
        """
        all_flows: list[Flow] = await self.list_all()
        return [flow for flow in all_flows if flow.segmentId == segment_id]
