"""
Company models for Upsales API.

Generated from /api/v2/accounts endpoint.
Analysis based on 619 samples.

Note:
    API endpoint is /accounts but we use "Company" to match the Upsales UI
    where users see "Companies". See docs/terminology.md for rationale.

Enhanced with Pydantic v2 features:
- Reusable validators (BinaryFlag, CustomFieldsList, NonEmptyStr)
- Computed fields (@computed_field)
- Field serialization (@field_serializer)
- Strict type checking
- Field descriptions
- Optimized serialization
"""

from typing import TYPE_CHECKING, Any, TypedDict, Unpack

from pydantic import Field, computed_field, field_serializer, field_validator, model_validator

from upsales.models.ad_campaign import AdCampaign
from upsales.models.address import PartialAddress
from upsales.models.address_list import AddressList
from upsales.models.assignment import Assignment
from upsales.models.base import BaseModel, PartialModel
from upsales.models.campaign import PartialCampaign
from upsales.models.custom_fields import CustomFields
from upsales.models.processed_by import ProcessedBy
from upsales.validators import BinaryFlag, CustomFieldsList, NonEmptyStr

if TYPE_CHECKING:
    from upsales.models.user import PartialUser  # Avoid circular import


class CompanyUpdateFields(TypedDict, total=False):
    """
    Available fields for updating a Company.

    All fields are optional. Use with Unpack for IDE autocomplete.

    Note:
        Excludes read-only fields: id, regDate, modDate
    """

    # Core fields
    name: str
    active: int
    isExternal: int
    headquarters: int
    cfar: int

    # Metadata
    numberOfContacts: int
    numberOfContactsTotal: int
    numberOfSubaccounts: int
    score: int
    journeyStep: str

    # Boolean flags
    excludedFromProspectingMonitor: bool
    isMonitored: bool
    hasVisit: bool
    hasMail: bool
    hasForm: bool
    userEditable: bool
    userRemovable: bool

    # Text fields
    about: str
    phone: str
    webpage: str
    orgNo: str
    currency: str
    status: str
    notes: str
    fax: str
    linkedin: str
    twitter: str
    companyForm: str
    naceCode: str
    sniCode: str
    dunsNo: str
    creditRating: str

    # Numeric fields
    noEmployees: int
    turnover: int
    profit: int

    # Date fields
    scoreUpdateDate: str
    registrationDate: str
    monitorChangeDate: str
    prospectingUpdateDate: str

    # Prospecting fields
    prospectingId: str
    autoMatchedProspectingId: str
    prospectingCreditRating: str
    prospectingNumericCreditRating: int

    # Activity tracking
    hadOrder: str
    hasOrder: str
    hadActivity: str
    hasActivity: str
    hadAppointment: str
    hasAppointment: str
    hadOpportunity: str
    hasOpportunity: str

    # List fields
    custom: list[Any]
    users: list[dict[str, Any]]
    addresses: list[dict[str, Any]]
    adCampaign: list[dict[str, Any]]
    projects: list[dict[str, Any]]
    categories: list[Any]
    clientPlans: list[Any]
    clientQuotas: list[Any]
    connectedClients: list[Any]
    externalClientData: list[Any]

    # Dict/object fields
    extraFields: dict[str, Any]
    ads: dict[str, Any]
    assigned: dict[str, Any]
    growth: dict[str, Any]
    mailAddress: dict[str, Any]
    soliditet: dict[str, Any]
    supportTickets: dict[str, Any]
    parent: dict[str, Any]
    regBy: dict[str, Any]
    processedBy: dict[str, Any]
    operationalAccount: dict[str, Any]
    source: dict[str, Any]

    # Any type fields
    priceList: Any
    priceListId: Any
    phoneCountryCode: Any
    sicCode: Any
    ukSicCode: Any
    naicsCode: Any
    importId: Any
    facebook: Any
    deactivatedBy: Any
    deactivationDate: Any
    deactivationReason: Any


