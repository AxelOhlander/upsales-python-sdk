"""
API Key models for Upsales API.

Generated from /api/v2/apiKeys endpoint.
Analysis based on 12 samples.

Enhanced with Pydantic v2 features:
- Field descriptions for all fields
- Computed fields for boolean helpers
- Strict type checking for read-only fields
- Optimized serialization
"""

from typing import TypedDict, Unpack

from pydantic import Field, computed_field

from upsales.models.base import BaseModel, PartialModel
from upsales.validators import NonEmptyStr


class ApiKeyUpdateFields(TypedDict, total=False):
    """
    Available fields for updating an API Key.

    All fields are optional. Use with Unpack for IDE autocomplete.
    """

    name: str
    active: bool


class ApiKey(BaseModel):
    """
    API Key model from /api/v2/apiKeys.

    Represents an API key for authenticating with the Upsales API.
    API keys can be created, activated, deactivated, and managed through
    the Upsales interface.

    Generated from 12 samples with field analysis.

    Example:
        >>> apikey = await upsales.apikeys.get(1)
        >>> apikey.name
        'Production API Key'
        >>> apikey.is_active
        True
        >>> await apikey.edit(active=False)
    """

    # Read-only fields (frozen=True, strict=True)
    id: int = Field(frozen=True, strict=True, description="Unique API key ID")

    # Required updatable fields
    name: NonEmptyStr = Field(description="API key name/description")
    active: bool = Field(default=True, description="Active status (true=active, false=inactive)")

    @computed_field
    @property
    def is_active(self) -> bool:
        """
        Check if API key is active.

        Returns:
            True if active flag is True, False otherwise.

        Example:
            >>> apikey.is_active
            True
        """
        return self.active

    async def edit(self, **kwargs: Unpack[ApiKeyUpdateFields]) -> "ApiKey":
        """
        Edit this API key.

        Uses Pydantic v2's optimized serialization via to_api_dict().

        Args:
            **kwargs: Fields to update (full IDE autocomplete support).

        Returns:
            Updated API key with fresh data from API.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> apikey = await upsales.apikeys.get(1)
            >>> updated = await apikey.edit(
            ...     name="New API Key Name",
            ...     active=False
            ... )
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.apikeys.update(self.id, **self.to_update_dict(**kwargs))


class PartialApiKey(PartialModel):
    """
    Partial API Key for nested responses.

    Contains minimal fields for when API Key appears nested in other
    API responses (though this is rare for API keys).

    Use fetch_full() to get complete ApiKey object with all fields.

    Example:
        >>> # If API key appeared nested somewhere
        >>> partial_apikey = some_object.apikey  # PartialApiKey
        >>> full_apikey = await partial_apikey.fetch_full()  # Now ApiKey
    """

    id: int = Field(frozen=True, strict=True, description="Unique API key ID")
    name: NonEmptyStr = Field(description="API key name/description")
    active: bool = Field(default=True, description="Active status (true=active, false=inactive)")

    async def fetch_full(self) -> ApiKey:
        """
        Fetch complete API key data.

        Returns:
            Full ApiKey object with all fields populated.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> partial = some_object.apikey  # PartialApiKey
            >>> full = await partial.fetch_full()  # ApiKey
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.apikeys.get(self.id)

    async def edit(self, **kwargs: Unpack[ApiKeyUpdateFields]) -> ApiKey:
        """
        Edit this API key.

        Returns full ApiKey object after update.

        Args:
            **kwargs: Fields to update (full IDE autocomplete support).

        Returns:
            Updated full ApiKey object.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> partial = some_object.apikey  # PartialApiKey
            >>> updated = await partial.edit(name="New Name")  # Returns ApiKey
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.apikeys.update(self.id, **kwargs)
