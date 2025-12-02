"""User-defined object 2 resource for Upsales API."""

from __future__ import annotations

from typing import TYPE_CHECKING

from upsales.models.user_defined_object_2 import (
    PartialUserDefinedObject2,
    UserDefinedObject2,
)
from upsales.resources.base import BaseResource

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class UserDefinedObject2Resource(BaseResource[UserDefinedObject2, PartialUserDefinedObject2]):
    """Resource manager for user-defined objects (slot 2).

    Handles CRUD operations for user-defined custom objects.

    Example:
        ```python
        async with Upsales.from_env() as upsales:
            # Create user-defined object
            obj = await upsales.user_defined_object_2.create(
                notes="Main notes",
                clientId=1
            )

            # Get user-defined object
            obj = await upsales.user_defined_object_2.get(1)

            # List user-defined objects
            objects = await upsales.user_defined_object_2.list(limit=10)

            # Update user-defined object
            updated = await upsales.user_defined_object_2.update(
                1,
                notes="Updated notes",
                userId=2
            )

            # Delete user-defined object
            await upsales.user_defined_object_2.delete(1)
        ```
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize user-defined object 2 resource.

        Args:
            http: HTTP client instance for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/userDefinedObjects/2",
            model_class=UserDefinedObject2,
            partial_class=PartialUserDefinedObject2,
        )
