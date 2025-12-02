"""
Mail domains resource manager for Upsales API.

Provides methods to interact with the /api/v2/mail/domains endpoint.
Handles email domain verification and DNS configuration.

Note:
    Requires mail account configuration. Operations require administrator permissions.

Example:
    >>> async with Upsales.from_env() as upsales:
    ...     # Create a new domain
    ...     domain = await upsales.mail_domains.create(domain="example.com")
    ...     # List all domains
    ...     domains = await upsales.mail_domains.list()
    ...     # Get domain by name
    ...     domain = await upsales.mail_domains.get("example.com")
"""

from typing import Any

from upsales.http import HTTPClient
from upsales.models.mail_domains import MailDomain, PartialMailDomain
from upsales.resources.base import BaseResource


class MailDomainsResource(BaseResource[MailDomain, PartialMailDomain]):
    """
    Resource manager for mail domain verification.

    Manages email domains for sending campaigns. Domains must be verified
    through DNS records before use. Requires administrator permissions.

    Inherits standard CRUD operations from BaseResource:
    - create(domain) - Register new domain for verification
    - get(domain) - Get single domain by name
    - list(limit, offset, **params) - List domains with pagination
    - list_all(**params) - Auto-paginated list of all domains
    - delete(domain) - Remove domain (Halon accounts only)

    Note:
        Unlike most resources, mail domains use domain name as identifier
        instead of numeric ID.

    Example:
        >>> resource = MailDomainsResource(http_client)
        >>> domain = await resource.create(domain="example.com")
        >>> print(f"DNS Status: {domain.dns}")
        >>> print(f"Valid: {domain.is_valid}")
    """

    def __init__(self, http: HTTPClient):
        """
        Initialize mail domains resource manager.

        Args:
            http: HTTP client for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/mail/domains",
            model_class=MailDomain,
            partial_class=PartialMailDomain,
        )

    async def get(self, domain_name: str) -> MailDomain:  # type: ignore[override]
        """
        Get a mail domain by name.

        Note:
            Unlike most resources, mail domains use domain name as identifier
            instead of numeric ID.

        Args:
            domain_name: Domain name (e.g., "example.com")

        Returns:
            MailDomain instance for the specified domain.

        Raises:
            NotFoundError: If domain doesn't exist.
            AuthenticationError: If authentication fails.

        Example:
            >>> domain = await client.mail_domains.get("example.com")
            >>> print(f"Valid: {domain.is_valid}, DNS: {domain.dns}")
        """
        response = await self._http.get(f"{self._endpoint}/{domain_name}")
        return self._model_class(**response["data"], _client=self._http._upsales_client)

    async def update(self, domain_name: str, **data: Any) -> MailDomain:  # type: ignore[override]
        """
        Update a mail domain.

        Args:
            domain_name: Domain name (e.g., "example.com")
            **data: Fields to update

        Returns:
            Updated MailDomain instance.

        Raises:
            NotFoundError: If domain doesn't exist.
            ValidationError: If provided data is invalid.
            PermissionError: If user lacks administrator permissions.

        Example:
            >>> domain = await client.mail_domains.update(
            ...     "example.com",
            ...     msg="Updated validation message"
            ... )
        """
        response = await self._http.put(f"{self._endpoint}/{domain_name}", json=data)
        return self._model_class(**response["data"], _client=self._http._upsales_client)

    async def delete(self, domain_name: str) -> None:  # type: ignore[override]
        """
        Delete a mail domain.

        Note:
            Only works with Halon mail accounts. Requires administrator permissions.

        Args:
            domain_name: Domain name to delete (e.g., "example.com")

        Raises:
            NotFoundError: If domain doesn't exist.
            PermissionError: If user lacks administrator permissions or wrong mail account type.

        Example:
            >>> await client.mail_domains.delete("example.com")
        """
        await self._http.delete(f"{self._endpoint}/{domain_name}")

    async def get_verified(self) -> list[MailDomain]:
        """
        Get all verified mail domains.

        Returns:
            List of domains with valid DNS configuration.

        Example:
            >>> verified = await upsales.mail_domains.get_verified()
            >>> for domain in verified:
            ...     print(f"{domain.domain} is ready to use")
        """
        all_domains: list[MailDomain] = await self.list_all()
        return [d for d in all_domains if d.is_valid]

    async def get_by_name(self, domain_name: str) -> MailDomain:
        """
        Get domain by name.

        Convenience method that's more descriptive than generic get().

        Args:
            domain_name: Domain name (e.g., "example.com")

        Returns:
            MailDomain instance for the specified domain.

        Raises:
            NotFoundError: If domain not found.

        Example:
            >>> domain = await upsales.mail_domains.get_by_name("example.com")
        """
        return await self.get(domain_name)
