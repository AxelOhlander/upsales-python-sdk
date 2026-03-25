"""
Address models for Upsales API.

Addresses are always nested within other objects (e.g., Company.addresses,
Company.mailAddress) and don't have their own endpoint. These are data models
for type-safe access to structured address information.

Note:
    Addresses don't have edit() or fetch_full() methods since they're not
    standalone resources. They must be updated through their parent object.

Example:
    >>> company = await upsales.companies.get(1)
    >>> if company.addresses:
    ...     address = company.addresses[0]
    ...     print(f"{address.address}, {address.city}")  # Type-safe!
    ...     print(f"Type: {address.type}")
    >>> if company.mailAddress:
    ...     print(f"Mail: {company.mailAddress.address}")
"""

from typing import Any

from pydantic import BaseModel as PydanticBase
from pydantic import ConfigDict, Field, computed_field


class Address(PydanticBase):
    """
    Address model for company addresses.

    Represents a complete address with all fields present. Used for both
    physical addresses (type="Visit") and mail addresses (type="Mail").

    Note:
        Addresses don't have their own API endpoint. They must be managed
        through parent objects (e.g., Company).

    Example:
        >>> address = Address(
        ...     type="Visit",
        ...     address="Bergsnäsgatan 11",
        ...     city="Avesta",
        ...     country="SE",
        ...     zipcode="77441"
        ... )
        >>> address.is_visit_address
        True
        >>> address.full_address
        'Bergsnäsgatan 11, 77441 Avesta, DALARNA, SE'
    """

    model_config = ConfigDict(
        frozen=False,  # Mutable models
        validate_assignment=True,  # Validate on assignment
        extra="allow",  # Allow extra fields from API
        populate_by_name=True,  # Allow both field name and alias
    )

    # Core address fields (can be null from API)
    type: str | None = Field(None, description="Address type (e.g., 'Visit', 'Mail')")
    address: str | None = Field(None, description="Street address (can be empty or null)")
    city: str | None = Field(None, description="City name (can be empty or null)")
    country: str | None = Field(None, description="Country code (e.g., 'SE', 'US', can be null)")

    # Optional address fields
    zipcode: str | None = Field(None, description="Postal/ZIP code")
    state: str | None = Field(None, description="State/region/province")
    municipality: str | None = Field(None, description="Municipality")

    # Geolocation fields
    latitude: float | None = Field(None, description="Latitude coordinate")
    longitude: float | None = Field(None, description="Longitude coordinate")

    @computed_field
    @property
    def full_address(self) -> str:
        """
        Get full formatted address string.

        Returns:
            Complete address formatted as single string.

        Example:
            >>> address.full_address
            'Bergsnäsgatan 11, 77441, Avesta, DALARNA, SE'
        """
        parts = []
        if self.address:
            parts.append(self.address)
        if self.zipcode:
            parts.append(self.zipcode)
        if self.city:
            parts.append(self.city)
        if self.state:
            parts.append(self.state)
        if self.country:
            parts.append(self.country)
        return ", ".join(parts)

    @computed_field
    @property
    def is_visit_address(self) -> bool:
        """
        Check if this is a visit address.

        Returns:
            True if type is "Visit", False otherwise.

        Example:
            >>> address.is_visit_address
            True
        """
        return bool(self.type and self.type.lower() == "visit")

    @computed_field
    @property
    def is_mail_address(self) -> bool:
        """
        Check if this is a mail address.

        Returns:
            True if type is "Mail", False otherwise.

        Example:
            >>> address.is_mail_address
            False
        """
        return bool(self.type and self.type.lower() == "mail")

    @computed_field
    @property
    def has_geolocation(self) -> bool:
        """
        Check if address has geolocation data.

        Returns:
            True if both latitude and longitude are present.

        Example:
            >>> address.has_geolocation
            True
        """
        return self.latitude is not None and self.longitude is not None

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize address to dict for API requests.

        Returns:
            Dict suitable for API requests, excluding computed fields.

        Example:
            >>> address_dict = address.to_dict()
            >>> # Returns: {'type': 'Visit', 'address': '...', ...}
        """
        return self.model_dump(
            mode="python",
            exclude={"full_address", "is_visit_address", "is_mail_address", "has_geolocation"},
            exclude_none=False,  # Include None values
        )

    def __repr__(self) -> str:
        """
        Return string representation of the address.

        Returns:
            String like "<Address type=Visit city=Avesta>".
        """
        return f"<{self.__class__.__name__} type={self.type} city={self.city}>"


class PartialAddress(PydanticBase):
    """
    Partial Address model for minimal address data.

    Minimal address information for nested responses where not all fields
    are guaranteed to be present. Use Address for complete address data.

    Note:
        PartialAddress doesn't have fetch_full() or edit() methods since
        addresses are not standalone resources with their own endpoint.

    Example:
        >>> company = await upsales.companies.get(1)
        >>> for address in company.addresses:
        ...     print(f"{address.type}: {address.city}")
        Visit: Avesta
        Mail: Stockholm
    """

    model_config = ConfigDict(
        frozen=False,  # Mutable models
        validate_assignment=True,  # Validate on assignment
        extra="allow",  # Allow extra fields from API
        populate_by_name=True,  # Allow both field name and alias
    )

    # Core address fields (can be null from API)
    type: str | None = Field(None, description="Address type (e.g., 'Visit', 'Mail')")
    address: str | None = Field(None, description="Street address (can be null)")
    city: str | None = Field(None, description="City name (can be null)")
    country: str | None = Field(None, description="Country code (e.g., 'SE', 'US', can be null)")

    # Optional fields that may be present
    zipcode: str | None = Field(None, description="Postal/ZIP code")
    state: str | None = Field(None, description="State/region/province")
    municipality: str | None = Field(None, description="Municipality")
    latitude: float | None = Field(None, description="Latitude coordinate")
    longitude: float | None = Field(None, description="Longitude coordinate")

    @computed_field
    @property
    def is_visit_address(self) -> bool:
        """
        Check if this is a visit address.

        Returns:
            True if type is "Visit", False otherwise.

        Example:
            >>> address.is_visit_address
            True
        """
        return bool(self.type and self.type.lower() == "visit")

    @computed_field
    @property
    def is_mail_address(self) -> bool:
        """
        Check if this is a mail address.

        Returns:
            True if type is "Mail", False otherwise.

        Example:
            >>> address.is_mail_address
            False
        """
        return bool(self.type and self.type.lower() == "mail")

    @computed_field
    @property
    def has_geolocation(self) -> bool:
        """
        Check if address has geolocation data.

        Returns:
            True if both latitude and longitude are present.

        Example:
            >>> address.has_geolocation
            True
        """
        return self.latitude is not None and self.longitude is not None

    def to_full(self) -> Address:
        """
        Convert partial address to full Address model.

        Returns:
            Full Address model with all available fields.

        Example:
            >>> partial = PartialAddress(type="Visit", address="...", city="...", country="...")
            >>> full = partial.to_full()
            >>> full.full_address
            '...'
        """
        return Address(**self.model_dump())

    def __repr__(self) -> str:
        """
        Return string representation of the partial address.

        Returns:
            String like "<PartialAddress type=Visit city=Avesta>".
        """
        return f"<{self.__class__.__name__} type={self.type} city={self.city}>"
