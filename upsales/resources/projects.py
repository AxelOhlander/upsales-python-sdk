"""
Projects resource manager for Upsales API.

Provides methods to interact with the /projects endpoint using Project models.

Example:
    >>> async with Upsales(token="...") as upsales:
    ...     # Get single project
    ...     project = await upsales.projects.get(1)
    ...     print(project.name, project.is_active)
    ...
    ...     # List projects
    ...     projects = await upsales.projects.list(limit=10)
    ...
    ...     # Get active projects
    ...     active = await upsales.projects.get_active()
    ...
    ...     # Get projects by user
    ...     user_projects = await upsales.projects.get_by_user(user_id=123)
    ...
    ...     # Get call list projects
    ...     call_lists = await upsales.projects.get_call_lists()
"""

from upsales.http import HTTPClient
from upsales.models.projects import PartialProject, Project
from upsales.resources.base import BaseResource


class ProjectsResource(BaseResource[Project, PartialProject]):
    """
    Resource manager for Project endpoint.

    Inherits standard CRUD operations from BaseResource:
    - create(**data) - Create new project
    - get(id) - Get single project
    - list(limit, offset, **params) - List projects with pagination
    - list_all(**params) - Auto-paginated list of all projects
    - search(**filters) - Search with comparison operators
    - update(id, **data) - Update project
    - delete(id) - Delete project
    - bulk_update(ids, data, max_concurrent) - Parallel updates
    - bulk_delete(ids, max_concurrent) - Parallel deletes

    Additional methods:
    - get_active() - Get all active projects
    - get_inactive() - Get all inactive projects
    - get_by_user(user_id) - Get projects assigned to a user
    - get_call_lists() - Get projects that are call lists

    Example:
        >>> projects = ProjectsResource(http_client)
        >>> project = await projects.get(1)
        >>> active = await projects.get_active()
        >>> user_projects = await projects.get_by_user(123)
    """

    def __init__(self, http: HTTPClient):
        """
        Initialize projects resource manager.

        Args:
            http: HTTP client for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/projects",
            model_class=Project,
            partial_class=PartialProject,
        )

    async def get_active(self) -> list[Project]:
        """
        Get all active projects.

        Returns:
            List of active projects (active=1).

        Example:
            >>> active = await upsales.projects.get_active()
            >>> len(active)
            25
            >>> all(p.is_active for p in active)
            True
        """
        return await self.list_all(active=1)

    async def get_inactive(self) -> list[Project]:
        """
        Get all inactive projects.

        Returns:
            List of inactive projects (active=0).

        Example:
            >>> inactive = await upsales.projects.get_inactive()
            >>> len(inactive)
            10
            >>> all(not p.is_active for p in inactive)
            True
        """
        return await self.list_all(active=0)

    async def get_by_user(self, user_id: int) -> list[Project]:
        """
        Get all projects assigned to a specific user.

        Args:
            user_id: User ID to filter by.

        Returns:
            List of projects where user is assigned.

        Example:
            >>> projects = await upsales.projects.get_by_user(123)
            >>> len(projects)
            5
            >>> any(u['id'] == 123 for p in projects for u in p.users)
            True

        Note:
            This searches for projects where the user appears in the users list.
            Uses nested field syntax for API filtering.
        """
        # Note: API uses nested field syntax for filtering
        return await self.search(**{"users.id": user_id})

    async def get_call_lists(self) -> list[Project]:
        """
        Get all projects that are call lists.

        Returns:
            List of projects marked as call lists (isCallList=True).

        Example:
            >>> call_lists = await upsales.projects.get_call_lists()
            >>> len(call_lists)
            3
            >>> all(p.isCallList for p in call_lists)
            True
        """
        return await self.list_all(isCallList=True)
