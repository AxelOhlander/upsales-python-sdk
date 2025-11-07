"""
Tests for AddressList collection.

Tests the smart address collection that provides both list-like access
and convenient property accessors for address types.
"""

import pytest

from upsales.models.address import Address
from upsales.models.address_list import AddressList


class TestAddressListCreation:
    """Test AddressList creation and initialization."""

    def test_create_empty(self):
        """Test creating empty AddressList."""
        addresses = AddressList()
        assert len(addresses) == 0
        assert not addresses
        assert list(addresses) == []

    def test_create_with_addresses(self):
        """Test creating AddressList with addresses."""
        addr1 = Address(type="Mail", address="Box 123", city="Stockholm", country="SE")
        addr2 = Address(type="Visit", address="Main St 1", city="Stockholm", country="SE")

        addresses = AddressList([addr1, addr2])
        assert len(addresses) == 2
        assert addresses


class TestAddressListPropertyAccess:
    """Test property accessors for address types."""

    def test_mail_address(self):
        """Test accessing mail address."""
        mail = Address(type="Mail", address="Box 123", city="Stockholm", country="SE")
        visit = Address(type="Visit", address="Main St 1", city="Stockholm", country="SE")

        addresses = AddressList([mail, visit])

        assert addresses.mail is not None
        assert addresses.mail.type == "Mail"
        assert addresses.mail.address == "Box 123"

    def test_visit_address(self):
        """Test accessing visit address."""
        visit = Address(type="Visit", address="Main St 1", city="Stockholm", country="SE")
        addresses = AddressList([visit])

        assert addresses.visit is not None
        assert addresses.visit.city == "Stockholm"

    def test_postal_address(self):
        """Test accessing postal address."""
        postal = Address(type="Postal", address="PO Box 456", city="Malmö", country="SE")
        addresses = AddressList([postal])

        assert addresses.postal is not None
        assert addresses.postal.address == "PO Box 456"

    def test_billing_address(self):
        """Test accessing billing address."""
        billing = Address(type="Billing", address="Invoice St", city="Göteborg", country="SE")
        addresses = AddressList([billing])

        assert addresses.billing is not None
        assert addresses.billing.city == "Göteborg"

    def test_delivery_address(self):
        """Test accessing delivery address."""
        delivery = Address(type="Delivery", address="Warehouse Rd", city="Uppsala", country="SE")
        addresses = AddressList([delivery])

        assert addresses.delivery is not None
        assert addresses.delivery.type == "Delivery"

    def test_missing_address_type(self):
        """Test accessing non-existent address type returns None."""
        mail = Address(type="Mail", address="Box 123", city="Stockholm", country="SE")
        addresses = AddressList([mail])

        assert addresses.visit is None
        assert addresses.postal is None
        assert addresses.billing is None
        assert addresses.delivery is None


class TestAddressListMethods:
    """Test AddressList helper methods."""

    def test_get_by_type_case_insensitive(self):
        """Test get_by_type with case variations."""
        mail = Address(type="Mail", address="Box 123", city="Stockholm", country="SE")
        addresses = AddressList([mail])

        assert addresses.get_by_type("mail") is not None
        assert addresses.get_by_type("MAIL") is not None
        assert addresses.get_by_type("Mail") is not None

    def test_get_by_type_not_found(self):
        """Test get_by_type returns None when not found."""
        mail = Address(type="Mail", address="Box 123", city="Stockholm", country="SE")
        addresses = AddressList([mail])

        assert addresses.get_by_type("Visit") is None

    def test_filter_by_country(self):
        """Test filtering addresses by country."""
        se_addr = Address(type="Mail", address="Box 1", city="Stockholm", country="SE")
        us_addr = Address(type="Visit", address="5th Ave", city="New York", country="US")
        se_addr2 = Address(type="Billing", address="Main St", city="Malmö", country="SE")

        addresses = AddressList([se_addr, us_addr, se_addr2])

        se_addresses = addresses.filter_by_country("SE")
        assert len(se_addresses) == 2
        assert all(a.country == "SE" for a in se_addresses)

        us_addresses = addresses.filter_by_country("US")
        assert len(us_addresses) == 1
        assert us_addresses[0].city == "New York"

    def test_all_method(self):
        """Test getting all addresses as list."""
        addr1 = Address(type="Mail", address="Box 1", city="City1", country="SE")
        addr2 = Address(type="Visit", address="St 1", city="City2", country="SE")

        addresses = AddressList([addr1, addr2])
        all_addrs = addresses.all()

        assert len(all_addrs) == 2
        assert isinstance(all_addrs, list)
        # Should be a copy
        all_addrs.append(Address(type="Postal", address="X", city="Y", country="Z"))
        assert len(addresses) == 2  # Original unchanged


