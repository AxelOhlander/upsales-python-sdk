"""
E-signature function resource for Upsales API.

This resource provides access to e-signature integration settings and
document download capabilities. Note: This endpoint does not follow
standard CRUD patterns.
"""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from upsales.http import HTTPClient

from upsales.models.esign_function import EsignFunctionSettings


class EsignFunctionResource:
    """
    Resource manager for e-signature function endpoint.

    This is a special function endpoint that provides:
    - POST: Retrieve e-signature integration settings
    - GET: Download signed documents as PDF

    Unlike standard resources, this does not support list/create/update/delete
    operations. It's a specialized endpoint for e-signature integration.

    Args:
        http: HTTP client instance for making API requests.

    Attributes:
        _http: HTTP client for API requests.
        _endpoint: API endpoint path (/function/esign).

    Example:
        >>> # Get e-signature settings
        >>> settings = await upsales.esign_function.get_settings(
        ...     integration_id=123
        ... )
        >>> print(settings.languages)
        ['en', 'sv', 'no']
        >>>
        >>> # Download a signed document
        >>> pdf_bytes = await upsales.esign_function.download(
        ...     document_id=456
        ... )
        >>> with open("signed.pdf", "wb") as f:
        ...     f.write(pdf_bytes)
    """

    def __init__(self, http: "HTTPClient") -> None:
        """
        Initialize e-signature function resource.

        Args:
            http: HTTP client instance.
        """
        self._http = http
        self._endpoint = "/function/esign"

    async def get_settings(
        self,
        integration_id: int,
        **kwargs: Any,
    ) -> EsignFunctionSettings:
        """
        Retrieve e-signature integration settings.

        Fetches configuration settings for a specific e-signature integration,
        including delivery methods, supported languages, BankID countries,
        and multi-signature capabilities.

        Args:
            integration_id: The integration identifier.
            **kwargs: Additional settings parameters to include in the request.

        Returns:
            EsignFunctionSettings instance with integration configuration.

        Raises:
            AuthenticationError: If authentication fails (401/403).
            ValidationError: If the integration ID is invalid (400).
            NotFoundError: If the integration is not found (404).
            ServerError: If the server encounters an error (500+).

        Example:
            >>> settings = await upsales.esign_function.get_settings(
            ...     integration_id=123
            ... )
            >>> if settings.multiSign:
            ...     print("Multiple signatures supported")
            >>> print(f"Available languages: {settings.languages}")
        """
        response = await self._http.post(
            self._endpoint,
            type="settings",
            integrationId=integration_id,
            **kwargs,
        )

        settings = EsignFunctionSettings(**response["data"])
        settings._client = getattr(self._http, "_client", None)
        return settings

    async def download(self, document_id: int) -> bytes:
        """
        Download a signed document as PDF.

        Retrieves the signed PDF document from the e-signature provider.

        Args:
            document_id: The document identifier to download.

        Returns:
            bytes: Raw PDF file content.

        Raises:
            AuthenticationError: If authentication fails (401/403).
            NotFoundError: If the document is not found (404).
            ServerError: If the server encounters an error (500+).

        Example:
            >>> pdf_bytes = await upsales.esign_function.download(
            ...     document_id=456
            ... )
            >>> with open("signed.pdf", "wb") as f:
            ...     f.write(pdf_bytes)
        """
        return await self._http.get_bytes(f"{self._endpoint}/download/{document_id}")
