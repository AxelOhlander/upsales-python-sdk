"""ValidatePage model for Upsales API.

This module provides models for validating that a webpage contains the Upsales tracking script.
"""

from __future__ import annotations

from pydantic import BaseModel as PydanticBaseModel
from pydantic import Field


class ValidatePageRequest(PydanticBaseModel):
    """Request model for validatePage endpoint.

    Attributes:
        url: The URL of the webpage to validate for Upsales tracking script.

    Example:
        ```python
        request = ValidatePageRequest(url="https://example.com")
        result = await upsales.validate_page.validate(request.url)
        ```
    """

    url: str = Field(description="URL of webpage to validate")


class ValidatePageResponse(PydanticBaseModel):
    """Response model for validatePage endpoint.

    Attributes:
        valid: Whether the page contains valid Upsales tracking script.
        message: Optional message describing validation result.

    Example:
        ```python
        result = await upsales.validate_page.validate("https://example.com")
        if result.valid:
            print("Tracking script found!")
        else:
            print(f"Validation failed: {result.message}")
        ```
    """

    valid: bool = Field(description="Whether page contains valid tracking script")
    message: str | None = Field(None, description="Validation result message")
