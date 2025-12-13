"""
Mail Multi resource manager for Upsales API.

Provides batch email sending functionality through the /api/v2/mail/multi endpoint.
This is a POST-only endpoint for sending multiple emails in a single request.

Example:
    >>> async with Upsales(token="...") as upsales:
    ...     response = await upsales.mail_multi.send_batch([
    ...         {
    ...             "date": "2025-01-01",
    ...             "type": "out",
    ...             "clientId": 123,
    ...             "subject": "Email 1",
    ...             "body": "<p>Content</p>",
    ...             "to": "customer@example.com",
    ...             "from_address": "sales@company.com",
    ...             "fromName": "Sales Team"
    ...         }
    ...     ])
"""

from upsales.http import HTTPClient
from upsales.models.mail_multi import MailMultiItem, MailMultiResponse


class MailMultiResource:
    """
    Resource manager for batch email sending.

    This is a specialized resource that only supports POST operations for sending
    multiple emails in a single batch request. It does not inherit from BaseResource
    as it doesn't support standard CRUD operations.

    Example:
        Send multiple emails:
        ```python
        resource = MailMultiResource(http_client)
        response = await resource.send_batch([
            {"date": "2025-01-01", "type": "out", "subject": "Test", ...},
            {"date": "2025-01-01", "type": "out", "subject": "Test 2", ...}
        ])
        print(f"Sent: {response.total_sent}, Failed: {response.total_failed}")
        ```
    """

    def __init__(self, http: HTTPClient):
        """
        Initialize mail multi resource manager.

        Args:
            http: HTTP client for API requests.
        """
        self.http = http
        self.endpoint = "/mail/multi"

    def _prepare_http_kwargs(self) -> dict[str, object]:
        """Prepare kwargs for HTTP client calls."""
        if getattr(self.http, "_auto_allow_uninitialized", False):
            return {"_allow_uninitialized": True}
        return {}

    async def send_batch(self, emails: list[MailMultiItem]) -> MailMultiResponse:
        """
        Send multiple emails in a single batch request.

        Args:
            emails: List of email items to send. Each item should contain email fields
                   like date, type, subject, body, to, from_address, etc.

        Returns:
            Response containing batch operation results.

        Raises:
            UpsalesError: If the batch operation fails.
            ValueError: If emails list is empty.

        Examples:
            Send two emails:
            ```python
            response = await mail_multi.send_batch([
                {
                    "date": "2025-01-01",
                    "type": "out",
                    "clientId": 123,
                    "contactId": 456,
                    "subject": "First Email",
                    "body": "<p>Content 1</p>",
                    "to": "customer1@example.com",
                    "from_address": "sales@company.com",
                    "fromName": "Sales Team"
                },
                {
                    "date": "2025-01-01",
                    "type": "out",
                    "clientId": 789,
                    "contactId": 101,
                    "subject": "Second Email",
                    "body": "<p>Content 2</p>",
                    "to": "customer2@example.com",
                    "from_address": "sales@company.com",
                    "fromName": "Sales Team"
                }
            ])
            print(f"Total sent: {response.total_sent}")
            print(f"Total failed: {response.total_failed}")
            ```

        Note:
            This is a single batch request to the API. For truly parallel
            processing of multiple batches, use asyncio.gather().
        """
        if not emails:
            raise ValueError("Cannot send empty batch of emails")

        response = await self.http.post(
            self.endpoint,
            **self._prepare_http_kwargs(),
            array=emails,
        )

        payload = response.get("data", response)
        return MailMultiResponse(
            success=payload.get("success", True),
            results=payload.get("results", []),
            errors=payload.get("errors", []),
            total_sent=payload.get("total_sent", 0),
            total_failed=payload.get("total_failed", 0),
        )
