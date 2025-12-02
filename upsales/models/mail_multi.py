"""
Mail Multi models for Upsales API.

Provides batch email sending functionality. This endpoint allows sending multiple emails
in a single API request for improved performance.
"""

from typing import Any, TypedDict

from pydantic import BaseModel, Field


class MailMultiItem(TypedDict, total=False):
    """
    Single email item for batch sending.

    All fields are optional to provide maximum flexibility.
    """

    date: str
    subject: str
    body: str
    to: str
    from_address: str
    fromName: str
    type: str
    clientId: int
    contactId: int
    cc: list[str]
    bcc: list[str]
    attachments: list[dict[str, Any]]


class MailMultiRequest(TypedDict, total=False):
    """
    Request payload for batch email sending.

    Contains an array of email items to send.
    """

    array: list[MailMultiItem]


class MailMultiResponse(BaseModel):
    """
    Response from batch email sending operation.

    Contains the results of the batch operation, including success/failure status
    for each email.

    Examples:
        Send multiple emails in batch:
        ```python
        response = await upsales.mail_multi.send_batch([
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
        print(f"Sent {len(response.results)} emails")
        ```
    """

    success: bool = Field(description="Overall batch operation success status")
    results: list[dict[str, Any]] = Field(
        default_factory=list, description="Individual email results"
    )
    errors: list[dict[str, Any]] = Field(
        default_factory=list, description="Any errors that occurred"
    )
    total_sent: int = Field(default=0, description="Total number of emails successfully sent")
    total_failed: int = Field(default=0, description="Total number of emails that failed")
