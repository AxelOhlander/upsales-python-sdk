"""System mail resource for sending predefined template emails.

This module provides the resource manager for the systemMail endpoint,
which is a POST-only function endpoint for sending system emails.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from upsales.http import HTTPClient
    from upsales.models.system_mail import SystemMailResponse


class SystemMailResource:
    """Resource manager for system mail operations.

    This resource provides methods for sending system emails using predefined
    templates. Unlike standard CRUD resources, this is a function endpoint that
    only supports POST operations.

    The endpoint supports three predefined templates:
    - installingScript: Send installation script instructions
    - verifyDomains: Send domain verification requests
    - requestAddon: Send addon requests

    Attributes:
        http: HTTP client for making API requests
        endpoint: API endpoint path

    Example:
        >>> # Send verification email
        >>> response = await upsales.system_mail.send(
        ...     template_name="verifyDomains",
        ...     email="admin@example.com",
        ...     additional={"domain": "example.com"}
        ... )
        >>> print(response.success)
        True

        >>> # Send to multiple recipients
        >>> response = await upsales.system_mail.send(
        ...     template_name="requestAddon",
        ...     email=["admin@example.com", "support@example.com"],
        ...     additional={"addon": "advanced-reporting"}
        ... )
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize the system mail resource.

        Args:
            http: HTTP client instance for making API requests
        """
        self.http = http
        self.endpoint = "/function/system-mail"

    async def send(
        self,
        template_name: Literal["installingScript", "verifyDomains", "requestAddon"],
        email: str | list[str],
        additional: dict[str, Any] | None = None,
    ) -> SystemMailResponse:
        """Send a system email using a predefined template.

        Args:
            template_name: Name of the predefined template to use
            email: Single email address or list of email addresses
            additional: Optional additional data to pass to the template

        Returns:
            Response indicating success or failure

        Raises:
            ValidationError: If the email format is invalid or template_name is not valid
            ServerError: If the API request fails

        Example:
            >>> # Send single email
            >>> response = await upsales.system_mail.send(
            ...     template_name="verifyDomains",
            ...     email="admin@example.com",
            ...     additional={"domain": "example.com"}
            ... )

            >>> # Send to multiple recipients
            >>> response = await upsales.system_mail.send(
            ...     template_name="installingScript",
            ...     email=["user1@example.com", "user2@example.com"]
            ... )
        """
        from upsales.models.system_mail import SystemMailResponse

        payload: dict[str, Any] = {
            "templateName": template_name,
            "email": email,
        }

        if additional is not None:
            payload["additional"] = additional

        response_data = await self.http.post(self.endpoint, json=payload)
        return SystemMailResponse.model_validate(response_data["data"])


__all__ = ["SystemMailResource"]
