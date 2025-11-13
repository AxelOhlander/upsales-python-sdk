"""
Tests for Address and PartialAddress models.

Uses Python 3.13 native type hints.
"""

from typing import Any

import pytest
from pydantic import ValidationError

from upsales.models.address import Address, PartialAddress


@pytest.fixture
def sample_address_data() -> dict[str, Any]:
    """
    Sample address data from API.

    Returns:
        Dict with complete address data.
    """
    return {
        "type": "Visit",
        "address": "Bergsnäsgatan 11",
        "zipcode": "77441",
        "state": "DALARNA",
        "city": "Avesta",
        "municipality": None,
        "country": "SE",
        "latitude": 60.137989,
        "longitude": 16.184715,
    }


@pytest.fixture
def sample_mail_address_data() -> dict[str, Any]:
    """
    Sample mail address data from API.

    Returns:
        Dict with mail address data.
    """
    return {
        "type": "Mail",
        "address": "Box 74",
        "zipcode": "77422",
        "city": "Avesta",
        "state": "DALARNA",
        "municipality": None,
        "country": "SE",
        "latitude": 60.124591,
        "longitude": 16.216351,
    }


@pytest.fixture
def minimal_address_data() -> dict[str, Any]:
    """
    Minimal address data (required fields only).

    Returns:
        Dict with minimum required address fields.
    """
    return {
        "type": "Visit",
        "address": "123 Main St",
        "city": "Stockholm",
        "country": "SE",
    }


# ============================================================================
# Address Model Tests
# ============================================================================


def test_address_creation(sample_address_data):
    """Test creating Address with complete data."""
    address = Address(**sample_address_data)

    assert address.type == "Visit"
    assert address.address == "Bergsnäsgatan 11"
    assert address.city == "Avesta"
    assert address.country == "SE"
    assert address.zipcode == "77441"
    assert address.state == "DALARNA"
    assert address.latitude == 60.137989
    assert address.longitude == 16.184715


def test_address_minimal_creation(minimal_address_data):
    """Test creating Address with minimal required fields."""
    address = Address(**minimal_address_data)

    assert address.type == "Visit"
    assert address.address == "123 Main St"
    assert address.city == "Stockholm"
    assert address.country == "SE"
    assert address.zipcode is None
    assert address.state is None
    assert address.latitude is None
    assert address.longitude is None


def test_address_validates_required_fields():
    """Test that Address validates required fields (but allows empty strings)."""
    # Missing type - should raise
    with pytest.raises(ValidationError, match="type"):
        Address(address="123 Main St", city="Stockholm", country="SE")

    # Missing address - should raise
    with pytest.raises(ValidationError, match="address"):
        Address(type="Visit", city="Stockholm", country="SE")

    # Missing city - should raise
    with pytest.raises(ValidationError, match="city"):
        Address(type="Visit", address="123 Main St", country="SE")

    # Missing country - should raise
    with pytest.raises(ValidationError, match="country"):
        Address(type="Visit", address="123 Main St", city="Stockholm")


def test_address_validates_non_empty_strings():
    """Test that Address allows empty strings (API can return empty strings)."""
    # Empty type is allowed by API
    address = Address(type="", address="123 Main St", city="Stockholm", country="SE")
    assert address.type == ""

    # Whitespace-only type is allowed
    address = Address(type="   ", address="123 Main St", city="Stockholm", country="SE")
    assert address.type == "   "

    # Empty address is allowed by API
    address = Address(type="Visit", address="", city="Stockholm", country="SE")
    assert address.address == ""


def test_address_full_address_computed(sample_address_data):
    """Test full_address computed field."""
    address = Address(**sample_address_data)
    expected = "Bergsnäsgatan 11, 77441, Avesta, DALARNA, SE"

    assert address.full_address == expected


def test_address_full_address_minimal(minimal_address_data):
    """Test full_address computed field with minimal data."""
    address = Address(**minimal_address_data)
    # Should handle missing optional fields gracefully
    assert "123 Main St" in address.full_address
    assert "Stockholm" in address.full_address
    assert "SE" in address.full_address


def test_address_is_visit_address(sample_address_data):
    """Test is_visit_address computed field."""
    address = Address(**sample_address_data)
    assert address.is_visit_address is True
    assert address.is_mail_address is False


def test_address_is_mail_address(sample_mail_address_data):
    """Test is_mail_address computed field."""
    address = Address(**sample_mail_address_data)
    assert address.is_mail_address is True
    assert address.is_visit_address is False


def test_address_is_visit_address_case_insensitive():
    """Test is_visit_address is case-insensitive."""
    address_upper = Address(type="VISIT", address="123", city="City", country="SE")
    address_mixed = Address(type="ViSiT", address="123", city="City", country="SE")

    assert address_upper.is_visit_address is True
    assert address_mixed.is_visit_address is True


def test_address_has_geolocation(sample_address_data, minimal_address_data):
    """Test has_geolocation computed field."""
    # With geolocation
    address_with_geo = Address(**sample_address_data)
    assert address_with_geo.has_geolocation is True

    # Without geolocation
    address_no_geo = Address(**minimal_address_data)
    assert address_no_geo.has_geolocation is False

    # Partial geolocation (only latitude)
    address_partial = Address(
        type="Visit",
        address="123",
        city="City",
        country="SE",
        latitude=60.0,
    )
    assert address_partial.has_geolocation is False


