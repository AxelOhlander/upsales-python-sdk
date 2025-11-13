"""
ProjectPlanPriority resource manager for Upsales API.

Provides methods to interact with the /projectPlanPriority endpoint using
ProjectPlanPriority models.

Example:
    >>> async with Upsales(token="...") as upsales:
    ...     # Get single priority
    ...     priority = await upsales.project_plan_priorities.get(1)
    ...     print(priority.name, priority.category)
    ...
    ...     # List all priorities
    ...     priorities = await upsales.project_plan_priorities.list()
    ...
    ...     # Get by category
    ...     high = await upsales.project_plan_priorities.get_by_category("HIGH")
    ...
    ...     # Get defaults
    ...     defaults = await upsales.project_plan_priorities.get_defaults()
"""

from upsales.http import HTTPClient
from upsales.models.project_plan_priority import (
    PartialProjectPlanPriority,
    ProjectPlanPriority,
)
from upsales.resources.base import BaseResource


class ProjectPlanPrioritiesResource(BaseResource[ProjectPlanPriority, PartialProjectPlanPriority]):
    """
    Resource manager for ProjectPlanPriority endpoint.

    Inherits standard CRUD operations from BaseResource:
    - get(id) - Get single priority
    - list(limit, offset, **params) - List priorities with pagination
    - list_all(**params) - Auto-paginated list of all priorities
    - create(**data) - Create new priority
    - update(id, **data) - Update priority
    - delete(id) - Delete priority
    - bulk_update(ids, data, max_concurrent) - Parallel updates
    - bulk_delete(ids, max_concurrent) - Parallel deletes

    Additional methods:
    - get_by_category(category) - Get all priorities by category (LOW, MEDIUM, HIGH)
    - get_defaults() - Get all default system priorities
    - get_by_name(name) - Get priority by name

    Example:
        >>> priorities = ProjectPlanPrioritiesResource(http_client)
        >>> priority = await priorities.get(1)
        >>> high = await priorities.get_by_category("HIGH")
        >>> defaults = await priorities.get_defaults()
    """

    def __init__(self, http: HTTPClient):
        """
        Initialize project plan priorities resource manager.

        Args:
            http: HTTP client for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/projectPlanPriority",
            model_class=ProjectPlanPriority,
            partial_class=PartialProjectPlanPriority,
        )

    async def get_by_category(self, category: str) -> list[ProjectPlanPriority]:
        """
        Get all priorities by category.

        Args:
            category: Priority category (LOW, MEDIUM, HIGH).

        Returns:
            List of priorities matching the specified category.

        Example:
            >>> high_priorities = await upsales.project_plan_priorities.get_by_category("HIGH")
            >>> for priority in high_priorities:
            ...     print(f"{priority.name} - {priority.category}")
        """
        all_priorities: list[ProjectPlanPriority] = await self.list_all()
        return [p for p in all_priorities if p.category.upper() == category.upper()]

    async def get_defaults(self) -> list[ProjectPlanPriority]:
        """
        Get all default system priorities.

        Returns:
            List of priorities where isDefault is True.

        Example:
            >>> defaults = await upsales.project_plan_priorities.get_defaults()
            >>> for priority in defaults:
            ...     print(f"{priority.name} ({priority.category})")
        """
        all_priorities: list[ProjectPlanPriority] = await self.list_all()
        return [p for p in all_priorities if p.is_default]

    async def get_by_name(self, name: str) -> ProjectPlanPriority | None:
        """
        Get priority by name.

        Args:
            name: Priority name to search for (case-insensitive).

        Returns:
            Priority object if found, None otherwise.

        Example:
            >>> priority = await upsales.project_plan_priorities.get_by_name("Låg")
            >>> if priority:
            ...     print(priority.category)  # LOW
        """
        all_priorities: list[ProjectPlanPriority] = await self.list_all()
        for priority in all_priorities:
            if priority.name.lower() == name.lower():
                return priority
        return None

    async def get_low(self) -> list[ProjectPlanPriority]:
        """
        Get all low priority items.

        Convenience method, equivalent to get_by_category("LOW").

        Returns:
            List of priorities with category LOW.

        Example:
            >>> low = await upsales.project_plan_priorities.get_low()
            >>> for priority in low:
            ...     print(priority.name)
        """
        return await self.get_by_category("LOW")

    async def get_medium(self) -> list[ProjectPlanPriority]:
        """
        Get all medium priority items.

        Convenience method, equivalent to get_by_category("MEDIUM").

        Returns:
            List of priorities with category MEDIUM.

        Example:
            >>> medium = await upsales.project_plan_priorities.get_medium()
            >>> for priority in medium:
            ...     print(priority.name)
        """
        return await self.get_by_category("MEDIUM")

    async def get_high(self) -> list[ProjectPlanPriority]:
        """
        Get all high priority items.

        Convenience method, equivalent to get_by_category("HIGH").

        Returns:
            List of priorities with category HIGH.

        Example:
            >>> high = await upsales.project_plan_priorities.get_high()
            >>> for priority in high:
            ...     print(priority.name)
        """
        return await self.get_by_category("HIGH")
