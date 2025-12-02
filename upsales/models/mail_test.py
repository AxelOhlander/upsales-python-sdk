"""Mail Test models for Upsales API.

This module provides models for sending test emails via the mail test endpoint.
"""

from __future__ import annotations

from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict, Field


class MailTestSendFields(dict[str, int | str]):
    """Fields for sending a test email.

    This is a type annotation helper for documentation purposes.

    Required fields:
        client: Company ID
        contact: Contact ID

    Optional fields:
        subject: Email subject
        body: Email body content
        to: Recipient email address
        from_address: Sender email address (API uses 'from')
        from_name: Sender display name
    """

    client: int
    contact: int
    subject: str | None
    body: str | None
    to: str | None
    from_address: str | None
    from_name: str | None


class MailTestResponse(PydanticBaseModel):
    """Response from sending a test email.

    This is a simple response model that doesn't require an ID field.
    Unlike standard CRUD models, this inherits directly from Pydantic's BaseModel.

    Attributes:
        success: Whether the test email was sent successfully
        message: Optional response message from the API

    Example:
        >>> response = MailTestResponse(success=True)
        >>> print(response.success)
        True
    """

    success: bool = Field(default=True, description="Whether the test email was sent successfully")
    message: str | None = Field(None, description="Response message from API")

    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="allow",  # Allow extra fields from API response
    )
