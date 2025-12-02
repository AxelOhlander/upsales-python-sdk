"""ValidatePage resource manager for Upsales API.

Provides methods to validate that webpages contain Upsales tracking script.

Example:
    ```python
    async with Upsales(token="...") as upsales:
        result = await upsales.validate_page.validate("https://example.com")
        if result.valid:
            print("Tracking script found!")
    ```
"""

from upsales.http import HTTPClient
from upsales.models.validate_page import ValidatePageResponse


class ValidatePageResource:
    """Resource manager for validatePage function endpoint.

    This endpoint validates that a webpage contains the Upsales tracking script.
    It's a POST-only function endpoint, not a standard CRUD resource.

    Args:
        http: HTTP client for API requests.

    Example:
        ```python
        resource = ValidatePageResource(http_client)
        result = await resource.validate("https://example.com")
        print(f"Valid: {result.valid}")
        ```
    """

    def __init__(self, http: HTTPClient):
        """Initialize validatePage resource manager.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/function/validatePage"

    async def validate(self, url: str) -> ValidatePageResponse:
        """Validate that a webpage contains Upsales tracking script.

        Args:
            url: The URL of the webpage to validate.

        Returns:
            ValidatePageResponse with validation result.

        Raises:
            ValidationError: If URL is invalid or request fails validation.
            ServerError: If server returns 5xx error.

        Example:
            ```python
            result = await upsales.validate_page.validate("https://example.com")
            if result.valid:
                print("Tracking script is present!")
            else:
                print(f"Validation failed: {result.message}")
            ```
        """
        response_data = await self._http.post(self._endpoint, url=url)
        return ValidatePageResponse(**response_data["data"])
