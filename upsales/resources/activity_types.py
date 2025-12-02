"""
Activity Types resource manager for Upsales API.

Provides methods to interact with the /activitytypes/activity endpoint.

Example:
    >>> async with Upsales(token="...") as upsales:
    ...     activity_type = await upsales.activity_types.get(1)
    ...     types_list = await upsales.activity_types.list(limit=10)
"""

from upsales.http import HTTPClient
from upsales.models.activity_types import ActivityType, PartialActivityType
from upsales.resources.base import BaseResource


class ActivityTypesResource(BaseResource[ActivityType, PartialActivityType]):
    """
    Resource manager for ActivityType endpoint.

    Inherits standard CRUD operations from BaseResource:
    - get(id) - Get single activity type
    - list(limit, offset, **params) - List activity types with pagination
    - list_all(**params) - Auto-paginated list of all activity types
    - create(**data) - Create new activity type
    - update(id, **data) - Update activity type
    - delete(id) - Delete activity type
    - bulk_update(ids, data, max_concurrent) - Parallel updates
    - bulk_delete(ids, max_concurrent) - Parallel deletes

    Example:
        >>> activity_types = ActivityTypesResource(http_client)
        >>> activity_type = await activity_types.get(1)
        >>> types_list = await activity_types.list(limit=100)
        >>> all_types = await activity_types.list_all()
    """

    def __init__(self, http: HTTPClient):
        """
        Initialize activity types resource manager.

        Args:
            http: HTTP client for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/activitytypes/activity",
            model_class=ActivityType,
            partial_class=PartialActivityType,
        )

    # Add activity type-specific methods here as needed