def test_address_to_dict(sample_address_data):
    """Test to_dict serialization."""
    address = Address(**sample_address_data)
    data = address.to_dict()

    # Should include all fields
    assert data["type"] == "Visit"
    assert data["address"] == "Bergsnäsgatan 11"
    assert data["city"] == "Avesta"
    assert data["country"] == "SE"

    # Should NOT include computed fields
    assert "full_address" not in data
    assert "is_visit_address" not in data
    assert "is_mail_address" not in data
    assert "has_geolocation" not in data


def test_address_repr(sample_address_data):
    """Test string representation."""
    address = Address(**sample_address_data)
    repr_str = repr(address)

    assert "Address" in repr_str
    assert "type=Visit" in repr_str
    assert "city=Avesta" in repr_str


def test_address_mutability(sample_address_data):
    """Test that Address is mutable."""
    address = Address(**sample_address_data)

    # Should allow assignment
    address.city = "Stockholm"
    assert address.city == "Stockholm"

    # Should allow empty strings (API can return them)
    address.city = ""
    assert address.city == ""


# ============================================================================
# PartialAddress Model Tests
# ============================================================================


def test_partial_address_creation(sample_address_data):
    """Test creating PartialAddress with complete data."""
    address = PartialAddress(**sample_address_data)

    assert address.type == "Visit"
    assert address.address == "Bergsnäsgatan 11"
    assert address.city == "Avesta"
    assert address.country == "SE"


def test_partial_address_minimal_creation(minimal_address_data):
    """Test creating PartialAddress with minimal required fields."""
    address = PartialAddress(**minimal_address_data)

    assert address.type == "Visit"
    assert address.address == "123 Main St"
    assert address.city == "Stockholm"
    assert address.country == "SE"


def test_partial_address_validates_required_fields():
    """Test that PartialAddress validates required fields."""
    # Missing type
    with pytest.raises(ValidationError, match="type"):
        PartialAddress(address="123 Main St", city="Stockholm", country="SE")

    # Missing address
    with pytest.raises(ValidationError, match="address"):
        PartialAddress(type="Visit", city="Stockholm", country="SE")


def test_partial_address_allows_empty_strings():
    """Test that PartialAddress allows empty strings (less strict)."""
    # PartialAddress uses str, not NonEmptyStr, so empty strings are allowed
    address = PartialAddress(type="", address="", city="", country="")

    assert address.type == ""
    assert address.address == ""


def test_partial_address_is_visit_address():
    """Test is_visit_address computed field on PartialAddress."""
    address = PartialAddress(
        type="Visit",
        address="123 Main St",
        city="Stockholm",
        country="SE",
    )
    assert address.is_visit_address is True
    assert address.is_mail_address is False


def test_partial_address_has_geolocation():
    """Test has_geolocation computed field on PartialAddress."""
    # With geolocation
    address_with_geo = PartialAddress(
        type="Visit",
        address="123",
        city="City",
        country="SE",
        latitude=60.0,
        longitude=16.0,
    )
    assert address_with_geo.has_geolocation is True

    # Without geolocation
    address_no_geo = PartialAddress(
        type="Visit",
        address="123",
        city="City",
        country="SE",
    )
    assert address_no_geo.has_geolocation is False


def test_partial_address_to_full(sample_address_data):
    """Test converting PartialAddress to full Address."""
    partial = PartialAddress(**sample_address_data)
    full = partial.to_full()

    assert isinstance(full, Address)
    assert full.type == partial.type
    assert full.address == partial.address
    assert full.city == partial.city
    assert full.country == partial.country
    assert full.latitude == partial.latitude


def test_partial_address_to_full_validates():
    """Test that to_full() successfully converts even with empty strings."""
    # Both PartialAddress and Address allow empty strings (API reality)
    partial = PartialAddress(type="", address="", city="", country="")

    # Should successfully convert to Address
    full = partial.to_full()
    assert isinstance(full, Address)
    assert full.type == ""
    assert full.address == ""


def test_partial_address_repr():
    """Test string representation of PartialAddress."""
    address = PartialAddress(
        type="Visit",
        address="123 Main St",
        city="Stockholm",
        country="SE",
    )
    repr_str = repr(address)

    assert "PartialAddress" in repr_str
    assert "type=Visit" in repr_str
    assert "city=Stockholm" in repr_str


# ============================================================================
# Integration Tests
# ============================================================================


def test_address_in_list():
    """Test using Address in a list (like Company.addresses)."""
    addresses = [
        Address(type="Visit", address="123 Main", city="City1", country="SE"),
        Address(type="Mail", address="Box 1", city="City2", country="SE"),
    ]

    visit_addresses = [a for a in addresses if a.is_visit_address]
    mail_addresses = [a for a in addresses if a.is_mail_address]

    assert len(visit_addresses) == 1
    assert len(mail_addresses) == 1


def test_address_extra_fields():
    """Test that Address allows extra fields from API."""
    # API might return extra fields we don't know about yet
    data = {
        "type": "Visit",
        "address": "123 Main St",
        "city": "Stockholm",
        "country": "SE",
        "unknown_field": "some_value",
    }

    # Should not raise error (extra="allow" in config)
    address = Address(**data)
    assert address.type == "Visit"


def test_partial_address_extra_fields():
    """Test that PartialAddress allows extra fields from API."""
    data = {
        "type": "Visit",
        "address": "123 Main St",
        "city": "Stockholm",
        "country": "SE",
        "future_field": 123,
    }

    # Should not raise error (extra="allow" in config)
    address = PartialAddress(**data)
    assert address.type == "Visit"
