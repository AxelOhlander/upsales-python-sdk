"""Send e-sign reminder resource for Upsales API.

Sends reminders for pending e-signature documents.

Example:
    ```python
    async with Upsales(token="...") as upsales:
        result = await upsales.send_esign_reminder.send(esign_id=123)
    ```
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class SendEsignReminderResource:
    """Resource manager for sending e-sign reminders.

    Function endpoint at /function/sendEsignReminder/:id.

    Example:
        ```python
        resource = SendEsignReminderResource(http_client)
        result = await resource.send(esign_id=123)
        ```
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize send e-sign reminder resource.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/function/sendEsignReminder"

    async def send(self, esign_id: int) -> dict[str, Any]:
        """Send a reminder for a pending e-sign document.

        Args:
            esign_id: The e-sign document ID.

        Returns:
            Updated Esign object data.

        Raises:
            NotFoundError: If the e-sign document is not found.

        Example:
            ```python
            result = await upsales.send_esign_reminder.send(esign_id=123)
            ```
        """
        return await self._http.put(f"{self._endpoint}/{esign_id}")
