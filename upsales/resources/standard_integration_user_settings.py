"""
StandardIntegrationUserSettings resource manager for Upsales API.

Provides methods to interact with the /standardIntegrationUserSettings endpoint.

Example:
    >>> async with Upsales(token="...") as upsales:
    ...     setting = await upsales.standard_integration_user_settings.get(1)
    ...     settings_list = await upsales.standard_integration_user_settings.list(limit=10)
"""

from upsales.http import HTTPClient
from upsales.models.standard_integration_user_settings import (
    PartialStandardIntegrationUserSettings,
    StandardIntegrationUserSettings,
)
from upsales.resources.base import BaseResource


class StandardIntegrationUserSettingsResource(
    BaseResource[StandardIntegrationUserSettings, PartialStandardIntegrationUserSettings]
):
    """
    Resource manager for StandardIntegrationUserSettings endpoint.

    Inherits standard CRUD operations from BaseResource:
    - get(id) - Get single standard integration user setting
    - list(limit, offset, **params) - List settings with pagination
    - list_all(**params) - Auto-paginated list of all settings
    - create(**data) - Create new setting
    - update(id, **data) - Update setting
    - delete(id) - Delete setting
    - bulk_update(ids, data, max_concurrent) - Parallel updates
    - bulk_delete(ids, max_concurrent) - Parallel deletes

    Example:
        >>> resource = StandardIntegrationUserSettingsResource(http_client)
        >>> setting = await resource.get(1)
        >>> all_active = await resource.list_all(active=1)
    """

    def __init__(self, http: HTTPClient):
        """
        Initialize standard integration user settings resource manager.

        Args:
            http: HTTP client for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/standardIntegrationUserSettings",
            model_class=StandardIntegrationUserSettings,
            partial_class=PartialStandardIntegrationUserSettings,
        )

    async def get_active(self) -> list[StandardIntegrationUserSettings]:
        """
        Get all active standard integration user settings.

        Returns:
            List of active settings.

        Example:
            >>> active_settings = await upsales.standard_integration_user_settings.get_active()
        """
        return await self.list_all(active=1)
