"""
Users resource manager for Upsales API.

Provides methods to interact with the /users endpoint.

Example:
    >>> async with Upsales(token="...") as upsales:
    ...     user = await upsales.users.get(1)
    ...     users_list = await upsales.users.list(limit=10)
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

    Example:
        >>> resource = UsersResource(http_client)
        >>> user = await resource.get(1)
        >>> all_active = await resource.list_all(active=1)
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

        Fetches all users and filters client-side for the email.

        Args:
            email: Email address to search for (case-insensitive).

        Returns:
            User if found, None otherwise.

        Example:
            >>> user = await upsales.users.get_by_email("john@example.com")
        """
        users: list[User] = await self.list_all()
        # Filter client-side (case-insensitive)
        email_lower = email.lower()
        matching = [u for u in users if u.email.lower() == email_lower]
        return matching[0] if matching else None

    async def get_administrators(self) -> list[User]:
        """
        Get all administrator users.

        Returns:
            List of users with administrator flag set.

        Example:
            >>> admins = await upsales.users.get_administrators()
        """
        return await self.list_all(administrator=1)

    async def get_active(self, include_api_keys: bool = False) -> list[User]:
        """
        Get all active users.

        By default, excludes API keys/service accounts (ghost=1).
        Set include_api_keys=True to include them.

        Args:
            include_api_keys: If True, include API keys (ghost=1). Default: False.

        Returns:
            List of active users.

        Example:
            >>> # Get active users only (excludes API keys)
            >>> active_users = await upsales.users.get_active()
            >>> # All returned users have active=1 and ghost=0
            >>>
            >>> # Include API keys
            >>> all_active = await upsales.users.get_active(include_api_keys=True)
            >>> # Includes both ghost=0 and ghost=1
        """
        if include_api_keys:
            return await self.list_all(active=1)
        return await self.list_all(active=1, ghost=0)
