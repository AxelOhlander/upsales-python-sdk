"""
Metadata models for Upsales API.

The /api/v2/metadata endpoint returns system configuration, user info,
currency settings, and field definitions. Unlike typical REST endpoints,
this returns a single dict (not a list of items).

This is a read-only endpoint containing system information.
"""

from typing import TYPE_CHECKING, Any

from pydantic import BaseModel as PydanticBase
from pydantic import ConfigDict, Field, computed_field

if TYPE_CHECKING:
    from upsales.client import Upsales

from upsales.models.roles import PartialRole
from upsales.validators import NonEmptyStr, PositiveInt


class Currency(PydanticBase):
    """
    Currency configuration from metadata.

    Attributes:
        iso: ISO 4217 currency code (e.g., 'USD', 'EUR', 'SEK')
        rate: Exchange rate relative to master currency
        active: Whether currency is enabled
        masterCurrency: Whether this is the master currency (rate = 1)

    Example:
        >>> metadata = await upsales.metadata.get()
        >>> sek = metadata.default_currency
        >>> sek.iso
        'SEK'
        >>> sek.is_master
        True
    """

    model_config = ConfigDict(
        frozen=False,
        validate_assignment=True,
        extra="allow",
        populate_by_name=True,
    )

    iso: NonEmptyStr = Field(description="ISO 4217 currency code")
    rate: float = Field(description="Exchange rate relative to master currency")
    active: bool = Field(description="Whether currency is enabled")
    masterCurrency: bool = Field(description="Whether this is the master currency")

    @computed_field
    @property
    def is_master(self) -> bool:
        """
        Check if this is the master currency.

        Returns:
            True if master currency, False otherwise.

        Example:
            >>> currency.is_master
            True
        """
        return self.masterCurrency

    @computed_field
    @property
    def is_active(self) -> bool:
        """
        Check if currency is active.

        Returns:
            True if active, False otherwise.

        Example:
            >>> currency.is_active
            True
        """
        return self.active


class MetadataUser(PydanticBase):
    """
    Current user information from metadata.

    Attributes:
        id: User ID
        name: User name
        administrator: Whether user is administrator (0 or 1)
        roleId: User role ID (0 if no role)
        teamLeader: Whether user is team leader
        active: Whether user is active (0 or 1)
        ghost: Whether user is a ghost user
        free: Whether user is a free user
        userTitle: User job title
        userAddress: User address
        userZipCode: User zip code
        userState: User state/province
        userPhone: User phone number
        userCellPhone: User mobile phone
        export: Whether user has export permissions
        billingAdmin: Whether user is billing administrator
        regDate: Registration date (ISO 8601)
        crm: Whether user has CRM access
        support: Whether user has support access
        service: Whether user has service access
        supportAdmin: Whether user is support administrator
        projectAdmin: Whether user is project administrator
        custom: Custom field values

    Example:
        >>> metadata = await upsales.metadata.get()
        >>> user = metadata.user
        >>> user.name
        'John Doe'
        >>> user.is_admin
        True
    """

    model_config = ConfigDict(
        frozen=False,
        validate_assignment=True,
        extra="allow",
        populate_by_name=True,
    )

    id: PositiveInt = Field(description="User ID")
    name: NonEmptyStr = Field(description="User name")
    administrator: bool = Field(description="Whether user is administrator")
    roleId: int = Field(description="User role ID (0 if no role)")
    teamLeader: bool = Field(description="Whether user is team leader")
    active: bool = Field(description="Whether user is active")
    ghost: bool = Field(description="Whether user is a ghost user")
    free: bool = Field(description="Whether user is a free user")
    userTitle: str | None = Field(None, description="User job title")
    userAddress: str | None = Field(None, description="User address")
    userZipCode: str | None = Field(None, description="User zip code")
    userState: str | None = Field(None, description="User state/province")
    userPhone: str | None = Field(None, description="User phone number")
    userCellPhone: str | None = Field(None, description="User mobile phone")
    export: bool = Field(description="Whether user has export permissions")
    billingAdmin: bool = Field(description="Whether user is billing administrator")
    regDate: str = Field(description="Registration date (ISO 8601)")
    crm: bool = Field(description="Whether user has CRM access")
    support: bool = Field(description="Whether user has support access")
    service: bool = Field(description="Whether user has service access")
    supportAdmin: bool = Field(description="Whether user is support administrator")
    projectAdmin: bool = Field(description="Whether user is project administrator")
    custom: list[dict[str, Any]] = Field(default_factory=list, description="Custom field values")

    @computed_field
    @property
    def is_admin(self) -> bool:
        """
        Check if user is administrator.

        Returns:
            True if administrator, False otherwise.

        Example:
            >>> user.is_admin
            True
        """
        return self.administrator

    @computed_field
    @property
    def is_active(self) -> bool:
        """
        Check if user is active.

        Returns:
            True if active, False otherwise.

        Example:
            >>> user.is_active
            True
        """
        return self.active

    @computed_field
    @property
    def is_team_leader(self) -> bool:
        """
        Check if user is team leader.

        Returns:
            True if team leader, False otherwise.

        Example:
            >>> user.is_team_leader
            False
        """
        return self.teamLeader

    @computed_field
    @property
    def has_crm_access(self) -> bool:
        """
        Check if user has CRM access.

        Returns:
            True if has CRM access, False otherwise.

        Example:
            >>> user.has_crm_access
            True
        """
        return self.crm


