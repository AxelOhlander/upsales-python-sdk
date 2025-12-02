"""Mail test resource manager for Upsales API.

This module provides methods to send test emails via the mail test endpoint.
Note: This endpoint only supports POST operations (no GET/PUT/DELETE).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from upsales.exceptions import ValidationError

if TYPE_CHECKING:
    from upsales.http import HTTPClient
    from upsales.models.mail_test import MailTestResponse


class MailTestResource:
    """Resource manager for mail test endpoint.

    This is a special-purpose resource that only supports sending test emails.
    Unlike standard CRUD resources, it does not support get, list, update, or delete operations.

    Example:
        >>> async with Upsales(token="...") as upsales:
        ...     response = await upsales.mail_test.send(
        ...         client=123,
        ...         contact=456,
        ...         subject="Test Email",
        ...         body="This is a test",
        ...         to="recipient@example.com"
        ...     )
        ...     print(response.success)
    """

    def __init__(self, http: HTTPClient):
        """Initialize mail test resource manager.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/mail/test"

    async def send(
        self,
        client: int,
        contact: int,
        subject: str | None = None,
        body: str | None = None,
        to: str | None = None,
        from_address: str | None = None,
        from_name: str | None = None,
    ) -> MailTestResponse:
        """Send a test email.

        Args:
            client: Company ID (required)
            contact: Contact ID (required)
            subject: Email subject line (optional)
            body: Email body content (optional)
            to: Recipient email address (optional)
            from_address: Sender email address (optional, API field is 'from')
            from_name: Sender display name (optional)

        Returns:
            Response object with success status

        Raises:
            ValidationError: If required fields are missing or invalid
            UpsalesError: If the API request fails

        Example:
            >>> response = await upsales.mail_test.send(
            ...     client=123,
            ...     contact=456,
            ...     subject="Welcome!",
            ...     body="Thanks for signing up",
            ...     to="user@example.com",
            ...     from_address="noreply@company.com",
            ...     from_name="Company Name"
            ... )
            >>> assert response.success is True
        """
        if not client or not contact:
            raise ValidationError("Both 'client' and 'contact' are required")

        # Build payload
        payload: dict[str, int | str] = {
            "client": client,
            "contact": contact,
        }

        # Add optional fields
        if subject is not None:
            payload["subject"] = subject
        if body is not None:
            payload["body"] = body
        if to is not None:
            payload["to"] = to
        if from_address is not None:
            payload["from"] = from_address  # API uses 'from' not 'from_address'
        if from_name is not None:
            payload["fromName"] = from_name

        # Import here to avoid circular imports
        from upsales.models.mail_test import MailTestResponse

        # Send test email
        response = await self._http.request("POST", self._endpoint, json=payload)

        # Parse response - API may return various formats
        if isinstance(response, dict):
            return MailTestResponse(**response)
        else:
            # If response is not a dict, assume success
            return MailTestResponse(success=True, message=str(response))
