"""
Project Plan Types resource manager for Upsales API.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from upsales.models.project_plan_types import PartialProjectPlanType, ProjectPlanType
from upsales.resources.base import BaseResource

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class ProjectPlanTypesResource(BaseResource[ProjectPlanType, PartialProjectPlanType]):
    """
    Resource manager for project plan types endpoint.

    Project plan types define templates for project workflows with stages.

    Example:
        >>> async with Upsales(token="...") as upsales:
        ...     # Get a project plan type
        ...     plan_type = await upsales.project_plan_types.get(1)
        ...     print(plan_type.name)
        ...
        ...     # List all project plan types
        ...     types = await upsales.project_plan_types.list()
        ...
        ...     # Update a plan type
        ...     updated = await upsales.project_plan_types.update(
        ...         1,
        ...         name="Updated Plan Type"
        ...     )
    """

    def __init__(self, http: HTTPClient):
        """
        Initialize ProjectPlanTypesResource.

        Args:
            http: HTTP client for API communication.
        """
        super().__init__(
            http=http,
            endpoint="/projectPlanTypes",
            model_class=ProjectPlanType,
            partial_class=PartialProjectPlanType,
        )
