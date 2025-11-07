"""
Metadata resource manager for Upsales API.

Manages /api/v2/metadata endpoint operations.

IMPORTANT: Metadata endpoint is read-only and returns a single dict (not a list).
This endpoint provides system configuration, user info, currency settings,
and field definitions.

This resource manager provides:
- get(): Get system metadata (single dict)

Standard operations like create(), update(), delete(), list() are not applicable.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from upsales.http import HTTPClient

from upsales.models.metadata import Currency, FieldDefinition, Metadata, MetadataUser


class MetadataResource:
    """
    Resource manager for /api/v2/metadata endpoint.

    Note: Unlike most resources, metadata returns a single dict with system
    information rather than a list of items. This endpoint is read-only.

    Args:
        http: HTTP client instance for making API requests.

    Attributes:
        _http: HTTP client for API requests.
        _endpoint: API endpoint path (/metadata).

    Example:
        >>> async with Upsales.from_env() as upsales:
        ...     # Get system metadata
        ...     metadata = await upsales.metadata.get()
        ...     print(f"Version: {metadata.version}")
        ...     print(f"Licenses: {metadata.licenses}")
        ...     print(f"User: {metadata.user.name}")
        ...
        ...     # Access currencies
        ...     for currency in metadata.active_currencies:
        ...         print(f"{currency.iso}: {currency.rate}")
        ...
        ...     # Check field definitions
        ...     client_fields = metadata.get_entity_fields('Client')
        ...     print(f"Client has {len(client_fields)} standard fields")
    """

    def __init__(self, http: HTTPClient) -> None:
        """
        Initialize metadata resource manager.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/metadata"

    async def get(self) -> Metadata:
        """
        Get system metadata.

        Returns system configuration, user information, currency settings,
        and field definitions in a single Metadata object.

        Returns:
            Metadata object with all system information.

        Raises:
            UpsalesError: If API request fails.

        Example:
            >>> metadata = await upsales.metadata.get()
            >>> metadata.version
            'Enterprise'
            >>> metadata.licenses
            10
            >>> metadata.user.name
            'John Doe'
            >>> metadata.has_multi_currency
            True
        """
        response = await self._http.get(self._endpoint)
        # Extract data from response wrapper
        return Metadata(**response["data"], _client=self._http._upsales_client)

    async def get_currencies(self) -> list[Currency]:
        """
        Get all available currencies from metadata.

        Convenience method to access currency list without fetching full metadata.

        Returns:
            List of Currency objects.

        Raises:
            UpsalesError: If API request fails.

        Example:
            >>> currencies = await upsales.metadata.get_currencies()
            >>> for currency in currencies:
            ...     print(f"{currency.iso}: {currency.rate}")
            USD: 0.106791513
            EUR: 0.091776799
            SEK: 1.0
        """
        metadata = await self.get()
        return metadata.customerCurrencies

    async def get_default_currency(self) -> Currency:
        """
        Get the default system currency.

        Returns:
            Default Currency object.

        Raises:
            UpsalesError: If API request fails.

        Example:
            >>> default = await upsales.metadata.get_default_currency()
            >>> print(f"Default currency: {default.iso}")
            Default currency: SEK
        """
        metadata = await self.get()
        return metadata.defaultCurrency

    async def get_entity_fields(self, entity_type: str) -> dict[str, FieldDefinition]:
        """
        Get field definitions for an entity type.

        Args:
            entity_type: Entity type (e.g., 'Client', 'Contact', 'Order',
                'Activity', 'Appointment', 'Agreement', 'Product')

        Returns:
            Dictionary of field name to FieldDefinition.

        Raises:
            KeyError: If entity type not found.
            UpsalesError: If API request fails.

        Example:
            >>> client_fields = await upsales.metadata.get_entity_fields('Client')
            >>> name_field = client_fields['Name']
            >>> print(f"Name field type: {name_field.type}")
            Name field type: String
            >>> print(f"Name field required: {name_field.is_required}")
            Name field required: False
        """
        metadata = await self.get()
        return metadata.get_entity_fields(entity_type)

    async def get_required_fields(self, entity_type: str) -> dict[str, bool]:
        """
        Get required field configuration for an entity type.

        Args:
            entity_type: Entity type (e.g., 'Client', 'Contact', 'Order')

        Returns:
            Dictionary of field name to required status.

        Raises:
            KeyError: If entity type not found.
            UpsalesError: If API request fails.

        Example:
            >>> required = await upsales.metadata.get_required_fields('Client')
            >>> print(f"Name required: {required['Name']}")
            Name required: False
            >>> print(f"Phone required: {required['Phone']}")
            Phone required: False
        """
        metadata = await self.get()
        return metadata.get_required_fields(entity_type)

    async def is_field_required(self, entity_type: str, field_name: str) -> bool:
        """
        Check if a specific field is required for an entity type.

        Args:
            entity_type: Entity type (e.g., 'Client', 'Contact', 'Order')
            field_name: Field name (e.g., 'Name', 'Email', 'Phone')

        Returns:
            True if field is required, False otherwise.

        Raises:
            UpsalesError: If API request fails.

        Example:
            >>> is_required = await upsales.metadata.is_field_required('Contact', 'Email')
            >>> print(f"Email required: {is_required}")
            Email required: False
        """
        metadata = await self.get()
        return metadata.is_field_required(entity_type, field_name)

    async def get_user_info(self) -> MetadataUser:
        """
        Get current user information from metadata.

        Returns:
            MetadataUser object with current user information.

        Raises:
            UpsalesError: If API request fails.

        Example:
            >>> user = await upsales.metadata.get_user_info()
            >>> print(f"User: {user.name}")
            User: John Doe
            >>> print(f"Admin: {user.is_admin}")
            Admin: True
            >>> print(f"Role ID: {user.roleId}")
            Role ID: 5
        """
        metadata = await self.get()
        return metadata.user

    async def get_system_version(self) -> str:
        """
        Get Upsales system version.

        Returns:
            Version string (e.g., 'Enterprise', 'Professional')

        Raises:
            UpsalesError: If API request fails.

        Example:
            >>> version = await upsales.metadata.get_system_version()
            >>> print(f"Version: {version}")
            Version: Enterprise
        """
        metadata = await self.get()
        return metadata.version

    async def get_license_count(self) -> int:
        """
        Get number of licenses.

        Returns:
            Number of user licenses.

        Raises:
            UpsalesError: If API request fails.

        Example:
            >>> licenses = await upsales.metadata.get_license_count()
            >>> print(f"Licenses: {licenses}")
            Licenses: 10
        """
        metadata = await self.get()
        return metadata.licenses
