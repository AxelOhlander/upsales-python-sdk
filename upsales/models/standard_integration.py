"""
StandardIntegration models for Upsales API.

Generated from /api/v2/standardIntegration endpoint.
Analysis based on 56 samples.

Enhanced with Pydantic v2 features:
- Reusable validators (BinaryFlag, NonEmptyStr)
- Computed fields (@computed_field)
- Field descriptions for documentation
- Strict type checking (frozen=True for read-only fields)
- Optimized serialization (to_api_dict)
- TypedDict for IDE autocomplete

Example:
    >>> integration = await upsales.standard_integrations.get(1)
    >>> integration.name
    'Salesforce Integration'
    >>> integration.is_active
    True
    >>> integration.supports_api_key
    False
    >>> await integration.edit(active=False, description="Updated description")
"""

from typing import Any, TypedDict, Unpack

from pydantic import Field, computed_field

from upsales.models.base import BaseModel, PartialModel
from upsales.validators import NonEmptyStr


class StandardIntegrationUpdateFields(TypedDict, total=False):
    """
    Available fields for updating a StandardIntegration.

    All fields are optional. Use with Unpack for IDE autocomplete.

    Example:
        >>> await integration.edit(
        ...     name="Updated Integration",
        ...     description="New description",
        ...     active=True
        ... )
    """

    name: str
    description: str
    descriptionLong: str
    alias: str
    category: str
    url: str
    imageLink: str
    color: str
    version: str
    active: bool
    visible: bool
    public: bool
    userOnly: bool
    userConfigurable: bool
    externalConfig: bool
    apiKey: bool
    hideForNew: bool
    endpoint: str
    authenticationKey: str
    supportEmail: str
    hostingProvider: str
    hostingLocation: str
    region: str
    langTagPrefix: str
    configJson: str
    price: int
    pricePerUser: int
    env: int
    publisherClientId: int
    publisherName: str
    termsAccepted: str
    termsAcceptedUser: str
    inputDebounceInMs: int | None
    contract: dict[str, Any]
    userContract: dict[str, Any]
    standardIntegrationInit: list[dict[str, Any]]
    standardIntegrationTag: list[Any]


