"""
ProjectPlanStage models for Upsales API.

Generated from /api/v2/projectPlanStages endpoint.
Analysis based on 3 samples.

Field optionality determined by:
- Required: Field present AND non-null in 100% of samples
- Optional: Field missing OR null in any sample
- Custom fields: Always optional with default []

TODO: Review and customize the generated models:
1. Mark read-only fields with Field(frozen=True)
2. Update field types if needed
3. Add custom_fields property if 'custom' field exists
4. Update docstrings with detailed descriptions
5. Add any custom methods
"""

from typing import TypedDict, Unpack

from pydantic import Field

from upsales.models.base import BaseModel, PartialModel


class ProjectPlanStageUpdateFields(TypedDict, total=False):
    """
    Available fields for updating a ProjectPlanStage.

    All fields are optional.
    """

    color: str
    category: str
    name: str


class ProjectPlanStage(BaseModel):
    """
    Project plan stage model from /api/v2/projectPlanStages.

    Represents a stage in project planning workflow (e.g., TODO, IN_PROGRESS, DONE).
    Verified with 3 API samples (2025-11-09).

    Example:
        >>> async with Upsales.from_env() as upsales:
        ...     stages = await upsales.project_plan_stages.list()
        ...     stage = stages[0]
        ...     print(f"{stage.name}: {stage.category}")
    """

    id: int = Field(frozen=True, strict=True, description="Unique stage ID")
    name: str = Field(description="Stage name (e.g., 'Att göra', 'Pågående')")
    category: str = Field(description="Stage category (TODO, IN_PROGRESS, DONE)")
    color: str = Field(description="Color code for visual representation (e.g., '#FCF0C0')")

    async def edit(self, **kwargs: Unpack[ProjectPlanStageUpdateFields]) -> "ProjectPlanStage":
        """
        Edit this projectplanstage.

        Args:
            **kwargs: Fields to update.

        Returns:
            Updated projectplanstage.
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.project_plan_stages.update(self.id, **self.to_api_dict(**kwargs))


class PartialProjectPlanStage(PartialModel):
    """
    Partial ProjectPlanStage for nested responses.

    Contains minimal fields for references in other models.
    """

    id: int = Field(frozen=True, strict=True, description="Unique stage ID")
    name: str = Field(description="Stage name")

    async def fetch_full(self) -> ProjectPlanStage:
        """Fetch full projectplanstage data."""
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.project_plan_stages.get(self.id)

    async def edit(self, **kwargs: Unpack[ProjectPlanStageUpdateFields]) -> ProjectPlanStage:
        """Edit this projectplanstage."""
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.project_plan_stages.update(self.id, **kwargs)
