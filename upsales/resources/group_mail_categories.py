"""
Group mail categories resource manager for Upsales API.

Provides methods to interact with the /api/v2/groupMailCategories endpoint.

Example:
    >>> async with Upsales(token="...") as upsales:
    ...     category = await upsales.group_mail_categories.get(1)
    ...     categories = await upsales.group_mail_categories.list(limit=10)
    ...     active = await upsales.group_mail_categories.get_active()
"""

from upsales.http import HTTPClient
from upsales.models.group_mail_categories import (
    GroupMailCategory,
    PartialGroupMailCategory,
)
from upsales.resources.base import BaseResource


class GroupMailCategoriesResource(BaseResource[GroupMailCategory, PartialGroupMailCategory]):
    """
    Resource manager for GroupMailCategory endpoint.

    Inherits standard CRUD operations from BaseResource:
    - get(id) - Get single group mail category
    - list(limit, offset, **params) - List categories with pagination
    - list_all(**params) - Auto-paginated list of all categories
    - create(**data) - Create new category
    - update(id, **data) - Update category
    - delete(id) - Delete category
    - search(**filters) - Search with comparison operators
    - bulk_update(ids, data, max_concurrent) - Parallel updates
    - bulk_delete(ids, max_concurrent) - Parallel deletes

    Example:
        >>> resource = GroupMailCategoriesResource(http_client)
        >>> category = await resource.get(1)
        >>> all_active = await resource.get_active()
        >>> new_category = await resource.create(
        ...     title="Newsletter",
        ...     description="Monthly newsletters"
        ... )
    """

    def __init__(self, http: HTTPClient):
        """
        Initialize group mail categories resource manager.

        Args:
            http: HTTP client for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/groupMailCategories",
            model_class=GroupMailCategory,
            partial_class=PartialGroupMailCategory,
        )

    async def get_active(self) -> list[GroupMailCategory]:
        """
        Get all active group mail categories.

        Returns:
            List of active categories (where active=1).

        Example:
            >>> categories = await upsales.group_mail_categories.get_active()
            >>> for category in categories:
            ...     print(category.title)
        """
        return await self.list_all(active=1)
