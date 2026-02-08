"""Assign resource for Upsales API.

Manages user assignment to client accounts (companies).

Example:
    ```python
    async with Upsales(token="...") as upsales:
        # Assign user 42 to company 100
        await upsales.assign.assign_user(client_id=100, user_id=42)

        # Get assigned user for a company
        user = await upsales.assign.get(client_id=100)

        # Remove assignment
        await upsales.assign.remove(client_id=100)
    ```
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class AssignResource:
    """Resource manager for user-to-company assignment.

    The assign endpoint manages which user is assigned to a client account.
    This is a function endpoint at /function/assign.

    Example:
        ```python
        resource = AssignResource(http_client)
        await resource.assign_user(client_id=100, user_id=42)
        ```
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize assign resource.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/function/assign"

    async def get(self, client_id: int) -> dict[str, Any]:
        """Get the assigned user for a client.

        Args:
            client_id: The client/account ID.

        Returns:
            User data dict (id, name, email) or empty if unassigned.

        Example:
            ```python
            user = await upsales.assign.get(client_id=100)
            print(user["name"])
            ```
        """
        return await self._http.get(f"{self._endpoint}/{client_id}")

    async def assign_user(self, client_id: int, user_id: int) -> dict[str, Any]:
        """Assign a user to a client account.

        Args:
            client_id: The client/account ID.
            user_id: The user ID to assign.

        Returns:
            API response data.

        Example:
            ```python
            await upsales.assign.assign_user(client_id=100, user_id=42)
            ```
        """
        return await self._http.put(
            f"{self._endpoint}/{client_id}",
            id=client_id,
            userId=user_id,
        )

    async def remove(self, client_id: int) -> dict[str, Any]:
        """Remove user assignment from a client.

        Args:
            client_id: The client/account ID.

        Returns:
            API response data.

        Example:
            ```python
            await upsales.assign.remove(client_id=100)
            ```
        """
        return await self._http.delete(f"{self._endpoint}/{client_id}")
