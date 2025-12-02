"""Standard integration settings resource manager."""

from upsales.http import HTTPClient
from upsales.models.standard_integration_settings import (
    PartialStandardIntegrationSettings,
    StandardIntegrationSettings,
)
from upsales.resources.base import BaseResource


class StandardIntegrationSettingsResource(
    BaseResource[StandardIntegrationSettings, PartialStandardIntegrationSettings]
):
    """Resource manager for standard integration settings endpoints.

    Provides CRUD operations and search capabilities for standard integration
    settings with configuration management.

    Attributes:
        http: HTTP client for API requests
        endpoint: API endpoint path (/api/v2/standardIntegrationSettings)
        model_class: StandardIntegrationSettings model
        partial_class: PartialStandardIntegrationSettings model

    Example:
        >>> # List all integration settings
        >>> settings_list = await upsales.standard_integration_settings.list()
        >>> for settings in settings_list:
        ...     print(f"{settings.integrationId} v{settings.version}")
        >>>
        >>> # Get specific settings
        >>> settings = await upsales.standard_integration_settings.get(1)
        >>> print(settings.configJson)
        >>>
        >>> # Create new settings
        >>> new_settings = await upsales.standard_integration_settings.create(
        ...     integrationId=10,
        ...     version="1.0.0",
        ...     active=1,
        ...     configJson='{"key": "value"}'
        ... )
        >>>
        >>> # Update settings
        >>> updated = await upsales.standard_integration_settings.update(
        ...     1,
        ...     version="2.0.0",
        ...     active=1
        ... )
        >>>
        >>> # Search for active settings
        >>> active_settings = await upsales.standard_integration_settings.search(
        ...     active=1
        ... )
        >>>
        >>> # Delete settings
        >>> await upsales.standard_integration_settings.delete(1)
    """

    def __init__(self, http: HTTPClient):
        """Initialize the standard integration settings resource manager.

        Args:
            http: HTTP client instance for making API requests
        """
        super().__init__(
            http=http,
            endpoint="/standardIntegrationSettings",
            model_class=StandardIntegrationSettings,
            partial_class=PartialStandardIntegrationSettings,
        )

    async def get_by_integration_id(self, integration_id: int) -> list[StandardIntegrationSettings]:
        """Get all settings for a specific integration.

        Args:
            integration_id: Integration identifier to filter by

        Returns:
            List of settings for the specified integration

        Raises:
            AuthenticationError: If authentication fails
            ServerError: If server error occurs

        Example:
            >>> settings = await upsales.standard_integration_settings.get_by_integration_id(10)
            >>> for s in settings:
            ...     print(f"Version {s.version}: {s.is_active}")
        """
        return await self.search(integrationId=integration_id)

    async def get_active_settings(self) -> list[StandardIntegrationSettings]:
        """Get all active integration settings.

        Returns:
            List of active settings (active=1)

        Raises:
            AuthenticationError: If authentication fails
            ServerError: If server error occurs

        Example:
            >>> active = await upsales.standard_integration_settings.get_active_settings()
            >>> print(f"Found {len(active)} active integrations")
        """
        return await self.search(active=1)
