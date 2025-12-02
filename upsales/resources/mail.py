"""
Mails resource manager for Upsales API.

Provides methods to interact with the /mail endpoint.

Example:
    >>> async with Upsales(token="...") as upsales:
    ...     mail = await upsales.mail.get(1)
    ...     mail_list = await upsales.mail.list(limit=10)
"""

from upsales.http import HTTPClient
from upsales.models.mail import Mail, PartialMail
from upsales.resources.base import BaseResource


class MailResource(BaseResource[Mail, PartialMail]):
    """
    Resource manager for Mail endpoint.

    Handles operations for email messages including sent, received, and processed emails.

    Inherits standard CRUD operations from BaseResource:
    - create(**data) - Create new mail record
    - get(id) - Get single mail
    - list(limit, offset, **params) - List mail with pagination
    - list_all(**params) - Auto-paginated list of all mail
    - update(id, **data) - Update mail
    - delete(id) - Delete mail
    - bulk_update(ids, data, max_concurrent) - Parallel updates
    - bulk_delete(ids, max_concurrent) - Parallel deletes

    Examples:
        Create a mail record:
        ```python
        mail = await upsales.mail.create(
            date="2025-01-01",
            type="out",
            clientId=123,
            contactId=456,
            subject="Follow-up",
            body="<p>Email content</p>",
            to="customer@example.com",
            from_address="sales@company.com"
        )
        ```

        List outgoing emails:
        ```python
        outgoing = await upsales.mail.list_all(type="out")
        ```
    """

    def __init__(self, http: HTTPClient):
        """
        Initialize mail resource manager.

        Args:
            http: HTTP client for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/mail",
            model_class=Mail,
            partial_class=PartialMail,
        )

    async def get_sent(self) -> list[Mail]:
        """
        Get all sent emails.

        Returns:
            List of sent emails.

        Examples:
            ```python
            sent_emails = await upsales.mail.get_sent()
            ```
        """
        return await self.search(type="sent")

    async def get_received(self) -> list[Mail]:
        """
        Get all received emails.

        Returns:
            List of received emails.

        Examples:
            ```python
            received = await upsales.mail.get_received()
            ```
        """
        return await self.search(type="received")

    async def get_drafts(self) -> list[Mail]:
        """
        Get all draft emails.

        Returns:
            List of draft emails.

        Examples:
            ```python
            drafts = await upsales.mail.get_drafts()
            ```
        """
        return await self.search(type="draft")

    async def get_map_emails(self) -> list[Mail]:
        """
        Get all MAP (Marketing Automation Platform) emails.

        Returns:
            List of MAP emails.

        Examples:
            ```python
            map_emails = await upsales.mail.get_map_emails()
            ```
        """
        return await self.search(isMap=1)

    async def get_by_company(self, company_id: int) -> list[Mail]:
        """
        Get all emails for a specific company.

        Args:
            company_id: Company ID.

        Returns:
            List of emails for the company.

        Examples:
            ```python
            company_emails = await upsales.mail.get_by_company(123)
            ```
        """
        return await self.search(**{"client.id": company_id})

    async def get_by_contact(self, contact_id: int) -> list[Mail]:
        """
        Get all emails for a specific contact.

        Args:
            contact_id: Contact ID.

        Returns:
            List of emails for the contact.

        Examples:
            ```python
            contact_emails = await upsales.mail.get_by_contact(456)
            ```
        """
        return await self.search(**{"contact.id": contact_id})

    async def get_by_opportunity(self, opportunity_id: int) -> list[Mail]:
        """
        Get all emails for a specific opportunity.

        Args:
            opportunity_id: Opportunity ID.

        Returns:
            List of emails for the opportunity.

        Examples:
            ```python
            opp_emails = await upsales.mail.get_by_opportunity(789)
            ```
        """
        return await self.search(**{"opportunity.id": opportunity_id})

    async def get_by_thread(self, thread_id: int) -> list[Mail]:
        """
        Get all emails in a specific thread.

        Args:
            thread_id: Mail thread ID.

        Returns:
            List of emails in the thread.

        Examples:
            ```python
            thread_emails = await upsales.mail.get_by_thread(456)
            ```
        """
        return await self.search(mailThreadId=thread_id)

    async def get_recent(self, days: int = 7) -> list[Mail]:
        """
        Get recent emails from the last N days.

        Args:
            days: Number of days to look back (default: 7).

        Returns:
            List of recent emails.

        Examples:
            ```python
            recent = await upsales.mail.get_recent(days=30)
            ```
        """
        from datetime import datetime, timedelta

        cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        return await self.search(**{"date": f"gte:{cutoff_date}"})

    async def get_with_attachments(self) -> list[Mail]:
        """
        Get all emails that have attachments.

        Returns:
            List of emails with attachments.

        Examples:
            ```python
            with_attachments = await upsales.mail.get_with_attachments()
            ```
        """
        all_mail: list[Mail] = await self.list_all()
        return [m for m in all_mail if m.has_attachments]

    async def get_with_tracking(self) -> list[Mail]:
        """
        Get all emails that have tracking events.

        Returns:
            List of emails with tracking events.

        Examples:
            ```python
            tracked = await upsales.mail.get_with_tracking()
            ```
        """
        all_mail: list[Mail] = await self.list_all()
        return [m for m in all_mail if m.has_tracking_events]

    async def search_by_subject(self, subject_query: str) -> list[Mail]:
        """
        Search emails by subject text.

        Args:
            subject_query: Text to search for in subject.

        Returns:
            List of matching emails.

        Examples:
            ```python
            results = await upsales.mail.search_by_subject("meeting")
            ```
        """
        all_mail: list[Mail] = await self.list_all()
        return [m for m in all_mail if subject_query.lower() in m.subject.lower()]

    async def get_failed(self) -> list[Mail]:
        """
        Get all emails that failed to send.

        Returns:
            List of failed emails (with errorCause set).

        Examples:
            ```python
            failed = await upsales.mail.get_failed()
            ```
        """
        all_mail: list[Mail] = await self.list_all()
        return [m for m in all_mail if m.errorCause is not None]
