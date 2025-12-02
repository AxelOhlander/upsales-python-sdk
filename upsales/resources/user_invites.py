"""User invites resource manager for Upsales API.

Provides methods to interact with the /userInvites endpoint for managing
user invitations stored in Redis with expiration.

Example:
    >>> async with Upsales(token="...") as upsales:
    ...     invite = await upsales.user_invites.get("invite-123")
    ...     invites_list = await upsales.user_invites.list(limit=10)
"""

from upsales.http import HTTPClient
from upsales.models.user_invites import PartialUserInvite, UserInvite
from upsales.resources.base import BaseResource


class UserInvitesResource(BaseResource[UserInvite, PartialUserInvite]):
    """Resource manager for UserInvite endpoint.

    Inherits standard CRUD operations from BaseResource:
    - create(**data) - Create new user invitation
    - get(id) - Get single user invite by UUID
    - list(limit, offset, **params) - List user invites with pagination
    - list_all(**params) - Auto-paginated list of all user invites
    - update(id, **data) - Update user invite
    - delete(id) - Delete user invite
    - bulk_update(ids, data, max_concurrent) - Parallel updates
    - bulk_delete(ids, max_concurrent) - Parallel deletes

    Example:
        >>> resource = UserInvitesResource(http_client)
        >>> invite = await resource.create(name="John Doe", email="john@example.com")
        >>> invite = await resource.get("invite-uuid-123")
        >>> all_active = await resource.list_all(active=1)
    """

    def __init__(self, http: HTTPClient):
        """Initialize user invites resource manager.

        Args:
            http: HTTP client for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/userInvites",
            model_class=UserInvite,
            partial_class=PartialUserInvite,
        )

    async def get_by_email(self, email: str) -> UserInvite | None:
        """Get user invite by email address.

        Args:
            email: Email address to search for.

        Returns:
            UserInvite | None: User invite if found, None otherwise.

        Example:
            >>> invite = await resource.get_by_email("john@example.com")
            >>> if invite:
            ...     print(invite.name)
        """
        invites: list[UserInvite] = await self.list_all()
        for invite in invites:
            if invite.email.lower() == email.lower():
                return invite
        return None
