"""
API Keys resource manager for Upsales API.

Provides methods to interact with the /apiKeys endpoint using ApiKey models.

Example:
    >>> async with Upsales(token="...") as upsales:
    ...     # Get single API key
    ...     apikey = await upsales.apikeys.get(1)
    ...     print(apikey.name, apikey.is_active)
    ...
    ...     # List API keys
    ...     apikeys = await upsales.apikeys.list(limit=10)
    ...
    ...     # Get all active API keys
    ...     active = await upsales.apikeys.get_active()
    ...
    ...     # Find API key by name
    ...     key = await upsales.apikeys.get_by_name("Production")
"""

from upsales.http import HTTPClient
from upsales.models.api_keys import ApiKey, PartialApiKey
from upsales.resources.base import BaseResource


class ApikeysResource(BaseResource[ApiKey, PartialApiKey]):
    """
    Resource manager for API Keys endpoint.

    Inherits standard CRUD operations from BaseResource:
    - get(id) - Get single API key
    - list(limit, offset, **params) - List API keys with pagination
    - list_all(**params) - Auto-paginated list of all API keys
    - create(**data) - Create new API key
    - update(id, **data) - Update API key
    - delete(id) - Delete API key
    - bulk_update(ids, data, max_concurrent) - Parallel updates
    - bulk_delete(ids, max_concurrent) - Parallel deletes

    Additional methods:
    - get_active() - Get all active API keys
    - get_inactive() - Get all inactive API keys
    - get_by_name() - Get API key by name

    Example:
        >>> apikeys = ApikeysResource(http_client)
        >>> apikey = await apikeys.get(1)
        >>> active = await apikeys.get_active()
        >>> key = await apikeys.get_by_name("Production")
    """

    def __init__(self, http: HTTPClient):
        """
        Initialize API keys resource manager.

        Args:
            http: HTTP client for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/apiKeys",
            model_class=ApiKey,
            partial_class=PartialApiKey,
        )

    async def get_active(self) -> list[ApiKey]:
        """
        Get all active API keys.

        Returns:
            List of API keys with active=True.

        Example:
            >>> active_keys = await upsales.apikeys.get_active()
            >>> for key in active_keys:
            ...     print(f"{key.name} - Active")
        """
        all_keys: list[ApiKey] = await self.list_all()
        return [key for key in all_keys if key.is_active]

    async def get_inactive(self) -> list[ApiKey]:
        """
        Get all inactive API keys.

        Returns:
            List of API keys with active=False.

        Example:
            >>> inactive_keys = await upsales.apikeys.get_inactive()
            >>> for key in inactive_keys:
            ...     print(f"{key.name} - Inactive")
        """
        all_keys: list[ApiKey] = await self.list_all()
        return [key for key in all_keys if not key.is_active]

    async def get_by_name(self, name: str) -> ApiKey | None:
        """
        Get API key by name.

        Args:
            name: API key name to search for (case-insensitive).

        Returns:
            ApiKey object if found, None otherwise.

        Example:
            >>> apikey = await upsales.apikeys.get_by_name("Production")
            >>> if apikey:
            ...     print(apikey.id, apikey.is_active)
        """
        all_keys: list[ApiKey] = await self.list_all()
        for key in all_keys:
            if key.name.lower() == name.lower():
                return key
        return None
