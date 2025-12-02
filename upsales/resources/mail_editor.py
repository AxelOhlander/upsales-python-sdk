"""Mail Editor authentication resource for Upsales API.

Provides authentication for BEE mail editor service integration.

Example:
    ```python
    async with Upsales(token="...") as upsales:
        token = await upsales.mail_editor.authenticate()
        print(f"BEE Token: {token.access_token}")
    ```
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from upsales.models.mail_editor import MailEditorToken

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class MailEditorResource:
    """Resource manager for BEE Mail Editor authentication.

    This resource provides authentication with the BEE mail editor service,
    returning an OAuth-style access token for use in editor API requests.

    Example:
        ```python
        resource = MailEditorResource(http_client)
        token = await resource.authenticate()
        print(f"Token expires in: {token.expires_in} seconds")
        ```
    """

    def __init__(self, http: HTTPClient):
        """Initialize mail editor authentication resource.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/function/mailEditor"

    async def authenticate(self) -> MailEditorToken:
        """Authenticate with BEE mail editor service.

        Returns an access token for authenticating requests to the BEE mail
        editor API. The token is typically valid for a limited time as specified
        in the expires_in field.

        Returns:
            MailEditorToken with access_token, token_type, and expires_in.

        Raises:
            AuthenticationError: If authentication fails (401/403).
            ServerError: If server error occurs (500+).
            UpsalesError: For other API errors.

        Example:
            ```python
            token = await upsales.mail_editor.authenticate()
            # Use token.access_token for BEE API requests
            headers = {"Authorization": f"Bearer {token.access_token}"}
            ```
        """
        response = await self._http.request("POST", self._endpoint)
        return MailEditorToken.model_validate(response["data"])
