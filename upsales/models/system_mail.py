"""System mail models for sending predefined template emails.

This module provides models for the systemMail endpoint, which is used
to send system emails from predefined templates.
"""

from __future__ import annotations

from typing import Any, Literal, TypedDict

from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field, field_validator


class SystemMailCreateFields(TypedDict, total=False):
    """Available fields for creating a system mail request.

    All fields are required for the POST request.
    """

    templateName: Literal["installingScript", "verifyDomains", "requestAddon"]
    email: str | list[str]
    additional: dict[str, Any]


class SystemMailResponse(PydanticBaseModel):
    """Response from sending a system mail.

    This model represents the response after successfully sending
    a system email using a predefined template.

    Attributes:
        success: Whether the email was sent successfully
        message: Response message from the API
    """

    success: bool = Field(description="Whether the email was sent successfully")
    message: str | None = Field(None, description="Response message from the API")

    model_config = {
        "json_schema_extra": {"example": {"success": True, "message": "Email sent successfully"}}
    }


class SystemMailRequest(PydanticBaseModel):
    """Request model for sending system mail.

    This model represents a request to send a system email using one of
    the predefined templates: installingScript, verifyDomains, or requestAddon.

    Attributes:
        templateName: Name of the predefined template to use
        email: Single email address or list of email addresses
        additional: Optional additional data to pass to the template

    Example:
        >>> request = SystemMailRequest(
        ...     templateName="verifyDomains",
        ...     email="admin@example.com",
        ...     additional={"domain": "example.com"}
        ... )
        >>> # Send via resource: await upsales.system_mail.send(request)
    """

    templateName: Literal["installingScript", "verifyDomains", "requestAddon"] = Field(
        description="Name of the predefined template to use"
    )
    email: str | list[str] = Field(description="Single email address or list of email addresses")
    additional: dict[str, Any] | None = Field(
        None, description="Optional additional data to pass to the template"
    )

    @field_validator("email", mode="before")
    @classmethod
    def validate_email(cls, v: str | list[str]) -> str | list[str]:
        """Validate email address(es).

        Args:
            v: Email address or list of email addresses

        Returns:
            Validated email address(es)

        Raises:
            ValueError: If email format is invalid
        """
        import re

        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

        if isinstance(v, str):
            # Validate single email
            if not re.match(email_pattern, v):
                raise ValueError(f"Invalid email format: {v}")
            return v
        elif isinstance(v, list):
            # Validate list of emails
            for email in v:
                if not isinstance(email, str):
                    raise ValueError(f"Email must be string, got {type(email)}")
                if not re.match(email_pattern, email):
                    raise ValueError(f"Invalid email format: {email}")
            return v
        else:
            raise ValueError(f"Email must be string or list[str], got {type(v)}")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "templateName": "verifyDomains",
                    "email": "admin@example.com",
                    "additional": {"domain": "example.com"},
                },
                {
                    "templateName": "requestAddon",
                    "email": ["admin@example.com", "support@example.com"],
                    "additional": {"addon": "advanced-reporting"},
                },
            ]
        }
    }


__all__ = ["SystemMailRequest", "SystemMailResponse", "SystemMailCreateFields"]