class SystemParams(PydanticBase):
    """
    System parameters and configuration.

    Contains various system-level settings and feature flags.
    Field names preserved from API for direct access.

    Example:
        >>> metadata = await upsales.metadata.get()
        >>> params = metadata.params
        >>> params.MultiCurrency
        True
        >>> params.sessionTime
        600
    """

    model_config = ConfigDict(
        frozen=False,
        validate_assignment=True,
        extra="allow",  # Allow all system params even if not explicitly defined
        populate_by_name=True,
    )

    # Common system parameters (non-exhaustive)
    teamAccountManager: bool = Field(False, description="Team account manager feature")
    defaultStageId: int | None = Field(None, description="Default order stage ID")
    MultiCurrency: bool = Field(False, description="Multi-currency support enabled")
    sessionTime: int = Field(600, description="Session timeout in seconds")
    UseDiscount: bool = Field(True, description="Whether discounts are enabled")
    SmsAuthentication: bool = Field(False, description="SMS authentication enabled")
    HasSamlLogin: bool = Field(False, description="SAML login enabled")
    UseContributionMargin: bool = Field(True, description="Whether contribution margin is used")
    HideReportCenter: bool = Field(False, description="Whether report center is hidden")


class FieldDefinition(PydanticBase):
    """
    Standard field definition from metadata.

    Describes a standard field's properties and configuration.

    Attributes:
        id: Field ID
        field: Field name in API
        name: Display name
        type: Field type (String, Number, Date, etc.)
        required: Whether field is required
        disabled: Whether field is disabled
        editable: Whether field is editable
        active: Whether field is active
        canHide: Whether field can be hidden
        canMakeRequired: Whether field can be made required
        sortOrder: Display order
        group: Field group name
        size: Maximum field size
        selectOptions: Select options (if applicable)
        tooltip: Field tooltip

    Example:
        >>> metadata = await upsales.metadata.get()
        >>> name_field = metadata.standard_fields['Client']['Name']
        >>> name_field.type
        'String'
        >>> name_field.required
        False
    """

    model_config = ConfigDict(
        frozen=False,
        validate_assignment=True,
        extra="allow",
        populate_by_name=True,
    )

    id: int = Field(description="Field ID")
    field: str | None = Field(None, description="Field name in API")
    name: NonEmptyStr = Field(description="Display name")
    type: NonEmptyStr = Field(description="Field type (String, Number, Date, etc.)")
    required: bool = Field(description="Whether field is required")
    disabled: bool = Field(description="Whether field is disabled")
    editable: bool = Field(description="Whether field is editable")
    active: bool = Field(description="Whether field is active")
    canHide: bool = Field(description="Whether field can be hidden")
    canMakeRequired: bool = Field(description="Whether field can be made required")
    sortOrder: int = Field(description="Display order")
    group: NonEmptyStr = Field(description="Field group name")
    size: int | None = Field(None, description="Maximum field size")
    selectOptions: str | list[str] = Field(
        default_factory=list, description="Select options (if applicable)"
    )
    tooltip: str | None = Field(None, description="Field tooltip")

    @computed_field
    @property
    def is_required(self) -> bool:
        """
        Check if field is required.

        Returns:
            True if required, False otherwise.

        Example:
            >>> field.is_required
            False
        """
        return self.required

    @computed_field
    @property
    def is_active(self) -> bool:
        """
        Check if field is active.

        Returns:
            True if active, False otherwise.

        Example:
            >>> field.is_active
            True
        """
        return self.active