class TestAddressListListBehavior:
    """Test list-like behavior of AddressList."""

    def test_iteration(self):
        """Test iterating over addresses."""
        addr1 = Address(type="Mail", address="Box 1", city="City1", country="SE")
        addr2 = Address(type="Visit", address="St 1", city="City2", country="SE")

        addresses = AddressList([addr1, addr2])

        types = [a.type for a in addresses]
        assert types == ["Mail", "Visit"]

    def test_indexing(self):
        """Test accessing by index."""
        addr1 = Address(type="Mail", address="Box 1", city="City1", country="SE")
        addr2 = Address(type="Visit", address="St 1", city="City2", country="SE")

        addresses = AddressList([addr1, addr2])

        assert addresses[0].type == "Mail"
        assert addresses[1].type == "Visit"

    def test_length(self):
        """Test len() function."""
        addr1 = Address(type="Mail", address="Box 1", city="City1", country="SE")
        addr2 = Address(type="Visit", address="St 1", city="City2", country="SE")

        addresses = AddressList([addr1, addr2])

        assert len(addresses) == 2

    def test_boolean_true(self):
        """Test boolean evaluation when addresses exist."""
        addr = Address(type="Mail", address="Box 1", city="City1", country="SE")
        addresses = AddressList([addr])

        assert bool(addresses) is True
        assert addresses  # Truthy

    def test_boolean_false(self):
        """Test boolean evaluation when empty."""
        addresses = AddressList()

        assert bool(addresses) is False
        assert not addresses  # Falsy

    def test_repr(self):
        """Test string representation."""
        addresses = AddressList([
            Address(type="Mail", address="Box 1", city="City", country="SE"),
            Address(type="Visit", address="St 1", city="City", country="SE"),
        ])

        assert repr(addresses) == "<AddressList count=2>"


class TestAddressListIntegration:
    """Test AddressList in realistic scenarios."""

    def test_company_address_access_pattern(self):
        """Test typical usage pattern with company addresses."""
        addresses = AddressList([
            Address(type="Visit", address="Bergsnäsgatan 11", city="Avesta", country="SE", zipcode="77441"),
            Address(type="Mail", address="Box 74", city="Stockholm", country="SE", zipcode="10052"),
            Address(type="Billing", address="Invoice Dept", city="Malmö", country="SE"),
        ])

        # Property access
        assert addresses.mail is not None
        assert addresses.mail.city == "Stockholm"

        assert addresses.visit is not None
        assert addresses.visit.zipcode == "77441"

        assert addresses.billing is not None
        assert addresses.billing.city == "Malmö"

        # No postal or delivery
        assert addresses.postal is None
        assert addresses.delivery is None

        # List access
        assert len(addresses) == 3
        first = addresses[0]
        assert first.type == "Visit"

    def test_iterate_with_computed_fields(self):
        """Test iterating and using Address computed fields."""
        addresses = AddressList([
            Address(type="Visit", address="Main St 1", city="City1", country="SE", latitude=59.0, longitude=18.0),
            Address(type="Mail", address="Box 1", city="City2", country="SE"),
        ])

        with_geo = [a for a in addresses if a.has_geolocation]
        assert len(with_geo) == 1
        assert with_geo[0].type == "Visit"

        visit_addrs = [a for a in addresses if a.is_visit_address]
        assert len(visit_addrs) == 1
