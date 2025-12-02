"""
Mail domain models for email domain verification.

This module provides models for managing email domain verification in Upsales,
including DNS validation and domain status tracking.

Example:
    >>> domain = MailDomain(domain="example.com", dns="valid", valid=1)
    >>> if domain.is_valid:
    ...     print(f"Domain {domain.domain} is verified")
"""

from typing import TypedDict, Unpack

from pydantic import Field, computed_field

from upsales.models.base import BaseModel, PartialModel
from upsales.validators import BinaryFlag


class MailDomainUpdateFields(TypedDict, total=False):
    """
    Available fields for updating a MailDomain.

    Note:
        Mail domains are primarily managed through DNS verification.
        Direct updates may be limited based on mail account configuration.

    Attributes:
        domain: Domain name (lowercase)
        dns: DNS configuration status
        valid: Validation status (0=invalid, 1=valid)
        msg: Validation message
    """

    domain: str
    dns: str
    valid: int
    msg: str


class MailDomain(BaseModel):
    """
    Mail domain model for email domain verification.

    Represents an email domain configured in Upsales for sending emails.
    Domains must be verified through DNS records before they can be used.

    Attributes:
        domain: Domain name (e.g., "example.com")
        dns: DNS configuration status
        valid: Whether domain is verified (0=no, 1=yes)
        msg: Validation status message

    Example:
        >>> async with Upsales.from_env() as client:
        ...     domain = await client.mail_domains.create(domain="example.com")
        ...     if domain.is_valid:
        ...         print(f"Domain {domain.domain} is ready to use")
        ...     else:
        ...         print(f"DNS setup required: {domain.msg}")
    """

    id: int = Field(
        default=0,
        frozen=True,
        description="Placeholder numeric ID for compatibility with base models",
    )
    domain: str = Field(description="Domain name (lowercase)")
    dns: str = Field(description="DNS configuration status")
    valid: BinaryFlag = Field(
        default=0, description="Domain validation status (0=invalid, 1=valid)"
    )
    msg: str | None = Field(None, description="Validation message or error details")

    @computed_field
    @property
    def is_valid(self) -> bool:
        """
        Check if domain is verified and ready to use.

        Returns:
            True if domain has been verified through DNS records.

        Example:
            >>> if domain.is_valid:
            ...     print("Domain is verified")
        """
        return self.valid == 1

    async def edit(self, **kwargs: Unpack[MailDomainUpdateFields]) -> "MailDomain":
        """
        Edit this mail domain.

        Note:
            Direct domain updates may be limited. Most changes require DNS
            reconfiguration and re-verification.

        Args:
            **kwargs: Fields to update (from MailDomainUpdateFields)

        Returns:
            Updated MailDomain instance with changes applied.

        Raises:
            RuntimeError: If no client available (shouldn't happen in practice).
            ValidationError: If provided data is invalid.
            PermissionError: If user lacks administrator permissions.

        Example:
            >>> domain = await client.mail_domains.get("example.com")
            >>> updated = await domain.edit(msg="Updated validation message")
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.mail_domains.update(self.domain, **self.to_api_dict(**kwargs))


class PartialMailDomain(PartialModel):
    """
    Partial mail domain model for nested references.

    Used when mail domain data appears as a nested object in other resources.
    Contains minimal fields for identification and display.

    Attributes:
        domain: Domain name
        valid: Domain validation status

    Example:
        >>> # When a campaign includes domain reference
        >>> campaign = await client.mail_campaigns.get(123)
        >>> if campaign.domain:
        ...     full_domain = await campaign.domain.fetch_full()
    """

    domain: str = Field(description="Domain name")
    valid: BinaryFlag = Field(default=0, description="Domain validation status")

    async def fetch_full(self) -> MailDomain:
        """
        Fetch complete mail domain data.

        Returns:
            Full MailDomain instance with all fields populated.

        Raises:
            RuntimeError: If no client available.
            NotFoundError: If domain doesn't exist.

        Example:
            >>> partial = PartialMailDomain(domain="example.com", valid=1)
            >>> full = await partial.fetch_full()
            >>> print(full.dns)  # Access DNS configuration
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.mail_domains.get(self.domain)

    async def edit(self, **kwargs: Unpack[MailDomainUpdateFields]) -> MailDomain:
        """
        Edit this mail domain and return full updated instance.

        Args:
            **kwargs: Fields to update (from MailDomainUpdateFields)

        Returns:
            Full updated MailDomain instance.

        Raises:
            RuntimeError: If no client available.
            ValidationError: If provided data is invalid.
            PermissionError: If user lacks administrator permissions.

        Example:
            >>> partial = PartialMailDomain(domain="example.com", valid=1)
            >>> updated = await partial.edit(msg="New status")
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.mail_domains.update(self.domain, **kwargs)