class Metadata(PydanticBase):
    """
    System metadata from /api/v2/metadata.

    Contains system configuration, user information, currency settings,
    and field definitions. This is a read-only endpoint.

    Attributes:
        customerCurrencies: List of available currencies
        defaultCurrency: Default system currency
        params: System parameters and configuration
        user: Current user information
        role: User role information (nullable)
        version: Upsales version (e.g., 'Enterprise')
        licenses: Number of licenses
        supportLicenses: Number of support licenses
        soliditetCredits: Soliditet credits available
        metaChannel: Pusher meta channel name
        notificationChannel: Pusher notification channel name
        notificationUserChannel: Pusher user notification channel name
        publicChannel: Pusher public channel name
        iOSInterest: iOS interest channel name
        requiredFields: Required field configuration by entity type
        standardFields: Standard field definitions by entity type

    Example:
        >>> metadata = await upsales.metadata.get()
        >>> metadata.version
        'Enterprise'
        >>> metadata.licenses
        10
        >>> len(metadata.customerCurrencies)
        6
        >>> metadata.default_currency.iso
        'SEK'
    """

    model_config = ConfigDict(
        frozen=False,
        validate_assignment=True,
        arbitrary_types_allowed=True,
        extra="allow",
        populate_by_name=True,
    )

    customerCurrencies: list[Currency] = Field(
        default_factory=list, description="List of available currencies"
    )
    defaultCurrency: Currency = Field(description="Default system currency")
    params: dict[str, Any] = Field(
        default_factory=dict,
        description="System parameters and configuration",
    )
    user: MetadataUser = Field(description="Current user information")
    role: PartialRole | None = Field(None, description="User role information")
    version: NonEmptyStr = Field(description="Upsales version (e.g., 'Enterprise')")
    licenses: PositiveInt = Field(description="Number of licenses")
    supportLicenses: int = Field(0, description="Number of support licenses")
    soliditetCredits: int = Field(0, description="Soliditet credits available")
    metaChannel: NonEmptyStr = Field(description="Pusher meta channel name")
    notificationChannel: NonEmptyStr = Field(description="Pusher notification channel name")
    notificationUserChannel: NonEmptyStr = Field(
        description="Pusher user notification channel name"
    )
    publicChannel: NonEmptyStr = Field(description="Pusher public channel name")
    iOSInterest: NonEmptyStr = Field(description="iOS interest channel name")
    requiredFields: dict[str, dict[str, bool]] = Field(
        default_factory=dict, description="Required field configuration by entity type"
    )
    standardFields: dict[str, dict[str, FieldDefinition]] = Field(
        default_factory=dict, description="Standard field definitions by entity type"
    )

    _client: "Upsales | None" = None

    def __init__(self, **data: Any) -> None:
        """
        Initialize metadata with optional client reference.

        Args:
            **data: Metadata field data from API.
        """
        client = data.pop("_client", None)
        super().__init__(**data)
        object.__setattr__(self, "_client", client)

    @computed_field
    @property
    def currency_count(self) -> int:
        """
        Get number of available currencies.

        Returns:
            Number of currencies.

        Example:
            >>> metadata.currency_count
            6
        """
        return len(self.customerCurrencies)

    @computed_field
    @property
    def master_currency(self) -> Currency | None:
        """
        Get the master currency.

        Returns:
            Master currency, or None if not found.

        Example:
            >>> metadata.master_currency.iso
            'SEK'
        """
        return next((c for c in self.customerCurrencies if c.is_master), None)

    @computed_field
    @property
    def active_currencies(self) -> list[Currency]:
        """
        Get list of active currencies.

        Returns:
            List of active currencies.

        Example:
            >>> len(metadata.active_currencies)
            6
        """
        return [c for c in self.customerCurrencies if c.is_active]

    @computed_field
    @property
    def has_multi_currency(self) -> bool:
        """
        Check if multi-currency support is enabled.

        Returns:
            True if multi-currency enabled, False otherwise.

        Example:
            >>> metadata.has_multi_currency
            True
        """
        return bool(self.params.get("MultiCurrency", False))

    @computed_field
    @property
    def is_enterprise(self) -> bool:
        """
        Check if this is an Enterprise version.

        Returns:
            True if Enterprise, False otherwise.

        Example:
            >>> metadata.is_enterprise
            True
        """
        return self.version == "Enterprise"

    def get_entity_fields(self, entity_type: str) -> dict[str, FieldDefinition]:
        """
        Get field definitions for an entity type.

        Args:
            entity_type: Entity type (e.g., 'Client', 'Contact', 'Order')

        Returns:
            Dictionary of field name to field definition.

        Raises:
            KeyError: If entity type not found.

        Example:
            >>> client_fields = metadata.get_entity_fields('Client')
            >>> client_fields['Name'].type
            'String'
        """
        return self.standardFields[entity_type]

    def get_required_fields(self, entity_type: str) -> dict[str, bool]:
        """
        Get required field configuration for an entity type.

        Args:
            entity_type: Entity type (e.g., 'Client', 'Contact', 'Order')

        Returns:
            Dictionary of field name to required status.

        Raises:
            KeyError: If entity type not found.

        Example:
            >>> required = metadata.get_required_fields('Client')
            >>> required['Name']
            False
        """
        return self.requiredFields[entity_type]

    def is_field_required(self, entity_type: str, field_name: str) -> bool:
        """
        Check if a field is required for an entity type.

        Args:
            entity_type: Entity type (e.g., 'Client', 'Contact', 'Order')
            field_name: Field name (e.g., 'Name', 'Email')

        Returns:
            True if field is required, False otherwise.

        Example:
            >>> metadata.is_field_required('Client', 'Name')
            False
            >>> metadata.is_field_required('Contact', 'Email')
            False
        """
        return self.requiredFields.get(entity_type, {}).get(field_name, False)

    def get_currency_by_iso(self, iso_code: str) -> Currency | None:
        """
        Get currency by ISO code.

        Args:
            iso_code: ISO 4217 currency code (e.g., 'USD', 'EUR')

        Returns:
            Currency if found, None otherwise.

        Example:
            >>> usd = metadata.get_currency_by_iso('USD')
            >>> usd.rate
            0.106791513
        """
        return next((c for c in self.customerCurrencies if c.iso == iso_code), None)