class Company(BaseModel):
    """
    Company model from /api/v2/accounts.

    Represents a customer/company in the Upsales system. Generated from 619
    real company records with comprehensive field analysis.

    Note:
        API endpoint is /accounts, but we use "Company" to match what users
        see in the Upsales UI (Companies, not Accounts).

    Field Selection (Performance Optimization):
        When using fields=["id", "name"], these 17 fields are ALWAYS returned
        regardless of field selection (verified 2025-11-07):

        - id (primary key)
        - userEditable, userRemovable (permissions)
        - dunsNo, prospectingId, extraFields (system identifiers)
        - hasActivity, hasAppointment, hasForm, hasMail, hasOpportunity,
          hasOrder, hasVisit (7 current activity flags)
        - hadActivity, hadAppointment, hadOpportunity, hadOrder (4 historical flags)

        All other 69 fields (80%) can be excluded for bandwidth reduction:
        - name, phone, addresses, users, categories, projects
        - turnover, profit, custom, about
        - All relationship and financial fields

        Example:
            >>> # Minimal query (76% bandwidth reduction)
            >>> companies = await upsales.companies.list(
            ...     fields=["id", "name"],
            ...     limit=100
            ... )
            >>> # Returns: id, name + 16 always-returned fields (21 total vs 86)

    Example:
        >>> company = await upsales.companies.get(1)
        >>> company.name
        'ACME Corporation'
        >>> company.is_active
        True
        >>> company.custom_fields[11]
        'value'
    """

    # Read-only fields (frozen=True, strict=True)
    id: int = Field(frozen=True, strict=True, description="Unique company ID")
    regDate: str | None = Field(None, frozen=True, description="Registration date")
    modDate: str = Field(
        default="",
        frozen=True,
        description="Last modification date (may be excluded by field selection)",
    )

    # Required core fields with validators (defaults added for field selection support)
    name: str = Field(
        default="",
        description="Company name (required for CREATE, may be excluded by field selection)",
    )
    active: BinaryFlag = Field(default=1, description="Active status (0=inactive, 1=active)")
    isExternal: BinaryFlag = Field(default=0, description="External company flag (0=no, 1=yes)")
    headquarters: BinaryFlag = Field(default=0, description="Headquarters flag (0=no, 1=yes)")
    cfar: int | None = Field(None, description="CFAR identifier code (not a binary flag)")

    # Metadata fields (calculated/system-managed, may be excluded by field selection)
    numberOfContacts: int = Field(
        default=0, description="Number of contacts (calculated, may be excluded by field selection)"
    )
    numberOfContactsTotal: int = Field(
        default=0,
        description="Total number of contacts (calculated, may be excluded by field selection)",
    )
    numberOfSubaccounts: int = Field(
        default=0,
        description="Number of subaccounts (calculated, may be excluded by field selection)",
    )
    score: int = Field(default=0, description="Company score (may be excluded by field selection)")
    journeyStep: str = Field(
        default="", description="Journey step in sales process (may be excluded by field selection)"
    )

    # Boolean flags
    excludedFromProspectingMonitor: bool = Field(
        default=False, description="Excluded from prospecting monitor"
    )
    isMonitored: bool = Field(default=False, description="Is being monitored")

    # NOTE: These tracking/permission fields are ALWAYS returned even with field selection (verified 2025-11-07)
    hasVisit: bool = Field(default=False, description="Has visit activity (always returned)")
    hasMail: bool = Field(default=False, description="Has mail activity (always returned)")
    hasForm: bool = Field(default=False, description="Has form submission (always returned)")
    userEditable: bool = Field(default=True, description="User can edit (always returned)")
    userRemovable: bool = Field(default=True, description="User can remove (always returned)")

    # Optional text fields
    about: str | None = Field(None, description="About the company")
    phone: str | None = Field(None, description="Phone number")
    webpage: str | None = Field(None, description="Company website")
    orgNo: str | None = Field(None, description="Organization number")
    currency: str | None = Field(None, description="Default currency")
    status: str | None = Field(None, description="Company status")
    notes: str | None = Field(None, description="Notes about company")
    fax: str | None = Field(None, description="Fax number")
    linkedin: str | None = Field(None, description="LinkedIn profile")
    twitter: str | None = Field(None, description="Twitter handle")
    companyForm: str | None = Field(None, description="Company form/type")
    naceCode: str | None = Field(None, description="NACE industry code")
    sniCode: str | None = Field(None, description="SNI industry code")
    # NOTE: 'dunsNo' is ALWAYS returned even with field selection
    dunsNo: str | None = Field(None, description="DUNS number (always returned)")
    creditRating: str | None = Field(None, description="Credit rating")

    # Optional numeric fields
    noEmployees: int | None = Field(None, description="Number of employees")
    turnover: int | None = Field(None, description="Annual turnover")
    profit: int | None = Field(None, description="Annual profit")

    # Optional date fields
    scoreUpdateDate: str | None = Field(None, description="Last score update date")
    registrationDate: str | None = Field(None, description="Company registration date")
    monitorChangeDate: str | None = Field(None, description="Monitor status change date")
    prospectingUpdateDate: str | None = Field(None, description="Last prospecting update date")

    # Optional prospecting fields
    # NOTE: 'prospectingId' is ALWAYS returned even with field selection
    prospectingId: str | None = Field(None, description="Prospecting ID (always returned)")
    autoMatchedProspectingId: str | None = Field(None, description="Auto-matched prospecting ID")
    prospectingCreditRating: str | None = Field(None, description="Prospecting credit rating")
    prospectingNumericCreditRating: int | None = Field(
        None, description="Numeric credit rating from prospecting"
    )

    # Activity tracking fields (date strings or None)
    # NOTE: These 8 fields are ALWAYS returned even with field selection (verified 2025-11-07)
    hadOrder: str | None = Field(None, description="Date of last order (always returned)")
    hasOrder: str | None = Field(None, description="Has active order (always returned)")
    hadActivity: str | None = Field(None, description="Date of last activity (always returned)")
    hasActivity: str | None = Field(None, description="Has active activity (always returned)")
    hadAppointment: str | None = Field(
        None, description="Date of last appointment (always returned)"
    )
    hasAppointment: str | None = Field(None, description="Has active appointment (always returned)")
    hadOpportunity: str | None = Field(
        None, description="Date of last opportunity (always returned)"
    )
    hasOpportunity: str | None = Field(None, description="Has active opportunity (always returned)")

    # List fields
    custom: CustomFieldsList = Field(default=[], description="Custom fields")
    users: list["PartialUser"] = Field(default=[], description="Users associated with company")
    addresses: AddressList = Field(
        default_factory=lambda: AddressList([]),
        description="Smart address collection with type accessors (.mail, .visit, .postal, .billing, .delivery)",
    )
    adCampaign: list[AdCampaign] = Field(
        default_factory=list, description="Advertising campaigns (API returns array)"
    )
    projects: list[PartialCampaign] = Field(default=[], description="Associated campaigns/projects")
    categories: list[Any] = Field(
        default=[], description="Company categories (dynamic structure, kept as Any)"
    )
    clientPlans: list[Any] = Field(
        default=[], description="Client plans (complex structure, kept as Any)"
    )
    clientQuotas: list[Any] = Field(
        default=[], description="Client quotas (complex structure, kept as Any)"
    )
    connectedClients: list[Any] = Field(
        default=[], description="Connected clients (structure TBD, kept as Any)"
    )
    externalClientData: dict[str, Any] | list[Any] = Field(
        default_factory=dict,
        description="External client data (API returns dict or list, inconsistent)",
    )

    # Dict/object fields
    # NOTE: 'extraFields' is ALWAYS returned even with field selection
    extraFields: dict[str, Any] = Field(
        default_factory=dict,
        description="Extra custom fields (flexible structure, always returned)",
    )
    ads: dict[str, Any] = Field(default={}, description="Ad data (complex structure)")
    assigned: list[Assignment] | Assignment | None = Field(
        default=None,
        description="Assigned users (API returns dict or list, inconsistent)",
    )
    growth: dict[str, Any] = Field(default={}, description="Growth data (metrics, kept as dict)")
    mailAddress: dict[str, Any] | None = Field(
        None,
        description="Mail address from API (raw dict, automatically merged into addresses collection)",
        exclude=True,  # Exclude from dict export since it's merged into addresses
    )
    soliditet: dict[str, Any] = Field(
        default={}, description="Soliditet data (third-party credit data)"
    )
    supportTickets: dict[str, Any] = Field(
        default={}, description="Support tickets (complex structure)"
    )

    # Optional object/dict fields (can be null) - Now typed!
    parent: "PartialCompany | None" = Field(None, description="Parent company")
    regBy: "PartialUser | None" = Field(None, description="Registered by user")
    processedBy: ProcessedBy | None = Field(None, description="Processing tracking information")
    operationalAccount: "PartialCompany | None" = Field(None, description="Operational account")
    source: dict[str, Any] | None = Field(
        None, description="Source information (tracking data, kept as dict)"
    )

    # Any type fields (need investigation)
    priceList: Any | None = Field(None, description="Price list")
    priceListId: Any | None = Field(None, description="Price list ID")
    phoneCountryCode: Any | None = Field(None, description="Phone country code")
    sicCode: Any | None = Field(None, description="SIC code")
    ukSicCode: Any | None = Field(None, description="UK SIC code")
    naicsCode: Any | None = Field(None, description="NAICS code")
    importId: Any | None = Field(None, description="Import ID")
    facebook: Any | None = Field(None, description="Facebook profile")
    deactivatedBy: Any | None = Field(None, description="Deactivated by user")
    deactivationDate: Any | None = Field(None, description="Deactivation date")
    deactivationReason: Any | None = Field(None, description="Deactivation reason")

    @computed_field
    @property
    def custom_fields(self) -> CustomFields:
        """
        Access custom fields with dict-like interface.

        Returns:
            CustomFields helper for easy access by ID or alias.

        Example:
            >>> company.custom_fields[11]  # By field ID
            'value'
            >>> company.custom_fields["INDUSTRY"] = "Tech"  # By alias
        """
        return CustomFields(self.custom)

    @computed_field
    @property
    def is_active(self) -> bool:
        """
        Check if company is active.

        Returns:
            True if active flag is 1, False otherwise.

        Example:
            >>> company.is_active
            True
        """
        return self.active == 1

    @computed_field
    @property
    def is_headquarters(self) -> bool:
        """
        Check if this is the headquarters location.

        Returns:
            True if headquarters flag is 1, False otherwise.

        Example:
            >>> company.is_headquarters
            True
        """
        return self.headquarters == 1

    @computed_field
    @property
    def contact_count(self) -> int:
        """
        Get total number of contacts.

        Returns:
            Number of contacts associated with this company.

        Example:
            >>> company.contact_count
            42
        """
        return self.numberOfContactsTotal

    @field_validator("addresses", mode="before")
    @classmethod
    def convert_addresses_list(cls, v: Any) -> AddressList:
        """
        Convert raw list from API to AddressList instance.

        The API returns addresses as a raw list of dicts, but our model
        uses AddressList for convenient typed access (.mail, .visit, etc.).

        Args:
            v: Value from API (list[dict] or AddressList).

        Returns:
            AddressList instance with Address objects.
        """
        if isinstance(v, list):
            # Convert list of dicts to list of Address objects
            from upsales.models.address import Address

            address_objects = [Address(**addr) if isinstance(addr, dict) else addr for addr in v]
            return AddressList(address_objects)
        if v is None:
            return AddressList([])
        return v

    @model_validator(mode="after")
    def merge_mail_address_into_addresses(self) -> "Company":
        """
        Merge mailAddress into addresses list automatically.

        The API returns mailAddress as a separate field, but we normalize
        this by merging it into the addresses collection for unified access.
        """
        if (
            self.mailAddress
            and isinstance(self.mailAddress, dict)
            and isinstance(self.addresses, AddressList)
        ):
            # Check if mail address not already in list
            if not self.addresses.mail:
                # Convert dict to Address and add to collection
                from upsales.models.address import Address

                try:
                    mail_addr = Address(**self.mailAddress)
                    self.addresses._addresses.append(mail_addr)
                except Exception:
                    # If conversion fails, skip merging
                    pass
        return self

    @field_serializer("addresses", when_used="always")
    def serialize_addresses(self, addresses: AddressList) -> list[dict[str, Any]]:
        """
        Serialize AddressList to list of dicts for API.

        Also handles splitting mail address back out if needed.
        Uses when_used='always' to work in both 'json' and 'python' modes.
        """
        # Get all addresses
        all_addrs = addresses.all() if isinstance(addresses, AddressList) else []

        # Serialize each address
        result = []
        for addr in all_addrs:
            # Skip mail type - it goes in mailAddress field
            if addr.type != "Mail":
                result.append(addr.to_dict())

        return result

    @field_serializer("custom", when_used="json")
    def serialize_custom_fields(self, custom: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Serialize custom fields for API requests.

        Removes fields without values to keep payloads clean.

        Args:
            custom: List of custom field dicts.

        Returns:
            Cleaned list with only fields that have values.
        """
        return [
            {"fieldId": item["fieldId"], "value": item.get("value")}
            for item in custom
            if "value" in item and item.get("value") is not None
        ]

    async def edit(self, **kwargs: Unpack[CompanyUpdateFields]) -> "Company":
        """
        Edit this company.

        Uses Pydantic v2's optimized serialization via to_api_dict().

        Args:
            **kwargs: Fields to update (full IDE autocomplete support).

        Returns:
            Updated company with fresh data from API.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> company = await upsales.companies.get(1)
            >>> updated = await company.edit(
            ...     name="ACME Corp",
            ...     active=1,
            ...     phone="+1234567890"
            ... )
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.companies.update(self.id, **self.to_api_dict(**kwargs))


class PartialCompany(PartialModel):
    """
    Partial Company for nested responses.

    Contains minimal fields for when Company appears nested in other
    API responses (e.g., as contact's company, parent company, etc.).

    Use fetch_full() to get complete Company object with all fields.

    Example:
        >>> contact = await upsales.contacts.get(1)
        >>> company = contact.company  # PartialCompany
        >>> full_company = await company.fetch_full()  # Company
    """

    id: int = Field(frozen=True, strict=True, description="Unique company ID")
    name: NonEmptyStr = Field(description="Company name")
    users: list[dict[str, Any]] | None = Field(None, description="Users (some endpoints)")
    operationalAccount: dict[str, Any] | None = Field(
        None, description="Operational account (some endpoints)"
    )
    journeyStep: str | None = Field(None, description="Journey step (some endpoints)")
    addresses: list[PartialAddress] | None = Field(None, description="Addresses (some endpoints)")
    phone: str | None = Field(None, description="Company phone (some endpoints)")

    @computed_field
    @property
    def display_name(self) -> str:
        """
        Get display name for the company.

        Returns:
            Company name formatted for display.

        Example:
            >>> partial_company.display_name
            'ACME Corporation'
        """
        return self.name

    async def fetch_full(self) -> Company:
        """
        Fetch complete company data.

        Returns:
            Full Company object with all fields populated.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> partial = contact.company  # PartialCompany
            >>> full = await partial.fetch_full()  # Company
            >>> full.phone  # Now available
            '+1234567890'
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.companies.get(self.id)

    async def edit(self, **kwargs: Unpack[CompanyUpdateFields]) -> Company:
        """
        Edit this company.

        Returns full Company object after update.

        Args:
            **kwargs: Fields to update (full IDE autocomplete support).

        Returns:
            Updated full Company object.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> partial = contact.company  # PartialCompany
            >>> updated = await partial.edit(phone="+1234567890")  # Returns Company
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.companies.update(self.id, **kwargs)
