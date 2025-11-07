"""
Standard Integrations resource manager for Upsales API.

Provides methods to interact with the /standardIntegration endpoint.

Example:
    >>> async with Upsales(token="...") as upsales:
    ...     integration = await upsales.standard_integrations.get(1)
    ...     integrations = await upsales.standard_integrations.list(limit=10)
    ...     active = await upsales.standard_integrations.get_active()
"""

from upsales.http import HTTPClient
from upsales.models.standard_integration import (
    PartialStandardIntegration,
    StandardIntegration,
)
from upsales.resources.base import BaseResource


class StandardIntegrationsResource(BaseResource[StandardIntegration, PartialStandardIntegration]):
    """
    Resource manager for StandardIntegration endpoint.

    Inherits standard CRUD operations from BaseResource:
    - get(id) - Get single integration
    - list(limit, offset, **params) - List integrations with pagination
    - list_all(**params) - Auto-paginated list of all integrations
    - create(**data) - Create new integration
    - update(id, **data) - Update integration
    - delete(id) - Delete integration
    - bulk_update(ids, data, max_concurrent) - Parallel updates
    - bulk_delete(ids, max_concurrent) - Parallel deletes

    Example:
        >>> integrations = StandardIntegrationsResource(http_client)
        >>> integration = await integrations.get(1)
        >>> active_integrations = await integrations.get_active()
        >>> public_integrations = await integrations.get_public()
    """

    def __init__(self, http: HTTPClient):
        """
        Initialize standard integrations resource manager.

        Args:
            http: HTTP client for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/standardIntegration",
            model_class=StandardIntegration,
            partial_class=PartialStandardIntegration,
        )

    async def get_by_name(self, name: str) -> StandardIntegration | None:
        """
        Get integration by name.

        Args:
            name: Integration name to search for (case-insensitive).

        Returns:
            StandardIntegration object if found, None otherwise.

        Example:
            >>> integration = await upsales.standard_integrations.get_by_name(
            ...     "Salesforce"
            ... )
            >>> if integration:
            ...     print(f"Found: {integration.id}")
        """
        all_integrations: list[StandardIntegration] = await self.list_all()
        for integration in all_integrations:
            if integration.name.lower() == name.lower():
                return integration
        return None

    async def get_by_alias(self, alias: str) -> StandardIntegration | None:
        """
        Get integration by alias.

        Args:
            alias: Integration alias to search for.

        Returns:
            StandardIntegration object if found, None otherwise.

        Example:
            >>> integration = await upsales.standard_integrations.get_by_alias(
            ...     "salesforce-crm"
            ... )
            >>> if integration:
            ...     print(f"Found: {integration.name}")
        """
        all_integrations: list[StandardIntegration] = await self.list_all()
        for integration in all_integrations:
            if integration.alias and integration.alias.lower() == alias.lower():
                return integration
        return None

    async def get_active(self) -> list[StandardIntegration]:
        """
        Get all active integrations.

        Returns:
            List of integrations with active=True.

        Example:
            >>> active_integrations = await upsales.standard_integrations.get_active()
            >>> for integration in active_integrations:
            ...     print(f"{integration.name} is active")
        """
        all_integrations: list[StandardIntegration] = await self.list_all()
        return [i for i in all_integrations if i.active]

    async def get_visible(self) -> list[StandardIntegration]:
        """
        Get all visible integrations.

        Returns:
            List of integrations with visible=True.

        Example:
            >>> visible = await upsales.standard_integrations.get_visible()
            >>> for integration in visible:
            ...     print(f"{integration.name} is visible in UI")
        """
        all_integrations: list[StandardIntegration] = await self.list_all()
        return [i for i in all_integrations if i.visible]

    async def get_public(self) -> list[StandardIntegration]:
        """
        Get all public integrations.

        Returns:
            List of integrations with public=True.

        Example:
            >>> public = await upsales.standard_integrations.get_public()
            >>> for integration in public:
            ...     print(f"{integration.name} is publicly available")
        """
        all_integrations: list[StandardIntegration] = await self.list_all()
        return [i for i in all_integrations if i.public]

    async def get_by_category(self, category: str) -> list[StandardIntegration]:
        """
        Get integrations by category.

        Args:
            category: Category to filter by (e.g., "CRM", "Marketing").

        Returns:
            List of integrations matching the category.

        Example:
            >>> crm_integrations = await upsales.standard_integrations.get_by_category(
            ...     "CRM"
            ... )
            >>> for integration in crm_integrations:
            ...     print(f"{integration.name} - {integration.category}")
        """
        all_integrations: list[StandardIntegration] = await self.list_all()
        return [i for i in all_integrations if i.category.lower() == category.lower()]

    async def get_by_publisher(self, publisher_name: str) -> list[StandardIntegration]:
        """
        Get integrations by publisher name.

        Args:
            publisher_name: Publisher name to filter by (case-insensitive).

        Returns:
            List of integrations from the specified publisher.

        Example:
            >>> integrations = await upsales.standard_integrations.get_by_publisher(
            ...     "Acme Corp"
            ... )
            >>> for integration in integrations:
            ...     print(f"{integration.name} by {integration.publisherName}")
        """
        all_integrations: list[StandardIntegration] = await self.list_all()
        return [i for i in all_integrations if i.publisherName.lower() == publisher_name.lower()]

    async def get_with_api_key(self) -> list[StandardIntegration]:
        """
        Get integrations that require API keys.

        Returns:
            List of integrations with apiKey=True.

        Example:
            >>> api_key_integrations = await upsales.standard_integrations.get_with_api_key()
            >>> for integration in api_key_integrations:
            ...     print(f"{integration.name} requires API key")
        """
        all_integrations: list[StandardIntegration] = await self.list_all()
        return [i for i in all_integrations if i.apiKey]

    async def get_user_configurable(self) -> list[StandardIntegration]:
        """
        Get integrations that are user-configurable.

        Returns:
            List of integrations with userConfigurable=True.

        Example:
            >>> configurable = await upsales.standard_integrations.get_user_configurable()
            >>> for integration in configurable:
            ...     print(f"{integration.name} can be configured by users")
        """
        all_integrations: list[StandardIntegration] = await self.list_all()
        return [i for i in all_integrations if i.userConfigurable]

    async def get_with_pricing(self) -> list[StandardIntegration]:
        """
        Get integrations with pricing information.

        Returns:
            List of integrations that have price or pricePerUser set.

        Example:
            >>> paid_integrations = await upsales.standard_integrations.get_with_pricing()
            >>> for integration in paid_integrations:
            ...     if integration.pricePerUser:
            ...         print(f"{integration.name} - ${integration.pricePerUser}/user")
            ...     elif integration.price:
            ...         print(f"{integration.name} - ${integration.price}")
        """
        all_integrations: list[StandardIntegration] = await self.list_all()
        return [i for i in all_integrations if i.has_pricing]

    async def get_by_region(self, region: str) -> list[StandardIntegration]:
        """
        Get integrations by region.

        Args:
            region: Region to filter by (case-insensitive).

        Returns:
            List of integrations deployed in the specified region.

        Example:
            >>> us_integrations = await upsales.standard_integrations.get_by_region("US")
            >>> for integration in us_integrations:
            ...     print(f"{integration.name} - Region: {integration.region}")
        """
        all_integrations: list[StandardIntegration] = await self.list_all()
        return [i for i in all_integrations if i.region.lower() == region.lower()]
