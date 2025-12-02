"""Mail Editor authentication models for Upsales API.

This module provides models for authenticating with the BEE mail editor service.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class MailEditorToken(BaseModel):
    """Authentication token response from BEE mail editor service.

    This model represents the OAuth-style token response returned when
    authenticating with the BEE mail editor integration.

    Attributes:
        access_token: The bearer token for authenticating API requests.
        token_type: Type of token, typically "Bearer".
        expires_in: Token expiration time in seconds.

    Example:
        ```python
        token = await upsales.mail_editor.authenticate()
        print(f"Token: {token.access_token}")
        print(f"Expires in: {token.expires_in} seconds")
        ```
    """

    access_token: str = Field(description="Bearer token for API authentication")
    token_type: str = Field(description="Token type (typically 'Bearer')")
    expires_in: int = Field(description="Token expiration time in seconds")
