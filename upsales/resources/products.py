"""
Products resource manager for Upsales API.

Provides methods to interact with the /products endpoint using Product models.

Example:
    >>> async with Upsales(token="...") as upsales:
    ...     # Get single product
    ...     product = await upsales.products.get(1)
    ...     print(product.name, product.profit_margin)
    ...
    ...     # List products
    ...     products = await upsales.products.list(limit=10)
    ...
    ...     # Get all active products
    ...     active = await upsales.products.get_active()
    ...
    ...     # Bulk deactivate
    ...     await upsales.products.bulk_deactivate([1, 2, 3])
"""

from upsales.http import HTTPClient
from upsales.models.product import PartialProduct, Product
from upsales.resources.base import BaseResource


class ProductsResource(BaseResource[Product, PartialProduct]):
    """
    Resource manager for Product endpoint.

    Inherits standard CRUD operations from BaseResource:
    - get(id) - Get single product
    - list(limit, offset, **params) - List products with pagination
    - list_all(**params) - Auto-paginated list of all products
    - update(id, **data) - Update product
    - delete(id) - Delete product
    - bulk_update(ids, data, max_concurrent) - Parallel updates
    - bulk_delete(ids, max_concurrent) - Parallel deletes

    Additional methods:
    - get_active() - Get all active products
    - get_recurring() - Get all recurring products
    - bulk_deactivate(ids) - Deactivate multiple products

    Example:
        >>> products = ProductsResource(http_client)
        >>> product = await products.get(1)
        >>> all_active = await products.get_active()
        >>> await products.bulk_deactivate([1, 2, 3])
    """

    def __init__(self, http: HTTPClient):
        """
        Initialize products resource manager.

        Args:
            http: HTTP client for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/products",
            model_class=Product,
            partial_class=PartialProduct,
        )

    async def get_active(self) -> list[Product]:
        """
        Get all active products.

        Returns:
            List of active products (active=1).

        Example:
            >>> active_products = await upsales.products.get_active()
            >>> len(active_products)
            15
        """
        return await self.list_all(active=1)

    async def get_recurring(self) -> list[Product]:
        """
        Get all recurring products.

        Returns:
            List of recurring products (isRecurring=1).

        Example:
            >>> recurring = await upsales.products.get_recurring()
            >>> for product in recurring:
            ...     print(f"{product.name}: every {product.recurringInterval} months")
        """
        return await self.list_all(isRecurring=1)

    async def bulk_deactivate(self, ids: list[int], max_concurrent: int = 10) -> list[Product]:
        """
        Deactivate multiple products in parallel.

        Args:
            ids: List of product IDs to deactivate.
            max_concurrent: Maximum concurrent requests (default: 10).

        Returns:
            List of updated Product objects.

        Raises:
            ExceptionGroup: If any updates fail.

        Example:
            >>> deactivated = await upsales.products.bulk_deactivate([1, 2, 3])
            >>> all(p.active == 0 for p in deactivated)
            True

        Note:
            With Python 3.13 free-threaded mode, these updates can run in
            true parallel without GIL contention. Enable with: python -X gil=0
        """
        return await self.bulk_update(ids, {"active": 0}, max_concurrent=max_concurrent)
