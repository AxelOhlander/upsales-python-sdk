"""Account manager history resource for Upsales API.

Manages historical account manager assignments on specific dates.

Example:
    ```python
    async with Upsales(token="...") as upsales:
        # Set account manager for a past date
        await upsales.account_manager_history.set_history(
            client_id=100, date="2025-01-15", user_ids=[42]
        )

        # Change account manager on a specific agreement
        await upsales.account_manager_history.set_specific(
            agreement_id=500, client_id=100, user_id=42
        )
    ```
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class AccountManagerHistoryResource:
    """Resource manager for account manager history.

    Two endpoints:
    - /function/accountManagerHistory — set AM for a client on a past date
    - /function/accountManagerHistory/specific — set AM on a specific agreement

    Example:
        ```python
        resource = AccountManagerHistoryResource(http_client)
        await resource.set_history(client_id=100, date="2025-01-15", user_ids=[42])
        ```
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize account manager history resource.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http

    async def set_history(
        self,
        client_id: int,
        date: str,
        user_ids: list[int] | None = None,
    ) -> dict[str, Any]:
        """Set account manager for a client on a historical date.

        The date must be in the past. This updates who was the account
        manager on that specific date and recalculates ARR.

        Args:
            client_id: The client/account ID.
            date: Historical date in YYYY-MM-DD format (must be past).
            user_ids: User IDs to set as account managers. Defaults to [0] (none).

        Returns:
            API response data.

        Example:
            ```python
            await upsales.account_manager_history.set_history(
                client_id=100, date="2025-01-15", user_ids=[42, 43]
            )
            ```
        """
        params: dict[str, Any] = {"clientId": client_id, "date": date}
        if user_ids is not None:
            params["userIds"] = user_ids
        return await self._http.put(
            "/function/accountManagerHistory",
            **params,
        )

    async def set_specific(
        self,
        agreement_id: int,
        client_id: int,
        user_id: int,
    ) -> dict[str, Any]:
        """Set account manager on a specific agreement.

        Args:
            agreement_id: The agreement ID.
            client_id: The client/account ID.
            user_id: The user ID to assign. Use 0 to clear.

        Returns:
            API response data.

        Example:
            ```python
            await upsales.account_manager_history.set_specific(
                agreement_id=500, client_id=100, user_id=42
            )
            ```
        """
        return await self._http.put(
            "/function/accountManagerHistory/specific",
            agreementId=agreement_id,
            clientId=client_id,
            userId=user_id,
        )
