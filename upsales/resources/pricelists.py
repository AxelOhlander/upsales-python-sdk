"""
Pricelists resource manager for Upsales API.

Provides methods to interact with the /pricelists endpoint using Pricelist models.

Example:
    >>> async with Upsales(token="...") as upsales:
    ...     # Get single pricelist
    ...     pricelist = await upsales.pricelists.get(1)
    ...     print(pricelist.name, pricelist.is_active)
    ...
    ...     # List pricelists
    ...     pricelists = await upsales.pricelists.list(limit=10)
    ...
    ...     # Get default pricelist
    ...     default = await upsales.pricelists.get_default()
    ...
    ...     # Get all active pricelists
    ...     active = await upsales.pricelists.get_active()
"""

from upsales.http import HTTPClient
from upsales.models.pricelist import PartialPricelist, Pricelist
from upsales.resources.base import BaseResource


class PricelistsResource(BaseResource[Pricelist, PartialPricelist]):
    """
    Resource manager for Pricelist endpoint.

    Inherits standard CRUD operations from BaseResource:
    - get(id) - Get single pricelist
    - list(limit, offset, **params) - List pricelists with pagination
    - list_all(**params) - Auto-paginated list of all pricelists
    - create(**data) - Create new pricelist
    - update(id, **data) - Update pricelist
    - delete(id) - Delete pricelist
    - bulk_update(ids, data, max_concurrent) - Parallel updates
    - bulk_delete(ids, max_concurrent) - Parallel deletes

    Additional methods:
    - get_default() - Get the default pricelist
    - get_active() - Get all active pricelists
    - get_by_code(code) - Get pricelist by code

    Example:
        >>> pricelists = PricelistsResource(http_client)
        >>> pricelist = await pricelists.get(1)
        >>> default = await pricelists.get_default()
        >>> active = await pricelists.get_active()
    """

    def __init__(self, http: HTTPClient):
        """
        Initialize pricelists resource manager.

        Args:
            http: HTTP client for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/pricelists",
            model_class=Pricelist,
            partial_class=PartialPricelist,
        )

    async def get_default(self) -> Pricelist | None:
        """
        Get the default pricelist.

        Returns:
            Default pricelist if found, None otherwise.

        Example:
            >>> default = await upsales.pricelists.get_default()
            >>> if default:
            ...     print(f"Default: {default.name}")
        """
        all_pricelists: list[Pricelist] = await self.list_all()
        for pricelist in all_pricelists:
            if pricelist.isDefault:
                return pricelist
        return None

    async def get_active(self) -> list[Pricelist]:
        """
        Get all active pricelists.

        Returns:
            List of pricelists with active=True.

        Example:
            >>> active = await upsales.pricelists.get_active()
            >>> for pricelist in active:
            ...     print(f"{pricelist.name} - Active")
        """
        return await self.list_all(active=True)

    async def get_by_code(self, code: str) -> Pricelist | None:
        """
        Get pricelist by code.

        Args:
            code: Pricelist code to search for.

        Returns:
            Pricelist object if found, None otherwise.

        Example:
            >>> pricelist = await upsales.pricelists.get_by_code("PREMIUM")
            >>> if pricelist:
            ...     print(pricelist.name)
        """
        all_pricelists: list[Pricelist] = await self.list_all()
        for pricelist in all_pricelists:
            if pricelist.code and pricelist.code.upper() == code.upper():
                return pricelist
        return None
