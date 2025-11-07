"""
Static values resource manager for Upsales API.

Manages /api/v2/staticValues/all endpoint operations.

IMPORTANT: This endpoint is read-only and returns a single dict (not a list).
This endpoint provides system-wide reference data including company statuses,
credit ratings, industry codes, and outcome types.

This resource manager provides:
- get(): Get all static values (single dict with multiple categories)

Standard operations like create(), update(), delete(), list() are not applicable.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from upsales.http import HTTPClient

from upsales.models.static_values import CreditRating, IndustryCode, StaticValue, StaticValues


class StaticValuesResource:
    """
    Resource manager for /api/v2/staticValues/all endpoint.

    Note: Unlike most resources, this returns a single dict with reference data
    organized by category rather than a list of items. This endpoint is read-only.

    Args:
        http: HTTP client instance for making API requests.

    Attributes:
        _http: HTTP client for API requests.
        _endpoint: API endpoint path (/staticValues/all).

    Example:
        >>> async with Upsales.from_env() as upsales:
        ...     # Get all static values
        ...     static_values = await upsales.static_values.get()
        ...     print(f"Total industry codes: {static_values.total_industry_codes}")
        ...
        ...     # Find specific values
        ...     active_status = static_values.get_status_by_id("active")
        ...     rating_aaa = static_values.get_credit_rating_by_id("aaa")
        ...
        ...     # Search industry codes
        ...     software_codes = static_values.search_industry_codes("software")
        ...     print(f"Found {len(software_codes)} software-related codes")
    """

    def __init__(self, http: HTTPClient) -> None:
        """
        Initialize static values resource manager.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/staticValues/all"

    async def get(self) -> StaticValues:
        """
        Get all static reference values.

        Returns system-wide reference data including company statuses, credit
        ratings, industry classification codes, language options, and activity
        outcome types in a single StaticValues object.

        Returns:
            StaticValues object containing all reference data categories.

        Raises:
            UpsalesError: If API request fails.

        Example:
            >>> static_values = await upsales.static_values.get()
            >>> # Access company statuses
            >>> active = static_values.get_status_by_id("active")
            >>> print(active.name)
            'default.companyStatus.ACTIVE'
            >>>
            >>> # Access credit ratings
            >>> rating = static_values.get_credit_rating_by_id("aaa")
            >>> print(rating.is_high_rating)
            True
            >>>
            >>> # Count industry codes
            >>> print(static_values.total_industry_codes)
            4535
        """
        response = await self._http.get(self._endpoint)
        # Extract data from response wrapper
        return StaticValues(**response["data"], _client=self._http._upsales_client)

    async def get_statuses(self) -> list[StaticValue]:
        """
        Get all company status values.

        Convenience method to access company statuses without fetching all
        static values.

        Returns:
            List of company status StaticValue objects (19 items).

        Raises:
            UpsalesError: If API request fails.

        Example:
            >>> statuses = await upsales.static_values.get_statuses()
            >>> for status in statuses:
            ...     print(f"{status.id}: {status.name}")
            active: default.companyStatus.ACTIVE
            inactive: default.companyStatus.INACTIVE
            ...
        """
        static_values = await self.get()
        return static_values.status

    async def get_credit_ratings(self) -> list[CreditRating]:
        """
        Get all credit rating values.

        Convenience method to access credit ratings without fetching all
        static values.

        Returns:
            List of CreditRating objects with chip type information (7 items).

        Raises:
            UpsalesError: If API request fails.

        Example:
            >>> ratings = await upsales.static_values.get_credit_ratings()
            >>> for rating in ratings:
            ...     print(f"{rating.id}: {rating.name} ({rating.assistChipType})")
            aaa: admin.customfieldCreditRatingAAA (success)
            aa: admin.customfieldCreditRatingAA (success)
            a: admin.customfieldCreditRatingA (success)
            b: admin.customfieldCreditRatingB (alert)
            c: admin.customfieldCreditRatingC (danger)
            ...
        """
        static_values = await self.get()
        return static_values.creditRating

    async def get_company_forms(self) -> list[StaticValue]:
        """
        Get all company legal form values.

        Returns:
            List of company form StaticValue objects (16 items).

        Raises:
            UpsalesError: If API request fails.

        Example:
            >>> forms = await upsales.static_values.get_company_forms()
            >>> len(forms)
            16
        """
        static_values = await self.get()
        return static_values.companyForm

    async def get_industry_codes(self, system: str | None = None) -> list[IndustryCode]:
        """
        Get industry classification codes.

        Args:
            system: Classification system name (sni, uksic, sic, nace, naics).
                If None, returns all codes from all systems.

        Returns:
            List of IndustryCode objects. If system is None, returns all codes
            from all classification systems combined.

        Raises:
            ValueError: If invalid system name provided.
            UpsalesError: If API request fails.

        Example:
            >>> # Get all industry codes
            >>> all_codes = await upsales.static_values.get_industry_codes()
            >>> len(all_codes)
            4535
            >>>
            >>> # Get specific system
            >>> sni_codes = await upsales.static_values.get_industry_codes("sni")
            >>> len(sni_codes)
            821
        """
        static_values = await self.get()

        if system is None:
            # Return all codes from all systems
            return (
                static_values.sniCode
                + static_values.ukSicCode
                + static_values.sicCode
                + static_values.naceCode
                + static_values.naicsCode
            )

        system_map = {
            "sni": static_values.sniCode,
            "uksic": static_values.ukSicCode,
            "sic": static_values.sicCode,
            "nace": static_values.naceCode,
            "naics": static_values.naicsCode,
        }

        system_lower = system.lower()
        if system_lower not in system_map:
            valid_systems = ", ".join(system_map.keys())
            raise ValueError(f"Invalid system '{system}'. Must be one of: {valid_systems}")

        return system_map[system_lower]

    async def get_languages(self) -> list[StaticValue]:
        """
        Get all available language values.

        Returns:
            List of language StaticValue objects (8 items).

        Raises:
            UpsalesError: If API request fails.

        Example:
            >>> languages = await upsales.static_values.get_languages()
            >>> for lang in languages:
            ...     print(f"{lang.id}: {lang.name}")
        """
        static_values = await self.get()
        return static_values.languages

    async def get_outcome_types(self, activity_type: str | None = None) -> list[StaticValue]:
        """
        Get activity outcome types.

        Args:
            activity_type: Type of activity (appointment, activity, phonecall).
                If None, returns all outcome types from all activity types.

        Returns:
            List of StaticValue objects for the specified activity type outcomes.

        Raises:
            ValueError: If invalid activity_type provided.
            UpsalesError: If API request fails.

        Example:
            >>> # Get all outcome types
            >>> all_outcomes = await upsales.static_values.get_outcome_types()
            >>> len(all_outcomes)
            8
            >>>
            >>> # Get appointment outcomes only
            >>> apt_outcomes = await upsales.static_values.get_outcome_types("appointment")
            >>> len(apt_outcomes)
            3
        """
        static_values = await self.get()

        if activity_type is None:
            # Return all outcomes from all activity types
            return (
                static_values.appointmentOutcome
                + static_values.activityOutcome
                + static_values.phonecallOutcome
            )

        type_map = {
            "appointment": static_values.appointmentOutcome,
            "activity": static_values.activityOutcome,
            "phonecall": static_values.phonecallOutcome,
        }

        type_lower = activity_type.lower()
        if type_lower not in type_map:
            valid_types = ", ".join(type_map.keys())
            raise ValueError(
                f"Invalid activity_type '{activity_type}'. Must be one of: {valid_types}"
            )

        return type_map[type_lower]

    async def search_industry_codes(self, search_term: str) -> list[IndustryCode]:
        """
        Search for industry codes by name across all classification systems.

        Args:
            search_term: Text to search for in industry descriptions (case-insensitive).

        Returns:
            List of matching IndustryCode objects from all systems.

        Raises:
            UpsalesError: If API request fails.

        Example:
            >>> # Search for software-related codes
            >>> codes = await upsales.static_values.search_industry_codes("software")
            >>> for code in codes[:3]:
            ...     print(f"{code.id}: {code.name}")
            62.01: Computer programming activities
            62.02: Computer consultancy activities
            ...
        """
        static_values = await self.get()
        return static_values.search_industry_codes(search_term)


__all__ = ["StaticValuesResource"]
