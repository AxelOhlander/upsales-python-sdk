"""
ProjectPlanStatus resource manager for Upsales API.

Provides CRUD access to the /ProjectPlanStatus endpoint using
ProjectPlanStatus models.

Example:
    >>> async with Upsales(token="...") as upsales:
    ...     # Get a single status
    ...     status = await upsales.project_plan_statuses.get(1)
    ...     print(status.name)
    ...
    ...     # List all statuses
    ...     statuses = await upsales.project_plan_statuses.list()
    ...
    ...     # Update a status
    ...     updated = await upsales.project_plan_statuses.update(1, name="Ongoing")
"""

from upsales.http import HTTPClient
from upsales.models.project_plan_status import (
    PartialProjectPlanStatus,
    ProjectPlanStatus,
)
from upsales.resources.base import BaseResource


class ProjectPlanStatusesResource(BaseResource[ProjectPlanStatus, PartialProjectPlanStatus]):
    """
    Resource manager for /ProjectPlanStatus endpoint.

    Inherits standard CRUD and search operations from BaseResource.
    """

    def __init__(self, http: HTTPClient):
        """
        Initialize the resource manager.

        Args:
            http: HTTP client for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/ProjectPlanStatus",
            model_class=ProjectPlanStatus,
            partial_class=PartialProjectPlanStatus,
        )
