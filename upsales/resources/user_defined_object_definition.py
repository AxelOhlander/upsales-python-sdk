"""User-defined object definitions resource manager for Upsales API.

Provides methods to interact with the /userDefinedDefinition endpoint.

Note:
    This endpoint only supports POST (create) and DELETE operations.
    GET and UPDATE operations are not available.

Example:
    >>> async with Upsales(token="...") as upsales:
    ...     definition = await upsales.user_defined_object_definitions.create(
    ...         name="Custom Type",
    ...         description="A custom entity",
    ...         fields=[{"name": "field1", "type": "string"}]
    ...     )
    ...     await upsales.user_defined_object_definitions.delete(definition.id)
"""

from upsales.http import HTTPClient
from upsales.models.user_defined_object_definition import (
    PartialUserDefinedObjectDefinition,
    UserDefinedObjectDefinition,
)
from upsales.resources.base import BaseResource


class UserDefinedObjectDefinitionsResource(
    BaseResource[UserDefinedObjectDefinition, PartialUserDefinedObjectDefinition]
):
    """Resource manager for UserDefinedObjectDefinition endpoint.

    This endpoint allows creating and deleting custom object type definitions.
    Note that GET and UPDATE operations are not supported by the API.

    Supported operations:
    - create(**data) - Create new definition
    - delete(id) - Delete definition

    Not supported:
    - get(id) - Not available for this endpoint
    - list(...) - Not available for this endpoint
    - update(id, **data) - Not available for this endpoint

    Example:
        >>> resource = UserDefinedObjectDefinitionsResource(http_client)
        >>> definition = await resource.create(
        ...     name="Projects",
        ...     description="Custom project tracking",
        ...     fields=[{"name": "status", "type": "string"}]
        ... )
        >>> await resource.delete(definition.id)
    """

    def __init__(self, http: HTTPClient):
        """Initialize user-defined object definitions resource manager.

        Args:
            http: HTTP client for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/userDefinedDefinition",
            model_class=UserDefinedObjectDefinition,
            partial_class=PartialUserDefinedObjectDefinition,
        )
