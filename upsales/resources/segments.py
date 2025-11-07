"""
Segments resource manager for Upsales API.

Provides methods to interact with the /segments endpoint using Segment models.

Example:
    >>> async with Upsales(token="...") as upsales:
    ...     # Get single segment
    ...     segment = await upsales.segments.get(1)
    ...     print(segment.name, segment.is_active)
    ...
    ...     # List segments
    ...     segments = await upsales.segments.list(limit=10)
    ...
    ...     # Get all active segments
    ...     active = await upsales.segments.get_active()
    ...
    ...     # Get segments with contacts
    ...     populated = await upsales.segments.get_populated()
"""

from upsales.http import HTTPClient
from upsales.models.segments import PartialSegment, Segment
from upsales.resources.base import BaseResource


class SegmentsResource(BaseResource[Segment, PartialSegment]):
    """
    Resource manager for Segment endpoint.

    Inherits standard CRUD operations from BaseResource:
    - get(id) - Get single segment
    - list(limit, offset, **params) - List segments with pagination
    - list_all(**params) - Auto-paginated list of all segments
    - create(**data) - Create new segment
    - update(id, **data) - Update segment
    - delete(id) - Delete segment
    - bulk_update(ids, data, max_concurrent) - Parallel updates
    - bulk_delete(ids, max_concurrent) - Parallel deletes

    Additional methods:
    - get_active() - Get all active segments
    - get_populated() - Get segments that have contacts

    Example:
        >>> segments = SegmentsResource(http_client)
        >>> segment = await segments.get(1)
        >>> active = await segments.get_active()
        >>> populated = await segments.get_populated()
    """

    def __init__(self, http: HTTPClient):
        """
        Initialize segments resource manager.

        Args:
            http: HTTP client for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/segments",
            model_class=Segment,
            partial_class=PartialSegment,
        )

    async def get_active(self) -> list[Segment]:
        """
        Get all active segments.

        Returns:
            List of segments with active=1.

        Example:
            >>> active_segments = await upsales.segments.get_active()
            >>> for segment in active_segments:
            ...     print(f"{segment.name} - {segment.nrOfContacts} contacts")
        """
        all_segments: list[Segment] = await self.list_all()
        return [segment for segment in all_segments if segment.is_active]

    async def get_populated(self) -> list[Segment]:
        """
        Get all segments that have contacts.

        Returns:
            List of segments where nrOfContacts > 0.

        Example:
            >>> populated = await upsales.segments.get_populated()
            >>> for segment in populated:
            ...     print(f"{segment.name} - {segment.nrOfContacts} contacts")
        """
        all_segments: list[Segment] = await self.list_all()
        return [segment for segment in all_segments if segment.has_contacts]

    async def get_by_name(self, name: str) -> Segment | None:
        """
        Get segment by name.

        Args:
            name: Segment name to search for (case-insensitive).

        Returns:
            Segment object if found, None otherwise.

        Example:
            >>> segment = await upsales.segments.get_by_name("Active Contacts")
            >>> if segment:
            ...     print(segment.nrOfContacts)
        """
        all_segments: list[Segment] = await self.list_all()
        for segment in all_segments:
            if segment.name.lower() == name.lower():
                return segment
        return None
