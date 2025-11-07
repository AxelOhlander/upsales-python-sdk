"""
Segment models for Upsales API.

Generated from /api/v2/segments endpoint.
Analysis based on 2 samples.

Enhanced with Pydantic v2 features:
- Field descriptions for all fields
- Computed fields for boolean helpers
- Strict type checking for read-only fields
- Optimized serialization
"""

from typing import Any, TypedDict, Unpack

from pydantic import Field, computed_field

from upsales.models.base import BaseModel, PartialModel
from upsales.validators import BinaryFlag, NonEmptyStr


class SegmentUpdateFields(TypedDict, total=False):
    """
    Available fields for updating a Segment.

    All fields are optional. Use with Unpack for IDE autocomplete.
    """

    name: str
    description: str | None
    active: int
    filter: list[dict[str, Any]]
    version: int
    flowStatus: str | None
    flowName: str | None
    sourceTemplate: str | None
    usedForProspectingMonitor: int


class Segment(BaseModel):
    """
    Segment model from /api/v2/segments.

    Represents a contact segment in Upsales with filters and metadata.
    Segments are used to group contacts based on various criteria.

    Generated from 2 samples with field analysis.

    Example:
        >>> segment = await upsales.segments.get(1)
        >>> segment.name
        'Active Contacts'
        >>> segment.is_active
        True
        >>> segment.nrOfContacts
        106
        >>> await segment.edit(name="New Name")
    """

    # Read-only fields (frozen=True, strict=True)
    id: int = Field(frozen=True, strict=True, description="Unique segment ID")
    createDate: str = Field(frozen=True, description="Creation date (ISO 8601)")
    modDate: str = Field(frozen=True, description="Last modification date (ISO 8601)")
    regBy: int = Field(frozen=True, description="User ID who created this segment")
    modBy: int = Field(frozen=True, description="User ID who last modified this segment")
    nrOfContacts: int = Field(
        frozen=True, description="Number of contacts in this segment (read-only)"
    )

    # Required updatable fields
    name: NonEmptyStr = Field(description="Segment name")
    active: BinaryFlag = Field(default=1, description="Active status (0=inactive, 1=active)")
    filter: list[dict[str, Any]] = Field(
        default=[], description="List of filter configurations for this segment"
    )
    version: int = Field(default=2, description="Segment version (1 or 2)")
    usedForProspectingMonitor: BinaryFlag = Field(
        default=0, description="Used for prospecting monitor (0=no, 1=yes)"
    )

    # Optional fields
    description: str | None = Field(default=None, description="Segment description")
    flowStatus: str | None = Field(default=None, description="Flow status")
    flowName: str | None = Field(default=None, description="Flow name")
    sourceTemplate: str | None = Field(default=None, description="Source template identifier")

    @computed_field
    @property
    def is_active(self) -> bool:
        """
        Check if segment is active.

        Returns:
            True if active flag is 1, False otherwise.

        Example:
            >>> segment.is_active
            True
        """
        return self.active == 1

    @computed_field
    @property
    def has_contacts(self) -> bool:
        """
        Check if segment has any contacts.

        Returns:
            True if nrOfContacts > 0, False otherwise.

        Example:
            >>> segment.has_contacts
            True
        """
        return self.nrOfContacts > 0

    @computed_field
    @property
    def is_used_for_prospecting(self) -> bool:
        """
        Check if segment is used for prospecting monitor.

        Returns:
            True if usedForProspectingMonitor is 1, False otherwise.

        Example:
            >>> segment.is_used_for_prospecting
            False
        """
        return self.usedForProspectingMonitor == 1

    async def edit(self, **kwargs: Unpack[SegmentUpdateFields]) -> "Segment":
        """
        Edit this segment.

        Uses Pydantic v2's optimized serialization via to_api_dict().

        Args:
            **kwargs: Fields to update (full IDE autocomplete support).

        Returns:
            Updated segment with fresh data from API.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> segment = await upsales.segments.get(1)
            >>> updated = await segment.edit(
            ...     name="New Segment Name",
            ...     description="Updated description",
            ...     active=1
            ... )
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.segments.update(self.id, **self.to_update_dict(**kwargs))


class PartialSegment(PartialModel):
    """
    Partial Segment for nested responses.

    Contains minimal fields for when Segment appears nested in other
    API responses. Since segments rarely appear nested, this is a
    minimal implementation.

    Use fetch_full() to get complete Segment object with all fields.

    Example:
        >>> # If segment appeared nested somewhere
        >>> partial_segment = some_object.segment  # PartialSegment
        >>> full_segment = await partial_segment.fetch_full()  # Now Segment
    """

    id: int = Field(frozen=True, strict=True, description="Unique segment ID")
    name: NonEmptyStr = Field(description="Segment name")
    active: BinaryFlag = Field(default=1, description="Active status (0=inactive, 1=active)")

    async def fetch_full(self) -> Segment:
        """
        Fetch complete segment data.

        Returns:
            Full Segment object with all fields populated.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> partial = some_object.segment  # PartialSegment
            >>> full = await partial.fetch_full()  # Segment
            >>> full.nrOfContacts  # Now available
            106
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.segments.get(self.id)

    async def edit(self, **kwargs: Unpack[SegmentUpdateFields]) -> Segment:
        """
        Edit this segment.

        Returns full Segment object after update.

        Args:
            **kwargs: Fields to update (full IDE autocomplete support).

        Returns:
            Updated full Segment object.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> partial = some_object.segment  # PartialSegment
            >>> updated = await partial.edit(name="New Name")  # Returns Segment
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.segments.update(self.id, **kwargs)
