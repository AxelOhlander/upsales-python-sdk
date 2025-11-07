"""
Static values models for Upsales API.

The /api/v2/staticValues/all endpoint returns system-wide reference data
including company statuses, credit ratings, industry codes, outcome types, etc.

Unlike typical REST endpoints, this returns a single dict containing multiple
categories of static values. This is a read-only endpoint.

Example:
    >>> static_values = await upsales.static_values.get()
    >>> # Access status values
    >>> active_status = static_values.get_status_by_id("active")
    >>> # Access credit ratings
    >>> rating_a = static_values.get_credit_rating_by_id("a")
"""

from typing import TYPE_CHECKING

from pydantic import BaseModel as PydanticBase
from pydantic import ConfigDict, Field, computed_field

if TYPE_CHECKING:
    from upsales.client import Upsales

from upsales.validators import NonEmptyStr


class StaticValue(PydanticBase):
    """
    Base model for simple static values (id + name).

    Most static values in the system follow this pattern.

    Attributes:
        id: Unique identifier (string)
        name: Display name or translation key

    Example:
        >>> status = StaticValue(id="active", name="default.companyStatus.ACTIVE")
        >>> status.id
        'active'
    """

    model_config = ConfigDict(
        frozen=False,
        validate_assignment=True,
        extra="allow",
        populate_by_name=True,
    )

    id: NonEmptyStr = Field(description="Unique identifier")
    name: NonEmptyStr = Field(description="Display name or translation key")


class CreditRating(StaticValue):
    """
    Credit rating static value with additional chip type.

    Extends StaticValue with UI presentation hint.

    Attributes:
        id: Credit rating code (e.g., 'a', 'aa', 'aaa', 'b', 'c')
        name: Display name or translation key
        assistChipType: UI chip style (success, alert, danger, info)

    Example:
        >>> rating = await static_values.get_credit_rating_by_id("aaa")
        >>> rating.is_high_rating
        True
        >>> rating.assistChipType
        'success'
    """

    assistChipType: NonEmptyStr | None = Field(None, description="UI chip style hint")

    @computed_field
    @property
    def is_high_rating(self) -> bool:
        """
        Check if this is a high credit rating (A, AA, AAA).

        Returns:
            True if rating is A, AA, or AAA.

        Example:
            >>> rating.id = "aaa"
            >>> rating.is_high_rating
            True
        """
        return self.id.lower() in ("a", "aa", "aaa")

    @computed_field
    @property
    def is_low_rating(self) -> bool:
        """
        Check if this is a low credit rating (B, C).

        Returns:
            True if rating is B or C.

        Example:
            >>> rating.id = "c"
            >>> rating.is_low_rating
            True
        """
        return self.id.lower() in ("b", "c")


class IndustryCode(PydanticBase):
    """
    Industry classification code (SNI, SIC, NACE, NAICS, etc).

    Large lists of standardized industry codes.

    Attributes:
        id: Industry code identifier
        name: Industry description

    Example:
        >>> sni_codes = static_values.sniCode
        >>> tech_code = next(c for c in sni_codes if "software" in c.name.lower())
    """

    model_config = ConfigDict(
        frozen=False,
        validate_assignment=True,
        extra="allow",
        populate_by_name=True,
    )

    id: NonEmptyStr = Field(description="Industry code identifier")
    name: NonEmptyStr = Field(description="Industry description")


