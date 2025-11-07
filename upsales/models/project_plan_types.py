"""
Project Plan Type models for Upsales API.

Project plan types define templates for project workflows with stages.
"""

from typing import Any, TypedDict, Unpack

from pydantic import Field

from upsales.models.base import BaseModel, PartialModel


class ProjectPlanTypeUpdateFields(TypedDict, total=False):
    """
    Available fields for updating a ProjectPlanType.

    All fields are optional.
    """

    name: str
    category: str
    stages: list[dict[str, Any]]
    isDefault: bool


class ProjectPlanType(BaseModel):
    """
    Project Plan Type model representing a project workflow template.

    Project plan types define reusable templates for project workflows,
    including stages and categories.

    Attributes:
        id: Unique identifier for the project plan type.
        name: Display name of the project plan type.
        category: Category classification for the plan type.
        stages: List of workflow stages in this plan type.
        isDefault: Whether this is the default plan type.
        regDate: Registration date (ISO format).
        regBy: User ID who created this plan type.
        modDate: Last modification date (ISO format).
        modBy: User ID who last modified this plan type.

    Example:
        >>> plan_type = await upsales.project_plan_types.get(1)
        >>> print(plan_type.name)
        >>> await plan_type.edit(name="Updated Plan Type")
    """

    # Read-only fields
    id: int = Field(frozen=True, strict=True, description="Unique project plan type ID")
    regDate: str = Field(frozen=True, description="Registration date")
    regBy: int = Field(frozen=True, description="User ID who created this")
    modDate: str = Field(frozen=True, description="Last modification date")
    modBy: int = Field(frozen=True, description="User ID who last modified this")

    # Updatable fields
    name: str = Field(description="Project plan type name")
    category: str = Field(description="Category classification")
    stages: list[dict[str, Any]] = Field(default=[], description="Workflow stages")
    isDefault: bool = Field(description="Whether this is the default plan type")

    async def edit(self, **kwargs: Unpack[ProjectPlanTypeUpdateFields]) -> "ProjectPlanType":
        """
        Edit this project plan type.

        Args:
            **kwargs: Fields to update. Available fields:
                - name: Project plan type name
                - category: Category classification
                - stages: Workflow stages
                - isDefault: Default plan type flag

        Returns:
            Updated project plan type instance.

        Raises:
            RuntimeError: If no client is available.

        Example:
            >>> plan_type = await upsales.project_plan_types.get(1)
            >>> updated = await plan_type.edit(name="New Name")
            >>> print(updated.name)
            New Name
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.project_plan_types.update(self.id, **self.to_api_dict(**kwargs))


class PartialProjectPlanType(PartialModel):
    """
    Partial ProjectPlanType for nested responses.

    Contains minimal fields typically included when project plan types
    appear as nested objects in other API responses.

    Attributes:
        id: Unique project plan type identifier.
        name: Project plan type name.

    Example:
        >>> partial = project.plan_type  # Nested reference
        >>> full = await partial.fetch_full()
        >>> print(full.category)
    """

    id: int = Field(description="Unique project plan type ID")
    name: str = Field(description="Project plan type name")

    async def fetch_full(self) -> ProjectPlanType:
        """
        Fetch the complete project plan type data.

        Returns:
            Full ProjectPlanType instance with all fields.

        Raises:
            RuntimeError: If no client is available.

        Example:
            >>> partial = project.plan_type
            >>> full = await partial.fetch_full()
            >>> print(full.stages)
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.project_plan_types.get(self.id)

    async def edit(self, **kwargs: Unpack[ProjectPlanTypeUpdateFields]) -> ProjectPlanType:
        """
        Edit this project plan type.

        Args:
            **kwargs: Fields to update.

        Returns:
            Updated ProjectPlanType instance.

        Raises:
            RuntimeError: If no client is available.

        Example:
            >>> partial = project.plan_type
            >>> updated = await partial.edit(name="New Name")
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.project_plan_types.update(self.id, **kwargs)
