"""
Standard Integration User Settings model.

User-specific integration settings for Upsales integrations.
"""

from typing import TypedDict, Unpack

from pydantic import Field

from upsales.models.base import BaseModel, PartialModel
from upsales.validators import BinaryFlag


class StandardIntegrationUserSettingsUpdateFields(TypedDict, total=False):
    """Fields that can be updated in StandardIntegrationUserSettings."""

    active: int
    configJson: str


class StandardIntegrationUserSettings(BaseModel):
    """
    Standard Integration User Settings model.

    Represents user-specific configuration for integrations.

    Attributes:
        id: Unique identifier.
        userId: User ID associated with this setting.
        integrationId: Integration ID.
        version: Version number.
        regDate: Registration date (ISO 8601 format).
        modDate: Modification date (ISO 8601 format).
        active: Active status (0 or 1).
        configJson: JSON configuration string.

    Example:
        >>> settings = StandardIntegrationUserSettings(
        ...     id=1,
        ...     userId=123,
        ...     integrationId=456,
        ...     version=1,
        ...     active=1,
        ...     configJson='{"key": "value"}'
        ... )
        >>> settings.is_active
        True
        >>> await settings.edit(active=0)
    """

    # Read-only fields
    id: int = Field(frozen=True, strict=True, description="Unique identifier")
    userId: int = Field(frozen=True, description="User ID")
    integrationId: int = Field(frozen=True, description="Integration ID")
    version: int | None = Field(None, frozen=True, description="Version number")
    regDate: str | None = Field(None, frozen=True, description="Registration date")
    modDate: str | None = Field(None, description="Modification date")

    # Updatable fields
    active: BinaryFlag = Field(default=1, description="Active status (0 or 1)")
    configJson: str | None = Field(None, description="JSON configuration string")

    @property
    def is_active(self) -> bool:
        """Check if the setting is active."""
        return self.active == 1

    async def edit(
        self, **kwargs: Unpack[StandardIntegrationUserSettingsUpdateFields]
    ) -> "StandardIntegrationUserSettings":
        """
        Edit this standard integration user setting.

        Args:
            **kwargs: Fields to update (active, configJson).

        Returns:
            Updated StandardIntegrationUserSettings instance.

        Raises:
            RuntimeError: If no client is available.

        Example:
            >>> settings = await upsales.standard_integration_user_settings.get(1)
            >>> updated = await settings.edit(active=0)
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.standard_integration_user_settings.update(
            self.id, **self.to_api_dict(**kwargs)
        )


class PartialStandardIntegrationUserSettings(PartialModel):
    """
    Partial Standard Integration User Settings model.

    Used when StandardIntegrationUserSettings appears as nested data in other responses.

    Attributes:
        id: Unique identifier.
        userId: User ID.
        integrationId: Integration ID.
        active: Active status (0 or 1).

    Example:
        >>> partial = PartialStandardIntegrationUserSettings(
        ...     id=1,
        ...     userId=123,
        ...     integrationId=456,
        ...     active=1
        ... )
        >>> full = await partial.fetch_full()
    """

    id: int = Field(description="Unique identifier")
    userId: int | None = Field(None, description="User ID")
    integrationId: int | None = Field(None, description="Integration ID")
    active: BinaryFlag = Field(default=1, description="Active status (0 or 1)")

    async def fetch_full(self) -> StandardIntegrationUserSettings:
        """
        Fetch complete StandardIntegrationUserSettings data.

        Returns:
            Full StandardIntegrationUserSettings instance.

        Raises:
            RuntimeError: If no client is available.

        Example:
            >>> partial = PartialStandardIntegrationUserSettings(id=1)
            >>> full = await partial.fetch_full()
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.standard_integration_user_settings.get(self.id)

    async def edit(
        self, **kwargs: Unpack[StandardIntegrationUserSettingsUpdateFields]
    ) -> StandardIntegrationUserSettings:
        """
        Edit this standard integration user setting.

        Args:
            **kwargs: Fields to update.

        Returns:
            Updated StandardIntegrationUserSettings instance.

        Raises:
            RuntimeError: If no client is available.

        Example:
            >>> partial = PartialStandardIntegrationUserSettings(id=1)
            >>> updated = await partial.edit(active=0)
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.standard_integration_user_settings.update(self.id, **kwargs)
