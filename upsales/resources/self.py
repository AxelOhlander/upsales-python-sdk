"""
Self resource manager for Upsales API.

Manages /api/v2/self endpoint operations.

IMPORTANT: Self endpoint is read-only and returns a single dict (not a list).
This endpoint provides current user session information including account details,
client info, version data, features, and addons.

This resource manager provides:
- get(): Get current user session info (single dict)

Standard operations like create(), update(), delete(), list() are not applicable.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from upsales.http import HTTPClient

from upsales.models.self import AccountManager, ClientDetail, Self, VersionData


class SelfResource:
    """
    Resource manager for /api/v2/self endpoint.

    Note: Unlike most resources, self returns a single dict with current user
    session information rather than a list of items. This endpoint is read-only.

    Args:
        http: HTTP client instance for making API requests.

    Attributes:
        _http: HTTP client for API requests.
        _endpoint: API endpoint path (/self).

    Example:
        >>> async with Upsales.from_env() as upsales:
        ...     # Get current user session info
        ...     self_data = await upsales.self.get()
        ...     print(f"User: {self_data.name}")
        ...     print(f"Email: {self_data.email}")
        ...     print(f"Version: {self_data.version}")
        ...
        ...     # Check products
        ...     if self_data.has_crm:
        ...         print("CRM is enabled")
        ...     if self_data.has_marketing_automation:
        ...         print("Marketing Automation is enabled")
        ...
        ...     # Check features
        ...     if self_data.has_feature('triggers'):
        ...         print("Triggers feature is enabled")
        ...
        ...     # Check addons
        ...     if self_data.has_addon('API_KEYS'):
        ...         print("API Keys addon is purchased")
        ...
        ...     # Access client info
        ...     print(f"Client: {self_data.client.name}")
        ...     print(f"Licenses: {self_data.client.numberOfLicenses}")
    """

    def __init__(self, http: HTTPClient) -> None:
        """
        Initialize self resource manager.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/self"

    async def get(self) -> Self:
        """
        Get current user session information.

        Returns current user info, client details, version data, features,
        and addons in a single Self object.

        Returns:
            Self object with all current user session information.

        Raises:
            UpsalesError: If API request fails.

        Example:
            >>> self_data = await upsales.self.get()
            >>> self_data.name
            'John Doe'
            >>> self_data.email
            'john.doe@example.com'
            >>> self_data.version
            'Enterprise'
            >>> self_data.has_crm
            True
            >>> self_data.client.name
            'Acme Corporation'
        """
        response = await self._http.get(self._endpoint)
        # Extract data from response wrapper
        return Self(**response["data"], _client=self._http._upsales_client)

    async def get_user_id(self) -> int:
        """
        Get current user ID.

        Convenience method to get just the user ID without fetching full data.

        Returns:
            Current user ID.

        Raises:
            UpsalesError: If API request fails.

        Example:
            >>> user_id = await upsales.self.get_user_id()
            >>> print(f"Current user ID: {user_id}")
            Current user ID: 1021058
        """
        self_data = await self.get()
        return self_data.id

    async def get_client_info(self) -> ClientDetail:
        """
        Get current client information.

        Convenience method to access client details without full self data.

        Returns:
            ClientDetail object with current client information.

        Raises:
            UpsalesError: If API request fails.

        Example:
            >>> client = await upsales.self.get_client_info()
            >>> print(f"Client: {client.name}")
            >>> print(f"Licenses: {client.numberOfLicenses}")
            >>> print(f"Trial: {client.is_trial}")
        """
        self_data = await self.get()
        return self_data.client

    async def get_version_info(self) -> VersionData:
        """
        Get version and feature information.

        Convenience method to access version data without full self data.

        Returns:
            VersionData object with version and feature information.

        Raises:
            UpsalesError: If API request fails.

        Example:
            >>> version = await upsales.self.get_version_info()
            >>> print(f"Version: {version.name}")
            >>> print(f"CRM: {version.has_crm}")
            >>> print(f"Features: {version.feature_count}")
        """
        self_data = await self.get()
        return self_data.versionData

    async def check_feature(self, feature_name: str) -> bool:
        """
        Check if a specific feature is enabled.

        Args:
            feature_name: Feature identifier to check.

        Returns:
            True if feature is enabled, False otherwise.

        Raises:
            UpsalesError: If API request fails.

        Example:
            >>> has_triggers = await upsales.self.check_feature('triggers')
            >>> print(f"Triggers enabled: {has_triggers}")
            Triggers enabled: True
        """
        self_data = await self.get()
        return self_data.has_feature(feature_name)

    async def check_addon(self, addon_name: str) -> bool:
        """
        Check if a specific addon is purchased.

        Args:
            addon_name: Addon identifier to check.

        Returns:
            True if addon is purchased, False otherwise.

        Raises:
            UpsalesError: If API request fails.

        Example:
            >>> has_api_keys = await upsales.self.check_addon('API_KEYS')
            >>> print(f"API Keys purchased: {has_api_keys}")
            API Keys purchased: True
        """
        self_data = await self.get()
        return self_data.has_addon(addon_name)

    async def get_account_manager(self) -> AccountManager:
        """
        Get account manager contact information.

        Returns:
            AccountManager object with contact information.

        Raises:
            UpsalesError: If API request fails.

        Example:
            >>> am = await upsales.self.get_account_manager()
            >>> print(f"{am.name} ({am.title})")
            >>> print(f"Email: {am.email}")
            >>> print(f"Phone: {am.phone}")
        """
        self_data = await self.get()
        return self_data.accountManager
