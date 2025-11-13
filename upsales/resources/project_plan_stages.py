"""
Projectplanstages resource manager for Upsales API.

Provides methods to interact with the /projectPlanStages endpoint.

Example:
    >>> async with Upsales(token="...") as upsales:
    ...     projectPlanStage = await upsales.projectPlanStages.get(1)
    ...     projectPlanStages = await upsales.projectPlanStages.list(limit=10)
"""

from upsales.http import HTTPClient
from upsales.models.project_plan_stages import PartialProjectPlanStage, ProjectPlanStage
from upsales.resources.base import BaseResource


class ProjectplanstagesResource(BaseResource[ProjectPlanStage, PartialProjectPlanStage]):
    """
    Resource manager for ProjectPlanStage endpoint.

    Inherits standard CRUD operations from BaseResource:
    - get(id) - Get single projectPlanStage
    - list(limit, offset, **params) - List projectPlanStages with pagination
    - list_all(**params) - Auto-paginated list of all projectPlanStages
    - update(id, **data) - Update projectPlanStage
    - delete(id) - Delete projectPlanStage
    - bulk_update(ids, data, max_concurrent) - Parallel updates
    - bulk_delete(ids, max_concurrent) - Parallel deletes

    Example:
        >>> projectPlanStages = ProjectplanstagesResource(http_client)
        >>> projectPlanStage = await projectPlanStages.get(1)
        >>> all_active = await projectPlanStages.list_all(active=1)
    """

    def __init__(self, http: HTTPClient):
        """
        Initialize projectPlanStages resource manager.

        Args:
            http: HTTP client for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/projectPlanStages",
            model_class=ProjectPlanStage,
            partial_class=PartialProjectPlanStage,
        )

    # Add custom methods here as needed
    # Example:
    # async def get_active(self) -> list[ProjectPlanStage]:
    #     """Get all active projectPlanStages."""
    #     return await self.list_all(active=1)