class StandardIntegration(BaseModel):
    """
    StandardIntegration model from /api/v2/standardIntegration.

    Represents an integration available in the Upsales system, including
    configuration, availability, and publisher information.

    Enhanced with Pydantic v2 validators, computed fields, and optimized serialization.
    Generated from 56 samples with field analysis.

    Example:
        >>> integration = await upsales.standard_integrations.get(1)
        >>> print(f"{integration.name} by {integration.publisherName}")
        'Salesforce Integration by Acme Corp'
        >>> if integration.is_active:
        ...     print(f"Active: {integration.url}")
        >>> await integration.edit(description="Updated description")
    """

    # Read-only fields
    id: int = Field(frozen=True, strict=True, description="Unique standard integration ID")

    # Core identification fields
    name: NonEmptyStr = Field(description="Integration name")
    description: str = Field(default="", description="Short integration description")
    descriptionLong: str = Field(default="", description="Detailed integration description")
    alias: str | None = Field(None, description="URL-friendly alias for the integration")

    # Categorization and branding
    category: NonEmptyStr = Field(description="Integration category (e.g., 'CRM', 'Marketing')")
    url: str | None = Field(None, description="Integration website or documentation URL")
    imageLink: str | None = Field(None, description="URL to integration logo/image")
    color: NonEmptyStr = Field(description="Brand color for UI display (hex code)")
    version: NonEmptyStr = Field(description="Integration version number")

    # Availability flags
    active: bool = Field(description="Whether integration is currently active")
    visible: bool = Field(description="Whether integration is visible in the UI")
    public: bool = Field(description="Whether integration is publicly available")
    userOnly: bool = Field(description="Whether integration is user-specific")
    hideForNew: bool = Field(description="Hide integration from new installations")

    # Configuration flags
    userConfigurable: bool = Field(description="Whether users can configure this integration")
    externalConfig: bool = Field(description="Whether integration uses external configuration")
    apiKey: bool = Field(description="Whether integration requires an API key")

    # Technical configuration
    endpoint: str | None = Field(None, description="API endpoint for the integration")
    authenticationKey: str | None = Field(None, description="Authentication key for integration")
    configJson: str = Field(default="{}", description="JSON configuration string")
    inputDebounceInMs: int | None = Field(None, description="Input debounce time in milliseconds")

    # Hosting information
    hostingProvider: str = Field(default="", description="Hosting provider name")
    hostingLocation: str = Field(default="", description="Hosting location/region")
    region: str = Field(default="", description="Deployment region")
    env: int = Field(description="Environment identifier")

    # Support and localization
    supportEmail: str = Field(default="", description="Support contact email")
    langTagPrefix: str = Field(default="", description="Language tag prefix for i18n")

    # Pricing
    price: int | None = Field(None, description="Integration price (one-time or base)")
    pricePerUser: int | None = Field(None, description="Per-user pricing amount")

    # Publisher information
    publisherClientId: int = Field(description="Publisher's client ID in Upsales")
    publisherName: NonEmptyStr = Field(description="Publisher/vendor name")

    # Terms and contracts
    termsAccepted: str | None = Field(None, description="Timestamp when terms were accepted")
    termsAcceptedUser: str | None = Field(None, description="User who accepted terms")
    contract: dict[str, Any] = Field(
        default_factory=dict, description="Contract details (structure varies)"
    )
    userContract: dict[str, Any] | None = Field(None, description="User-specific contract details")

    # Related configuration
    standardIntegrationInit: list[dict[str, Any]] = Field(
        default_factory=list, description="Initialization configuration list"
    )
    standardIntegrationTag: list[Any] = Field(
        default_factory=list, description="Tags associated with integration"
    )

    @computed_field
    @property
    def is_active(self) -> bool:
        """
        Check if integration is active.

        Returns:
            True if active flag is True, False otherwise.

        Example:
            >>> integration.is_active
            True
        """
        return self.active

    @computed_field
    @property
    def is_visible(self) -> bool:
        """
        Check if integration is visible in UI.

        Returns:
            True if visible flag is True, False otherwise.

        Example:
            >>> integration.is_visible
            True
        """
        return self.visible

    @computed_field
    @property
    def is_public(self) -> bool:
        """
        Check if integration is publicly available.

        Returns:
            True if public flag is True, False otherwise.

        Example:
            >>> integration.is_public
            True
        """
        return self.public

    @computed_field
    @property
    def requires_api_key(self) -> bool:
        """
        Check if integration requires an API key.

        Returns:
            True if apiKey flag is True, False otherwise.

        Example:
            >>> integration.requires_api_key
            False
        """
        return self.apiKey

    @computed_field
    @property
    def has_pricing(self) -> bool:
        """
        Check if integration has pricing information.

        Returns:
            True if either price or pricePerUser is set.

        Example:
            >>> integration.has_pricing
            True
        """
        return self.price is not None or self.pricePerUser is not None

    @computed_field
    @property
    def display_name(self) -> str:
        """
        Get display name for UI.

        Returns formatted name with version if available.

        Returns:
            Integration name with version.

        Example:
            >>> integration.display_name
            'Salesforce Integration v2.1'
        """
        return f"{self.name} v{self.version}" if self.version else self.name

    async def edit(
        self, **kwargs: Unpack[StandardIntegrationUpdateFields]
    ) -> "StandardIntegration":
        """
        Edit this standard integration.

        Uses Pydantic v2's optimized serialization via to_api_dict().
        With Python 3.13 free-threaded mode, multiple edits can run
        in true parallel without GIL contention.

        Args:
            **kwargs: Fields to update (from StandardIntegrationUpdateFields).

        Returns:
            Updated StandardIntegration object from API.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> integration = await upsales.standard_integrations.get(1)
            >>> updated = await integration.edit(
            ...     name="Updated Integration",
            ...     description="New description",
            ...     active=True
            ... )
            >>> updated.name
            'Updated Integration'
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.standard_integrations.update(
            self.id, **self.to_api_dict(**kwargs)
        )


class PartialStandardIntegration(PartialModel):
    """
    Partial StandardIntegration for nested responses.

    Contains minimal integration data when integration appears nested in other objects.
    Use fetch_full() to get complete integration data.

    Example:
        >>> # When integration is nested in another response
        >>> integration = some_object.standardIntegration
        >>> integration.name  # Partial data
        'Salesforce Integration'
        >>> full = await integration.fetch_full()  # Fetch complete data
        >>> full.description
        'Complete Salesforce integration'
    """

    id: int = Field(description="Unique standard integration ID")
    name: str = Field(description="Integration name")

    async def fetch_full(self) -> StandardIntegration:
        """
        Fetch full standard integration data from API.

        Returns:
            Complete StandardIntegration object with all fields.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> full_integration = await partial_integration.fetch_full()
            >>> full_integration.description
            'Complete integration details'
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.standard_integrations.get(self.id)

    async def edit(self, **kwargs: Unpack[StandardIntegrationUpdateFields]) -> StandardIntegration:
        """
        Edit this standard integration.

        Args:
            **kwargs: Fields to update (from StandardIntegrationUpdateFields).

        Returns:
            Updated StandardIntegration object from API.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> updated = await partial_integration.edit(
            ...     description="Updated from partial"
            ... )
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.standard_integrations.update(self.id, **kwargs)
