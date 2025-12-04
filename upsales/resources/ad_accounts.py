"""Ad accounts resource manager for Upsales API.

This module provides the resource manager for advertising account operations.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from upsales.models.ad_accounts import AdAccount, PartialAdAccount
from upsales.resources.base import BaseResource

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class AdAccountsResource(BaseResource[AdAccount, PartialAdAccount]):
    """Resource manager for advertising accounts.

    This resource handles operations for advertising account configuration
    per customer. Note that this endpoint uses a special path structure
    with customer ID: /api/v2/:customerId/engage/account

    Example:
        >>> async with Upsales.from_env() as client:
        ...     # Get account for customer
        ...     account = await client.ad_accounts.get(customer_id=123)
        ...     print(account.cpmAmount)
        ...
        ...     # Update account
        ...     updated = await client.ad_accounts.update(
        ...         customer_id=123,
        ...         cpmAmount=400.0
        ...     )
        ...
        ...     # Create account for customer
        ...     new_account = await client.ad_accounts.create(
        ...         customer_id=123,
        ...         cpmAmount=350.0,
        ...         active=True
        ...     )
    """

    def __init__(self, http: HTTPClient):
        """Initialize the ad accounts resource manager.

        Args:
            http: HTTP client instance for making API requests.
        """
        # Note: Base path is special for this endpoint
        super().__init__(
            http=http,
            endpoint="/:customerId/engage/account",
            model_class=AdAccount,
            partial_class=PartialAdAccount,
        )

    async def get(self, customer_id: int) -> AdAccount:
        """Get advertising account for a specific customer.

        Args:
            customer_id: The customer ID to get account for.

        Returns:
            AdAccount instance for the customer.

        Raises:
            NotFoundError: If account doesn't exist for customer.
            AuthenticationError: If authentication fails.

        Example:
            >>> account = await client.ad_accounts.get(customer_id=123)
            >>> print(account.cpmAmount)
            300.0
        """
        endpoint = f"/{customer_id}/engage/account"
        response = await self._http.get(endpoint)
        account = self._model_class.model_validate(response["data"])
        account._client = self._http._upsales_client  # type: ignore[attr-defined]
        return account

    async def create(self, customer_id: int, **data: object) -> AdAccount:  # type: ignore[override]
        """Create advertising account for a customer.

        Args:
            customer_id: The customer ID to create account for.
            **data: Account data (cpmAmount, active).

        Returns:
            Created AdAccount instance.

        Raises:
            ValidationError: If data validation fails.
            AuthenticationError: If authentication fails.

        Example:
            >>> account = await client.ad_accounts.create(
            ...     customer_id=123,
            ...     cpmAmount=350.0,
            ...     active=True
            ... )
            >>> print(account.cpmAmount)
            350.0
        """
        endpoint = f"/{customer_id}/engage/account"
        response = await self._http.post(endpoint, data=data)
        account = self._model_class.model_validate(response["data"])
        account._client = self._http._upsales_client  # type: ignore[attr-defined]
        return account

    async def update(self, customer_id: int, **data: object) -> AdAccount:  # type: ignore[override]
        """Update advertising account for a customer.

        Args:
            customer_id: The customer ID to update account for.
            **data: Account data to update (cpmAmount, active).

        Returns:
            Updated AdAccount instance.

        Raises:
            NotFoundError: If account doesn't exist for customer.
            ValidationError: If data validation fails.
            AuthenticationError: If authentication fails.

        Example:
            >>> account = await client.ad_accounts.update(
            ...     customer_id=123,
            ...     cpmAmount=400.0
            ... )
            >>> print(account.cpmAmount)
            400.0
        """
        endpoint = f"/{customer_id}/engage/account"
        response = await self._http.put(endpoint, data=data)
        account = self._model_class.model_validate(response["data"])
        account._client = self._http._upsales_client  # type: ignore[attr-defined]
        return account

    async def delete(self, customer_id: int) -> dict[str, object]:  # type: ignore[override]
        """Delete advertising account for a customer.

        Args:
            customer_id: The customer ID to delete account for.

        Raises:
            NotFoundError: If account doesn't exist for customer.
            AuthenticationError: If authentication fails.

        Example:
            >>> await client.ad_accounts.delete(customer_id=123)
        """
        endpoint = f"/{customer_id}/engage/account"
        return await self._http.delete(endpoint)
