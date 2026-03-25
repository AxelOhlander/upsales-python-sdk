"""
AddressList - Smart collection for company addresses.

Provides convenient property access for address types while maintaining
list-like behavior for iteration and indexing.
"""

from __future__ import annotations

from collections.abc import Iterator

from upsales.models.address import Address


class AddressList:
    """
    Smart collection for company addresses.

    Provides both list-like access and convenient property accessors
    for specific address types (mail, visit, postal, billing, delivery).

    This class wraps a list of Address objects and provides:
    - List-like iteration: `for addr in company.addresses`
    - Indexing: `company.addresses[0]`
    - Length: `len(company.addresses)`
    - Type-specific access: `company.addresses.mail`

    Example:
        ```python
        company = await upsales.companies.get(1)

        # Property access for specific types
        if company.addresses.mail:
            print(f"Mail to: {company.addresses.mail.full_address}")

        if company.addresses.visit:
            print(f"Visit: {company.addresses.visit.city}")

        # List-like iteration
        for addr in company.addresses:
            print(f"{addr.type}: {addr.city}")

        # Indexing
        first = company.addresses[0]

        # Length
        count = len(company.addresses)

        # Get all of a type
        all_postal = [a for a in company.addresses if a.type == "Postal"]
        ```

    Note:
        The API returns mailAddress as a separate field, but AddressList
        automatically merges it into the addresses list for unified access.
    """

    def __init__(self, addresses: list[Address] | None = None):
        """
        Initialize AddressList.

        Args:
            addresses: List of Address objects.
        """
        self._addresses: list[Address] = addresses or []

    @property
    def mail(self) -> Address | None:
        """
        Get the mail/mailing address.

        Returns:
            Mail address if exists, None otherwise.

        Example:
            ```python
            if company.addresses.mail:
                print(company.addresses.mail.full_address)
            ```
        """
        return next((a for a in self._addresses if a.type == "Mail"), None)

    @property
    def visit(self) -> Address | None:
        """
        Get the visit/visiting address.

        Returns:
            Visit address if exists, None otherwise.

        Example:
            ```python
            if company.addresses.visit:
                print(f"Visit us at: {company.addresses.visit.city}")
            ```
        """
        return next((a for a in self._addresses if a.type == "Visit"), None)

    @property
    def postal(self) -> Address | None:
        """
        Get the postal address.

        Returns:
            Postal address if exists, None otherwise.

        Example:
            ```python
            if company.addresses.postal:
                print(f"PO Box: {company.addresses.postal.address}")
            ```
        """
        return next((a for a in self._addresses if a.type == "Postal"), None)

    @property
    def billing(self) -> Address | None:
        """
        Get the billing address.

        Returns:
            Billing address if exists, None otherwise.

        Example:
            ```python
            if company.addresses.billing:
                print(f"Bill to: {company.addresses.billing.full_address}")
            ```
        """
        return next((a for a in self._addresses if a.type == "Billing"), None)

    @property
    def delivery(self) -> Address | None:
        """
        Get the delivery address.

        Returns:
            Delivery address if exists, None otherwise.

        Example:
            ```python
            if company.addresses.delivery:
                print(f"Ship to: {company.addresses.delivery.full_address}")
            ```
        """
        return next((a for a in self._addresses if a.type == "Delivery"), None)

    def get_by_type(self, address_type: str) -> Address | None:
        """
        Get address by type string.

        Args:
            address_type: Type to find (case-insensitive).

        Returns:
            Address of specified type if exists, None otherwise.

        Example:
            ```python
            mail = company.addresses.get_by_type("mail")
            visit = company.addresses.get_by_type("Visit")
            ```
        """
        return next(
            (a for a in self._addresses if a.type is not None and a.type.lower() == address_type.lower()),
            None,
        )

    def filter_by_country(self, country: str) -> list[Address]:
        """
        Filter addresses by country code.

        Args:
            country: ISO country code (e.g., "SE", "US").

        Returns:
            List of addresses in the specified country.

        Example:
            ```python
            us_addresses = company.addresses.filter_by_country("US")
            ```
        """
        return [a for a in self._addresses if a.country == country]

    def all(self) -> list[Address]:
        """
        Get all addresses as a list.

        Returns:
            List of all Address objects.

        Example:
            ```python
            all_addrs = company.addresses.all()
            print(f"Total: {len(all_addrs)}")
            ```
        """
        return self._addresses.copy()

    # List-like behavior
    def __iter__(self) -> Iterator[Address]:
        """Iterate over addresses."""
        return iter(self._addresses)

    def __len__(self) -> int:
        """Get number of addresses."""
        return len(self._addresses)

    def __getitem__(self, index: int) -> Address:
        """Get address by index."""
        return self._addresses[index]

    def __bool__(self) -> bool:
        """Check if any addresses exist."""
        return bool(self._addresses)

    def __repr__(self) -> str:
        """String representation."""
        return f"<AddressList count={len(self._addresses)}>"
