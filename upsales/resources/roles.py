"""
Roles resource manager for Upsales API.

Provides methods to interact with the /roles endpoint.

Example:
    >>> async with Upsales(token="...") as upsales:
    ...     role = await upsales.roles.get(1)
    ...     roles = await upsales.roles.list(limit=10)
"""

from upsales.http import HTTPClient
from upsales.models.roles import PartialRole, Role
from upsales.resources.base import BaseResource


class RolesResource(BaseResource[Role, PartialRole]):
    """
    Resource manager for Role endpoint.

    Inherits standard CRUD operations from BaseResource:
    - get(id) - Get single role
    - list(limit, offset, **params) - List roles with pagination
    - list_all(**params) - Auto-paginated list of all roles
    - update(id, **data) - Update role
    - delete(id) - Delete role
    - bulk_update(ids, data, max_concurrent) - Parallel updates
    - bulk_delete(ids, max_concurrent) - Parallel deletes

    Example:
        >>> roles = RolesResource(http_client)
        >>> role = await roles.get(1)
        >>> all_active = await roles.list_all(active=1)
    """

    def __init__(self, http: HTTPClient):
        """
        Initialize roles resource manager.

        Args:
            http: HTTP client for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/roles",
            model_class=Role,
            partial_class=PartialRole,
        )

    async def get_by_name(self, name: str) -> Role | None:
        """
        Get role by name.

        Args:
            name: Role name to search for.

        Returns:
            Role object if found, None otherwise.

        Example:
            >>> role = await upsales.roles.get_by_name("Sales Manager")
            >>> if role:
            ...     print(role.id)
        """
        all_roles: list[Role] = await self.list_all()
        for role in all_roles:
            if role.name.lower() == name.lower():
                return role
        return None

    async def get_with_discounts(self) -> list[Role]:
        """
        Get all roles that can apply discounts.

        Returns:
            List of roles with hasDiscount=True.

        Example:
            >>> discount_roles = await upsales.roles.get_with_discounts()
            >>> for role in discount_roles:
            ...     print(f"{role.name} can apply discounts")
        """
        all_roles: list[Role] = await self.list_all()
        return [role for role in all_roles if role.hasDiscount]

    async def get_by_currency(self, currency_code: str) -> list[Role]:
        """
        Get all roles with specified default currency.

        Args:
            currency_code: Currency code to filter by (e.g., "USD", "EUR").

        Returns:
            List of roles with matching defaultCurrency.

        Example:
            >>> usd_roles = await upsales.roles.get_by_currency("USD")
            >>> for role in usd_roles:
            ...     print(f"{role.name} uses {role.defaultCurrency}")
        """
        all_roles: list[Role] = await self.list_all()
        return [role for role in all_roles if role.defaultCurrency == currency_code]

    async def get_top_level(self) -> list[Role]:
        """
        Get all top-level roles (roles without parent).

        Returns:
            List of roles with no parent role.

        Example:
            >>> top_roles = await upsales.roles.get_top_level()
            >>> for role in top_roles:
            ...     print(f"{role.name} is a top-level role")
        """
        all_roles: list[Role] = await self.list_all()
        return [role for role in all_roles if not role.has_parent]
