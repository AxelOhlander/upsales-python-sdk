"""
Self models for Upsales API.

The /api/v2/self endpoint returns current user information including account
details, client information, version data, features, and add-ons. Unlike typical
REST endpoints, this returns a single dict (not a list of items).

This is a read-only endpoint containing current user session information.
"""

from typing import TYPE_CHECKING, Any

from pydantic import BaseModel as PydanticBase
from pydantic import ConfigDict, Field, computed_field

if TYPE_CHECKING:
    from upsales.client import Upsales

from upsales.validators import NonEmptyStr, PositiveInt


class SelfClient(PydanticBase):
    """
    Client information from self endpoint (list item).

    Attributes:
        name: Client account name
        clientId: Client ID
        userId: User ID associated with client

    Example:
        >>> self_data = await upsales.self.get()
        >>> for client in self_data.clients:
        ...     print(f"{client.name}: {client.clientId}")
    """

    model_config = ConfigDict(
        frozen=False,
        validate_assignment=True,
        extra="allow",
        populate_by_name=True,
    )

    name: NonEmptyStr = Field(description="Client account name")
    clientId: PositiveInt = Field(description="Client ID")
    userId: PositiveInt = Field(description="User ID associated with client")


class ClientDetail(PydanticBase):
    """
    Detailed client information from self endpoint.

    Attributes:
        id: Client ID
        name: Client account name
        numberOfLicenses: Number of user licenses
        killDate: Account termination date (null if active)
        isTrial: Whether account is trial
        provisioningMaxContactTotal: Maximum contact limit
        userId: Primary user ID
        address: Client address
        zipCode: Client zip code
        state: Client state/province
        country: Country code (e.g., 'SE', 'US')
        www: Website URL
        contactEmail: Contact email address
        delayedPayment: Delayed payment settings
        orgNumber: Organization number
        migrated: Migration status (0 or 1)
        movingStarted: Migration start date

    Example:
        >>> self_data = await upsales.self.get()
        >>> print(f"Client: {self_data.client.name}")
        >>> print(f"Licenses: {self_data.client.numberOfLicenses}")
        >>> print(f"Country: {self_data.client.country}")
    """

    model_config = ConfigDict(
        frozen=False,
        validate_assignment=True,
        extra="allow",
        populate_by_name=True,
    )

    id: PositiveInt = Field(description="Client ID")
    name: NonEmptyStr = Field(description="Client account name")
    numberOfLicenses: int = Field(description="Number of user licenses")
    killDate: str | None = Field(None, description="Account termination date")
    isTrial: bool = Field(description="Whether account is trial")
    provisioningMaxContactTotal: int = Field(description="Maximum contact limit (0 = unlimited)")
    userId: PositiveInt = Field(description="Primary user ID")
    address: str | None = Field(None, description="Client address")
    zipCode: str | None = Field(None, description="Client zip code")
    state: str | None = Field(None, description="Client state/province")
    country: str | None = Field(None, description="Country code")
    www: str | None = Field(None, description="Website URL")
    contactEmail: str | None = Field(None, description="Contact email address")
    delayedPayment: Any | None = Field(None, description="Delayed payment settings")
    orgNumber: str = Field(description="Organization number")
    migrated: int = Field(description="Migration status (0 or 1)")
    movingStarted: str | None = Field(None, description="Migration start date")

    @computed_field
    @property
    def is_trial(self) -> bool:
        """
        Check if account is trial.

        Returns:
            True if trial account, False otherwise.

        Example:
            >>> self_data.client.is_trial
            False
        """
        return self.isTrial

    @computed_field
    @property
    def is_active(self) -> bool:
        """
        Check if account is active (not killed).

        Returns:
            True if account is active, False otherwise.

        Example:
            >>> self_data.client.is_active
            True
        """
        return self.killDate is None

    @computed_field
    @property
    def has_contact_limit(self) -> bool:
        """
        Check if account has contact limit.

        Returns:
            True if contact limit exists, False if unlimited.

        Example:
            >>> self_data.client.has_contact_limit
            False
        """
        return self.provisioningMaxContactTotal > 0


