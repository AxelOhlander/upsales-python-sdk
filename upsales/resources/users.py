"""
Users resource manager for Upsales API.

Provides methods to interact with the /users endpoint using User models.

Example:
    >>> async with Upsales(token="...") as upsales:
    ...     # Get single user
    ...     user = await upsales.users.get(1)
    ...     print(user.name, user.is_admin)
    ...
    ...     # List users
    ...     users = await upsales.users.list(limit=10)
    ...
    ...     # Get user by email
    ...     user = await upsales.users.get_by_email("john@example.com")
    ...
    ...     # Get all administrators
    ...     admins = await upsales.users.get_administrators()
"""

from upsales.http import HTTPClient
from upsales.models.user import PartialUser, User
from upsales.resources.base import BaseResource


class UsersResource(BaseResource[User, PartialUser]):
    """
    Resource manager for User endpoint.

    Inherits standard CRUD operations from BaseResource:
    - get(id) - Get single user
    - list(limit, offset, **params) - List users with pagination
    - list_all(**params) - Auto-paginated list of all users
    - update(id, **data) - Update user
    - delete(id) - Delete user
    - bulk_update(ids, data, max_concurrent) - Parallel updates
    - bulk_delete(ids, max_concurrent) - Parallel deletes

    Additional methods:
    - get_by_email(email) - Get user by email address
    - get_administrators() - Get all administrator users
    - get_active() - Get all active users

    Example:
        >>> users = UsersResource(http_client)
        >>> user = await users.get(1)
        >>> admin = await users.get_by_email("admin@company.com")
        >>> all_admins = await users.get_administrators()
    """

    def __init__(self, http: HTTPClient):
        """
        Initialize users resource manager.

        Args:
            http: HTTP client for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/users",
            model_class=User,
            partial_class=PartialUser,
        )

    async def get_by_email(self, email: str) -> User | None:
        """
        Get user by email address.

        Args:
            email: Email address to search for.

        Returns:
            User object if found, None otherwise.

        Example:
            >>> user = await upsales.users.get_by_email("john@example.com")
            >>> if user:
            ...     print(user.name)
        """
        # Note: This assumes API supports filtering by email
        # May need adjustment based on actual API behavior
        all_users: list[User] = await self.list_all()
        for user in all_users:
            if user.email.lower() == email.lower():
                return user
        return None

    async def get_administrators(self) -> list[User]:
        """
        Get all administrator users.

        Returns:
            List of users with administrator=1.

        Example:
            >>> admins = await upsales.users.get_administrators()
            >>> for admin in admins:
            ...     print(f"{admin.name} - {admin.email}")
        """
        return await self.list_all(administrator=1)

    async def get_active(self, include_api_keys: bool = False) -> list[User]:
        """
        Get all active users.

        User types in Upsales:
        - Active users: ghost=0, active=1 (regular users)
        - API keys: ghost=1, active=1 (service accounts)
        - Inactive users: ghost=0, active=0
        - Invalid state: ghost=1, active=0 (inactive API key - shouldn't exist)

        Args:
            include_api_keys: If True, include API keys (ghost=1, active=1).
                            If False (default), only regular users (ghost=0, active=1).

        Returns:
            List of active users, optionally excluding API keys.

        Example:
            >>> # Get active users (excludes API keys by default)
            >>> users = await upsales.users.get_active()
            >>> all(u.ghost == 0 for u in users)
            True
            >>>
            >>> # Include API keys
            >>> all_active = await upsales.users.get_active(include_api_keys=True)
            >>> # Returns both ghost=0 and ghost=1 users (all with active=1)
        """
        if include_api_keys:
            # Include both regular users and API keys (all with active=1)
            return await self.list_all(active=1)
        else:
            # Exclude API keys (only ghost=0, active=1)
            return await self.list_all(active=1, ghost=0)
