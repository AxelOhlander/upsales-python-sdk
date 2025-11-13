"""
ProjectPlanStatus models for Upsales API.

Endpoint: /api/v2/ProjectPlanStatus

Note:
- The upstream endpoint may currently return an empty data array in some
  tenants. The model is designed to be forward-compatible: extra fields
  returned by the API are allowed and preserved by Pydantic v2 configuration
  in BaseModel.
"""

from typing import TypedDict, Unpack

from pydantic import Field, computed_field

from upsales.models.base import BaseModel, PartialModel
from upsales.validators import NonEmptyStr


class ProjectPlanStatusUpdateFields(TypedDict, total=False):
    """
    Available fields for updating a ProjectPlanStatus.

    All fields are optional. This TypedDict is used with Unpack in edit()
    to provide IDE autocomplete and type safety for updates.
    """

    name: str
    category: str
    isDefault: bool


class ProjectPlanStatus(BaseModel):
    """
    ProjectPlanStatus model from /api/v2/ProjectPlanStatus.

    Represents a status value used in project plans. Common examples include
    states like "Not Started", "In Progress", and "Completed". Exact fields
    can vary by tenant configuration; extra fields from the API are accepted.

    Attributes:
        id: Unique status ID (read-only).
        name: Human-readable status name.
        category: Category grouping for the status.
        isDefault: Whether this is a default system status.
        regDate: Registration date (read-only).
        regBy: User ID who created this status (read-only).
        modDate: Last modification date (read-only).
        modBy: User ID who last modified this status (read-only).

    Example:
        >>> status = await upsales.project_plan_statuses.get(1)
        >>> status.name
        'In Progress'
        >>> status.is_default
        False
        >>> await status.edit(name="Ongoing")
    """

    # Read-only fields
    id: int = Field(frozen=True, strict=True, description="Unique status ID")
    regDate: str | None = Field(default=None, frozen=True, description="Registration date")
    regBy: int | None = Field(
        default=None,
        frozen=True,
        description=(
            "ID of the user who created this (0 = system). TODO: map to PartialUser if the id is not 0."
        ),
    )
    modDate: str | None = Field(default=None, frozen=True, description="Last modification date")
    modBy: int | None = Field(
        default=None,
        frozen=True,
        description=(
            "ID of the user who last modified this (0 = system). TODO: map to PartialUser if the id is not 0."
        ),
    )

    # Updatable fields
    name: NonEmptyStr | None = Field(default=None, description="Status display name")
    category: NonEmptyStr | None = Field(
        default=None, description="Category classification for status"
    )
    isDefault: bool | None = Field(
        default=None, description="Whether this is a default system status"
    )

    @computed_field
    @property
    def is_default(self) -> bool:
        """
        Convenience boolean for default status flag.

        Returns:
            True if this status is a default system status.

        Example:
            >>> status.is_default
            True
        """
        return self.isDefault is True

    async def edit(self, **kwargs: Unpack[ProjectPlanStatusUpdateFields]) -> "ProjectPlanStatus":
        """
        Edit this project plan status via the API.

        Uses to_api_dict() to exclude read-only and computed fields and
        serialize using API aliases.

        Args:
            **kwargs: Fields to update (see ProjectPlanStatusUpdateFields).

        Returns:
            Updated ProjectPlanStatus with fresh data from API.

        Raises:
            RuntimeError: If no client reference is available.
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.project_plan_statuses.update(
            self.id, **self.to_api_dict(**kwargs)
        )


class PartialProjectPlanStatus(PartialModel):
    """
    Partial ProjectPlanStatus for nested responses.

    Contains minimal fields commonly present when a status appears nested
    within other API responses. Use fetch_full() to retrieve the complete
    ProjectPlanStatus.

    Attributes:
        id: Unique status ID.
        name: Status display name.
    """

    id: int = Field(frozen=True, strict=True, description="Unique status ID")
    name: NonEmptyStr = Field(description="Status display name")

    async def fetch_full(self) -> ProjectPlanStatus:
        """
        Fetch the complete ProjectPlanStatus from the API.

        Returns:
            Full ProjectPlanStatus instance.

        Raises:
            RuntimeError: If no client reference is available.
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.project_plan_statuses.get(self.id)

    async def edit(self, **kwargs: Unpack[ProjectPlanStatusUpdateFields]) -> ProjectPlanStatus:
        """
        Edit this status and return the full ProjectPlanStatus.

        Args:
            **kwargs: Fields to update.

        Returns:
            Updated full ProjectPlanStatus object.

        Raises:
            RuntimeError: If no client reference is available.
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.project_plan_statuses.update(self.id, **kwargs)