class VersionData(PydanticBase):
    """
    Version and feature information.

    Attributes:
        name: Version name (e.g., 'Enterprise', 'Professional', 'Accelerate')
        parent: Parent version tier
        products: Product access (crm, ma)
        unlimitedEmails: Whether emails are unlimited
        includedAddons: List of included addon identifiers
        canPurchaseAddons: List of purchasable addon identifiers
        features: List of enabled features
        whitelabel: Whether whitelabel is enabled
        trialAddons: List of trial addon identifiers
        availableAddons: List of available addon identifiers

    Example:
        >>> self_data = await upsales.self.get()
        >>> print(f"Version: {self_data.versionData.name}")
        >>> print(f"CRM: {self_data.versionData.has_crm}")
        >>> print(f"Features: {len(self_data.versionData.features)}")
    """

    model_config = ConfigDict(
        frozen=False,
        validate_assignment=True,
        extra="allow",
        populate_by_name=True,
    )

    name: NonEmptyStr = Field(description="Version name")
    parent: NonEmptyStr = Field(description="Parent version tier")
    products: dict[str, bool] = Field(description="Product access (crm, ma)")
    unlimitedEmails: bool = Field(description="Whether emails are unlimited")
    includedAddons: list[str] = Field(default=[], description="Included addon identifiers")
    canPurchaseAddons: list[str] = Field(default=[], description="Purchasable addon identifiers")
    features: list[str | None] = Field(default=[], description="Enabled features")
    whitelabel: bool = Field(description="Whether whitelabel is enabled")
    trialAddons: list[str] = Field(default=[], description="Trial addon identifiers")
    availableAddons: list[str] = Field(default=[], description="Available addon identifiers")

    @computed_field
    @property
    def has_crm(self) -> bool:
        """
        Check if CRM product is enabled.

        Returns:
            True if CRM is enabled, False otherwise.

        Example:
            >>> self_data.versionData.has_crm
            True
        """
        return self.products.get("crm", False)

    @computed_field
    @property
    def has_marketing_automation(self) -> bool:
        """
        Check if Marketing Automation product is enabled.

        Returns:
            True if MA is enabled, False otherwise.

        Example:
            >>> self_data.versionData.has_marketing_automation
            True
        """
        return self.products.get("ma", False)

    @computed_field
    @property
    def feature_count(self) -> int:
        """
        Get count of enabled features.

        Returns:
            Number of enabled features.

        Example:
            >>> self_data.versionData.feature_count
            150
        """
        return len([f for f in self.features if f is not None])

    @computed_field
    @property
    def addon_count(self) -> int:
        """
        Get count of included addons.

        Returns:
            Number of included addons.

        Example:
            >>> self_data.versionData.addon_count
            5
        """
        return len(self.includedAddons)


class AccountManager(PydanticBase):
    """
    Account manager contact information.

    Attributes:
        name: Account manager name
        title: Account manager job title
        email: Contact email address
        phone: Contact phone number
        cellPhone: Cell phone number

    Example:
        >>> self_data = await upsales.self.get()
        >>> am = self_data.accountManager
        >>> print(f"{am.name} ({am.title})")
        >>> print(f"Email: {am.email}")
    """

    model_config = ConfigDict(
        frozen=False,
        validate_assignment=True,
        extra="allow",
        populate_by_name=True,
    )

    name: NonEmptyStr = Field(description="Account manager name")
    title: NonEmptyStr = Field(description="Account manager job title")
    email: NonEmptyStr = Field(description="Contact email address")
    phone: str = Field(description="Contact phone number")
    cellPhone: str = Field(description="Cell phone number")

    @computed_field
    @property
    def has_cell_phone(self) -> bool:
        """
        Check if cell phone is provided.

        Returns:
            True if cell phone exists, False otherwise.

        Example:
            >>> self_data.accountManager.has_cell_phone
            False
        """
        return bool(self.cellPhone and self.cellPhone.strip())


