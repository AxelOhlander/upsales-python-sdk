"""
Address type constants for Upsales addresses.

Defines valid address type values used in the Address model and AddressList.
"""

from enum import StrEnum


class AddressType(StrEnum):
    """
    Valid address type values for Upsales addresses.

    The Upsales API uses these type values to categorize addresses.
    AddressList provides convenient property access for each type.

    Values discovered from:
    - AddressList property methods (.mail, .visit, .postal, .billing, .delivery)
    - Real API responses (VCR cassettes)
    - API documentation

    Example:
        >>> from upsales.models.address_types import AddressType
        >>>
        >>> # Create address with typed value
        >>> address = Address(
        ...     type=AddressType.VISIT,
        ...     address="123 Main St",
        ...     city="New York",
        ...     country="US"
        ... )
        >>>
        >>> # Check type
        >>> if address.type == AddressType.MAIL:
        ...     print("This is a mailing address")
        >>>
        >>> # Use in API requests
        >>> new_company = await upsales.companies.create(
        ...     name="ACME Corp",
        ...     addresses=[{
        ...         "type": AddressType.VISIT,
        ...         "address": "123 Main St",
        ...         "city": "New York",
        ...         "country": "US"
        ...     }]
        ... )
    """

    MAIL = "Mail"
    """Mailing/postal address for correspondence."""

    VISIT = "Visit"
    """Physical visiting address (headquarters, office location)."""

    POSTAL = "Postal"
    """Postal address (may differ from visiting address)."""

    BILLING = "Billing"
    """Billing address for invoices."""

    DELIVERY = "Delivery"
    """Delivery address for shipments."""

    OTHER = "Other"
    """Other/miscellaneous address type."""


# Constant list for validation
VALID_ADDRESS_TYPES = [t.value for t in AddressType]
"""List of valid address type strings: ['Mail', 'Visit', 'Postal', 'Billing', 'Delivery', 'Other']"""


# For backward compatibility and convenience
MAIL = AddressType.MAIL
VISIT = AddressType.VISIT
POSTAL = AddressType.POSTAL
BILLING = AddressType.BILLING
DELIVERY = AddressType.DELIVERY
OTHER = AddressType.OTHER
