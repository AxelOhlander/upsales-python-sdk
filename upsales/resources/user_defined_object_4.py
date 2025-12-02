"""User-defined object 4 resource for Upsales API."""

from __future__ import annotations

from typing import TYPE_CHECKING

from upsales.models.user_defined_object_4 import (
    PartialUserDefinedObject4,
    UserDefinedObject4,
)
from upsales.resources.base import BaseResource

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class UserDefinedObject4Resource(BaseResource[UserDefinedObject4, PartialUserDefinedObject4]):
    """Resource manager for user-defined objects (slot 4).

    Handles CRUD operations for user-defined custom objects.

    Example:
        ```python
        async with Upsales.from_env() as upsales:
            # Create user-defined object
            obj = await upsales.user_defined_object_4.create(
                notes="Main notes",
                clientId=1
            )

            # Get user-defined object
            obj = await upsales.user_defined_object_4.get(1)

            # List user-defined objects
            objects = await upsales.user_defined_object_4.list(limit=10)

            # Update user-defined object
            updated = await upsales.user_defined_object_4.update(
                1,
                notes="Updated notes",
                userId=2
            )

            # Delete user-defined object
            await upsales.user_defined_object_4.delete(1)
        ```
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize user-defined object 4 resource.

        Args:
            http: HTTP client instance for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/userDefinedObjects/4",
            model_class=UserDefinedObject4,
            partial_class=PartialUserDefinedObject4,
        )
