"""Standard integration settings models for Upsales API.

This module provides models for managing standard integration settings with
configuration management capabilities.
"""

from __future__ import annotations

from typing import TypedDict, Unpack

from pydantic import Field

from upsales.models.base import BaseModel, PartialModel
from upsales.validators import BinaryFlag  # noqa: TC001


class StandardIntegrationSettingsUpdateFields(TypedDict, total=False):
    """Available fields for updating StandardIntegrationSettings.

    All fields are optional to support partial updates.
    """

    version: str
    active: int
    configJson: str


class StandardIntegrationSettingsCreateFields(TypedDict, total=False):
    """Available fields for creating StandardIntegrationSettings.

    Required fields:
        integrationId: Integration identifier

    Optional fields:
        version: Version string
        active: Active status (0 or 1)
        configJson: Configuration JSON string
    """

    integrationId: int  # Required
    version: str
    active: int
    configJson: str


class StandardIntegrationSettings(BaseModel):
    """Standard integration settings with configuration management.

    Represents settings for standard integrations including version tracking
    and JSON-based configuration.

    Attributes:
        id: Unique identifier (read-only)
        integrationId: Integration identifier (read-only after creation)
        version: Version string
        regDate: Registration date (read-only)
        modDate: Modification date (read-only)
        active: Active status (0 or 1)
        configJson: Configuration JSON string

    Example:
        >>> settings = await upsales.standard_integration_settings.get(1)
        >>> print(f"Integration {settings.integrationId} v{settings.version}")
        >>> if settings.is_active:
        ...     print("Integration is active")
        >>> await settings.edit(version="2.0.0", active=1)
    """

    # Read-only fields
    id: int = Field(frozen=True, strict=True, description="Unique identifier")
    integrationId: int = Field(frozen=True, strict=True, description="Integration identifier")
    regDate: str | None = Field(None, frozen=True, description="Registration date")
    modDate: str | None = Field(None, frozen=True, description="Modification date")

    # Updatable fields
    version: str | None = Field(None, description="Version string")
    active: BinaryFlag = Field(default=1, description="Active status (0 or 1)")
    configJson: str | None = Field(None, description="Configuration JSON string")

    @property
    def is_active(self) -> bool:
        """Check if the integration settings are active.

        Returns:
            True if active == 1, False otherwise

        Example:
            >>> if settings.is_active:
            ...     print("Integration is enabled")
        """
        return self.active == 1

    async def edit(
        self, **kwargs: Unpack[StandardIntegrationSettingsUpdateFields]
    ) -> StandardIntegrationSettings:
        """Edit this standard integration settings instance.

        Provides full IDE autocomplete for available fields. Only non-frozen
        fields can be updated.

        Args:
            **kwargs: Fields to update (version, active, configJson)

        Returns:
            Updated StandardIntegrationSettings instance

        Raises:
            RuntimeError: If no client is available
            ValidationError: If field validation fails
            NotFoundError: If settings not found
            AuthenticationError: If authentication fails

        Example:
            >>> settings = await upsales.standard_integration_settings.get(1)
            >>> updated = await settings.edit(
            ...     version="2.0.0",
            ...     active=1,
            ...     configJson='{"key": "value"}'
            ... )
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.standard_integration_settings.update(
            self.id, **self.to_api_dict(**kwargs)
        )


class PartialStandardIntegrationSettings(PartialModel):
    """Partial standard integration settings for nested responses.

    Used when standard integration settings appear as nested objects in API responses.

    Attributes:
        id: Unique identifier
        integrationId: Integration identifier
        version: Version string (optional)
        active: Active status (optional)

    Example:
        >>> partial = PartialStandardIntegrationSettings(id=1, integrationId=10)
        >>> full = await partial.fetch_full()
        >>> print(full.configJson)
    """

    id: int = Field(description="Unique identifier")
    integrationId: int = Field(description="Integration identifier")
    version: str | None = Field(None, description="Version string")
    active: int | None = Field(None, description="Active status (0 or 1)")

    async def fetch_full(self) -> StandardIntegrationSettings:
        """Fetch the complete StandardIntegrationSettings object.

        Returns:
            Full StandardIntegrationSettings instance

        Raises:
            RuntimeError: If no client is available
            NotFoundError: If settings not found
            AuthenticationError: If authentication fails

        Example:
            >>> partial = contact.integration_settings
            >>> full = await partial.fetch_full()
            >>> print(full.configJson)
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.standard_integration_settings.get(self.id)

    async def edit(
        self, **kwargs: Unpack[StandardIntegrationSettingsUpdateFields]
    ) -> StandardIntegrationSettings:
        """Edit this standard integration settings using its ID.

        Args:
            **kwargs: Fields to update

        Returns:
            Updated StandardIntegrationSettings instance

        Raises:
            RuntimeError: If no client is available
            ValidationError: If field validation fails
            NotFoundError: If settings not found

        Example:
            >>> partial = contact.integration_settings
            >>> updated = await partial.edit(active=0)
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.standard_integration_settings.update(self.id, **kwargs)
