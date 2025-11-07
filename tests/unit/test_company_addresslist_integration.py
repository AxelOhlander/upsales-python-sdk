"""
Integration tests for Company model with AddressList.

Tests the automatic merging of mailAddress into the addresses collection
and the convenient property access pattern.
"""

import pytest

from upsales.models.address import Address
from upsales.models.address_list import AddressList
from upsales.models.company import Company


class TestCompanyAddressListIntegration:
    """Test Company model integration with AddressList."""

    def test_create_company_with_addresses(self):
        """Test creating company with AddressList."""
        company = Company(
            id=1,
            name="ACME Corp",
            addresses=AddressList([
                Address(type="Visit", address="Main St 1", city="Stockholm", country="SE"),
                Address(type="Mail", address="Box 123", city="Stockholm", country="SE"),
            ]),
        )

        assert isinstance(company.addresses, AddressList)
        assert len(company.addresses) == 2
        assert company.addresses.visit is not None
        assert company.addresses.mail is not None

    def test_mailaddress_merged_into_addresses(self):
        """Test that mailAddress is automatically merged into addresses list."""
        company = Company(
            id=1,
            name="ACME Corp",
            addresses=AddressList([
                Address(type="Visit", address="Main St 1", city="Stockholm", country="SE"),
            ]),
            mailAddress=Address(type="Mail", address="Box 123", city="Stockholm", country="SE"),
        )

        # After model_validator, mailAddress should be merged
        assert len(company.addresses) == 2
        assert company.addresses.mail is not None
        assert company.addresses.mail.address == "Box 123"
        assert company.addresses.visit is not None

    def test_property_access_mail(self):
        """Test accessing mail address via property."""
        company = Company(
            id=1,
            name="ACME Corp",
            addresses=AddressList([
                Address(type="Mail", address="Box 456", city="Malmö", country="SE"),
            ]),
        )

        mail = company.addresses.mail
        assert mail is not None
        assert mail.address == "Box 456"
        assert mail.city == "Malmö"

    def test_property_access_visit(self):
        """Test accessing visit address via property."""
        company = Company(
            id=1,
            name="ACME Corp",
            addresses=AddressList([
                Address(type="Visit", address="Office Plaza", city="Göteborg", country="SE"),
            ]),
        )

        visit = company.addresses.visit
        assert visit is not None
        assert visit.address == "Office Plaza"

    def test_all_five_address_types(self):
        """Test company with all 5 address types."""
        company = Company(
            id=1,
            name="ACME Corp",
            addresses=AddressList([
                Address(type="Mail", address="Box 1", city="City1", country="SE"),
                Address(type="Visit", address="St 2", city="City2", country="SE"),
                Address(type="Postal", address="PO 3", city="City3", country="SE"),
                Address(type="Billing", address="Invoice 4", city="City4", country="SE"),
                Address(type="Delivery", address="Warehouse 5", city="City5", country="SE"),
            ]),
        )

        assert company.addresses.mail.address == "Box 1"
        assert company.addresses.visit.address == "St 2"
        assert company.addresses.postal.address == "PO 3"
        assert company.addresses.billing.address == "Invoice 4"
        assert company.addresses.delivery.address == "Warehouse 5"

    def test_iteration_over_company_addresses(self):
        """Test iterating addresses on company."""
        company = Company(
            id=1,
            name="ACME Corp",
            addresses=AddressList([
                Address(type="Visit", address="St 1", city="City1", country="SE"),
                Address(type="Mail", address="Box 2", city="City2", country="SE"),
            ]),
        )

        cities = [addr.city for addr in company.addresses]
        assert "City1" in cities
        assert "City2" in cities

    def test_company_with_no_addresses(self):
        """Test company with empty addresses."""
        company = Company(id=1, name="ACME Corp")

        assert isinstance(company.addresses, AddressList)
        assert len(company.addresses) == 0
        assert company.addresses.mail is None
        assert company.addresses.visit is None

    def test_filter_company_addresses_by_country(self):
        """Test filtering company addresses."""
        company = Company(
            id=1,
            name="ACME Corp",
            addresses=AddressList([
                Address(type="Visit", address="5th Ave", city="New York", country="US"),
                Address(type="Mail", address="Box 1", city="Stockholm", country="SE"),
                Address(type="Billing", address="Main St", city="Malmö", country="SE"),
            ]),
        )

        se_addresses = company.addresses.filter_by_country("SE")
        assert len(se_addresses) == 2
        assert all(a.country == "SE" for a in se_addresses)

    def test_get_address_by_type_method(self):
        """Test getting address by type string."""
        company = Company(
            id=1,
            name="ACME Corp",
            addresses=AddressList([
                Address(type="Visit", address="Main", city="City", country="SE"),
            ]),
        )

        visit = company.addresses.get_by_type("visit")
        assert visit is not None
        assert visit.type == "Visit"

        mail = company.addresses.get_by_type("mail")
        assert mail is None