class StaticValues(PydanticBase):
    """
    Container for all static values from /api/v2/staticValues/all.

    This model wraps all categories of static reference data used throughout
    the Upsales system.

    Attributes:
        status: Company status codes (19 values)
        creditRating: Credit rating values with chip types (7 values)
        prospectingCreditRating: Simplified credit ratings (7 values)
        companyForm: Company legal forms (16 values)
        sniCode: Swedish SNI industry codes (821 values)
        ukSicCode: UK SIC industry codes (731 values)
        sicCode: US SIC industry codes (1005 values)
        naceCode: European NACE industry codes (1120 values)
        naicsCode: North American NAICS industry codes (1058 values)
        languages: Available languages (8 values)
        recurringInterval: Recurring billing intervals (9 values)
        intervalPeriod: Interval period types (9 values)
        periodLength: Period length options (8 values)
        appointmentOutcome: Appointment outcome types (3 values)
        activityOutcome: Activity outcome types (2 values)
        phonecallOutcome: Phone call outcome types (3 values)

    Example:
        >>> static_values = await upsales.static_values.get()
        >>> # Get all active statuses
        >>> active = static_values.get_status_by_id("active")
        >>> # Count industry codes
        >>> static_values.total_industry_codes
        4535
    """

    model_config = ConfigDict(
        frozen=False,
        validate_assignment=True,
        extra="allow",
        populate_by_name=True,
    )

    # Company-related
    status: list[StaticValue] = Field(default_factory=list, description="Company status codes")
    creditRating: list[CreditRating] = Field(
        default_factory=list, description="Credit rating values with chip types"
    )
    prospectingCreditRating: list[StaticValue] = Field(
        default_factory=list, description="Simplified credit ratings for prospecting"
    )
    companyForm: list[StaticValue] = Field(default_factory=list, description="Company legal forms")

    # Industry codes
    sniCode: list[IndustryCode] = Field(
        default_factory=list, description="Swedish SNI industry codes"
    )
    ukSicCode: list[IndustryCode] = Field(default_factory=list, description="UK SIC industry codes")
    sicCode: list[IndustryCode] = Field(default_factory=list, description="US SIC industry codes")
    naceCode: list[IndustryCode] = Field(
        default_factory=list, description="European NACE industry codes"
    )
    naicsCode: list[IndustryCode] = Field(
        default_factory=list, description="North American NAICS industry codes"
    )

    # Other
    languages: list[StaticValue] = Field(default_factory=list, description="Available languages")
    recurringInterval: list[StaticValue] = Field(
        default_factory=list, description="Recurring billing intervals"
    )
    intervalPeriod: list[StaticValue] = Field(
        default_factory=list, description="Interval period types"
    )
    periodLength: list[StaticValue] = Field(
        default_factory=list, description="Period length options"
    )

    # Activity outcomes
    appointmentOutcome: list[StaticValue] = Field(
        default_factory=list, description="Appointment outcome types"
    )
    activityOutcome: list[StaticValue] = Field(
        default_factory=list, description="Activity outcome types"
    )
    phonecallOutcome: list[StaticValue] = Field(
        default_factory=list, description="Phone call outcome types"
    )

    # Internal reference
    _client: "Upsales | None" = None

    @computed_field
    @property
    def total_industry_codes(self) -> int:
        """
        Count total industry classification codes.

        Returns:
            Total number of industry codes across all classification systems.

        Example:
            >>> static_values.total_industry_codes
            4535
        """
        return (
            len(self.sniCode)
            + len(self.ukSicCode)
            + len(self.sicCode)
            + len(self.naceCode)
            + len(self.naicsCode)
        )

    @computed_field
    @property
    def total_outcome_types(self) -> int:
        """
        Count total activity outcome types.

        Returns:
            Total number of outcome types across all activity types.

        Example:
            >>> static_values.total_outcome_types
            8
        """
        return len(self.appointmentOutcome) + len(self.activityOutcome) + len(self.phonecallOutcome)

    def get_status_by_id(self, status_id: str) -> StaticValue | None:
        """
        Find a company status by ID.

        Args:
            status_id: Status identifier (e.g., 'active', 'inactive')

        Returns:
            StaticValue if found, None otherwise.

        Example:
            >>> status = static_values.get_status_by_id("active")
            >>> status.name
            'default.companyStatus.ACTIVE'
        """
        return next((s for s in self.status if s.id == status_id), None)

    def get_credit_rating_by_id(self, rating_id: str) -> CreditRating | None:
        """
        Find a credit rating by ID.

        Args:
            rating_id: Rating identifier (e.g., 'a', 'aa', 'aaa')

        Returns:
            CreditRating if found, None otherwise.

        Example:
            >>> rating = static_values.get_credit_rating_by_id("aaa")
            >>> rating.is_high_rating
            True
        """
        return next((r for r in self.creditRating if r.id == rating_id), None)

    def get_language_by_id(self, language_id: str) -> StaticValue | None:
        """
        Find a language by ID.

        Args:
            language_id: Language identifier

        Returns:
            StaticValue if found, None otherwise.

        Example:
            >>> lang = static_values.get_language_by_id("en")
            >>> lang.name
            'English'
        """
        return next((lng for lng in self.languages if lng.id == language_id), None)

    def search_industry_codes(self, search_term: str) -> list[IndustryCode]:
        """
        Search for industry codes by name across all classification systems.

        Args:
            search_term: Text to search for in industry descriptions

        Returns:
            List of matching industry codes from all systems.

        Example:
            >>> codes = static_values.search_industry_codes("software")
            >>> len(codes) > 0
            True
        """
        search_lower = search_term.lower()
        results: list[IndustryCode] = []

        for code_list in [
            self.sniCode,
            self.ukSicCode,
            self.sicCode,
            self.naceCode,
            self.naicsCode,
        ]:
            results.extend([c for c in code_list if search_lower in c.name.lower()])

        return results


__all__ = ["StaticValue", "CreditRating", "IndustryCode", "StaticValues"]