class Self(PydanticBase):
    """
    Current user session information from /api/v2/self endpoint.

    This model represents the complete response containing current user info,
    client details, version data, features, and addons.

    Attributes:
        id: Current user ID
        email: User email address
        clients: List of accessible client accounts
        client: Detailed current client information
        name: User name
        lastOnline: Last online timestamp (legacy)
        lastOnlinePower: Last online timestamp (Power UI)
        language: User language code (e.g., 'en-US', 'sv-SE')
        versionData: Version and feature information
        version: Version name shorthand
        whitelabel: Whether whitelabel is enabled
        products: Product access dict
        features: Feature flags dict
        boughtAddons: Purchased addons dict
        availableAddons: Available addon list
        unreleasedFeatures: Unreleased feature flags dict
        userActivatedFeatures: User-activated feature dict
        accountManager: Account manager contact info

    Example:
        >>> async with Upsales.from_env() as upsales:
        ...     # Get current user info
        ...     self_data = await upsales.self.get()
        ...     print(f"User: {self_data.name}")
        ...     print(f"Email: {self_data.email}")
        ...     print(f"Version: {self_data.version}")
        ...     print(f"Has CRM: {self_data.has_crm}")
        ...     print(f"Has MA: {self_data.has_marketing_automation}")
    """

    model_config = ConfigDict(
        frozen=False,
        validate_assignment=True,
        extra="allow",
        populate_by_name=True,
    )

    # Client reference (injected by resource manager)
    _client: "Upsales | None" = None

    # User identification
    id: PositiveInt = Field(description="Current user ID")
    email: NonEmptyStr = Field(description="User email address")
    name: NonEmptyStr = Field(description="User name")

    # Client information
    clients: list[SelfClient] = Field(default=[], description="List of accessible client accounts")
    client: ClientDetail = Field(description="Detailed current client information")

    # Session information
    lastOnline: str | None = Field(None, description="Last online timestamp (legacy)")
    lastOnlinePower: str | None = Field(None, description="Last online timestamp (Power UI)")
    language: NonEmptyStr = Field(description="User language code")

    # Version and features
    versionData: VersionData = Field(description="Version and feature information")
    version: NonEmptyStr = Field(description="Version name shorthand")
    whitelabel: bool = Field(description="Whether whitelabel is enabled")
    products: dict[str, bool] = Field(description="Product access dict")
    features: dict[str, bool] = Field(description="Feature flags dict")
    boughtAddons: dict[str, bool] = Field(description="Purchased addons dict")
    availableAddons: list[str] = Field(default=[], description="Available addon identifiers")
    unreleasedFeatures: dict[str, bool] = Field(description="Unreleased feature flags dict")
    userActivatedFeatures: dict[str, Any] = Field(description="User-activated feature dict")

    # Account manager
    accountManager: AccountManager = Field(description="Account manager contact info")

    @computed_field
    @property
    def has_crm(self) -> bool:
        """
        Check if CRM product is enabled.

        Returns:
            True if CRM is enabled, False otherwise.

        Example:
            >>> self_data.has_crm
            True
        """
        return self.products.get("crm", False)

    @computed_field
    @property
    def has_marketing_automation(self) -> bool:
        """
        Check if Marketing Automation product is enabled.

        Returns:
            True if MA is enabled, False otherwise.

        Example:
            >>> self_data.has_marketing_automation
            True
        """
        return self.products.get("ma", False)

    @computed_field
    @property
    def client_count(self) -> int:
        """
        Get count of accessible client accounts.

        Returns:
            Number of accessible clients.

        Example:
            >>> self_data.client_count
            1
        """
        return len(self.clients)

    @computed_field
    @property
    def feature_count(self) -> int:
        """
        Get count of enabled features.

        Returns:
            Number of enabled features.

        Example:
            >>> self_data.feature_count
            150
        """
        return sum(1 for enabled in self.features.values() if enabled)

    @computed_field
    @property
    def addon_count(self) -> int:
        """
        Get count of purchased addons.

        Returns:
            Number of purchased addons.

        Example:
            >>> self_data.addon_count
            7
        """
        return sum(1 for enabled in self.boughtAddons.values() if enabled)

    def has_feature(self, feature_name: str) -> bool:
        """
        Check if a specific feature is enabled.

        Args:
            feature_name: Feature identifier to check.

        Returns:
            True if feature is enabled, False otherwise.

        Example:
            >>> self_data.has_feature('triggers')
            True
            >>> self_data.has_feature('nonexistent')
            False
        """
        return self.features.get(feature_name, False)

    def has_addon(self, addon_name: str) -> bool:
        """
        Check if a specific addon is purchased.

        Args:
            addon_name: Addon identifier to check.

        Returns:
            True if addon is purchased, False otherwise.

        Example:
            >>> self_data.has_addon('API_KEYS')
            True
            >>> self_data.has_addon('LOOKER')
            True
        """
        return self.boughtAddons.get(addon_name, False)

    def has_unreleased_feature(self, feature_name: str) -> bool:
        """
        Check if an unreleased feature is enabled.

        Args:
            feature_name: Unreleased feature identifier to check.

        Returns:
            True if unreleased feature is enabled, False otherwise.

        Example:
            >>> self_data.has_unreleased_feature('NEW_FIELDS')
            True
        """
        return self.unreleasedFeatures.get(feature_name, False)
