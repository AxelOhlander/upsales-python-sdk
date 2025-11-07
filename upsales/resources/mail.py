"""
Mail resource manager for Upsales API.

Provides methods to interact with the /mail endpoint.

Example:
    >>> async with Upsales(token="...") as upsales:
    ...     mail = await upsales.mail.get(1)
    ...     mails = await upsales.mail.list(limit=10)
    ...     sent_mails = await upsales.mail.get_sent()
"""

from upsales.http import HTTPClient
from upsales.models.mail import Mail, PartialMail
from upsales.resources.base import BaseResource


class MailResource(BaseResource[Mail, PartialMail]):
    """
    Resource manager for Mail endpoint.

    Inherits standard CRUD operations from BaseResource:
    - create(**data) - Create new mail
    - get(id) - Get single mail
    - list(limit, offset, **params) - List mails with pagination
    - list_all(**params) - Auto-paginated list of all mails
    - search(**filters) - Search with comparison operators
    - update(id, **data) - Update mail
    - delete(id) - Delete mail
    - bulk_update(ids, data, max_concurrent) - Parallel updates
    - bulk_delete(ids, max_concurrent) - Parallel deletes

    Example:
        >>> mail_resource = MailResource(http_client)
        >>> mail = await mail_resource.get(1)
        >>> sent = await mail_resource.get_sent()
        >>> recent = await mail_resource.get_recent(days=7)
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
            List of sent mail messages.

        Example:
            >>> sent_mails = await upsales.mail.get_sent()
            >>> all(m.type == 'sent' for m in sent_mails)
            True
        """
        return await self.list_all(type="sent")

    async def get_received(self) -> list[Mail]:
        """
        Get all received emails.

        Returns:
            List of received mail messages.

        Example:
            >>> received = await upsales.mail.get_received()
            >>> all(m.type == 'received' for m in received)
            True
        """
        return await self.list_all(type="received")

    async def get_drafts(self) -> list[Mail]:
        """
        Get all draft emails.

        Returns:
            List of draft mail messages.

        Example:
            >>> drafts = await upsales.mail.get_drafts()
            >>> all(m.type == 'draft' for m in drafts)
            True
        """
        return await self.list_all(type="draft")

    async def get_map_emails(self) -> list[Mail]:
        """
        Get all MAP (Marketing Automation Platform) emails.

        Returns:
            List of MAP emails (isMap=1).

        Example:
            >>> map_emails = await upsales.mail.get_map_emails()
            >>> all(m.is_map_email for m in map_emails)
            True
        """
        return await self.list_all(isMap=1)

    async def get_by_company(self, company_id: int) -> list[Mail]:
        """
        Get all emails for a specific company.

        Args:
            company_id: Company ID to filter by.

        Returns:
            List of emails linked to the company.

        Example:
            >>> mails = await upsales.mail.get_by_company(123)
            >>> len(mails)
            25
        """
        return await self.search(**{"client.id": company_id})

    async def get_by_contact(self, contact_id: int) -> list[Mail]:
        """
        Get all emails for a specific contact.

        Args:
            contact_id: Contact ID to filter by.

        Returns:
            List of emails linked to the contact.

        Example:
            >>> mails = await upsales.mail.get_by_contact(456)
            >>> all(m.contact is not None for m in mails)
            True
        """
        return await self.search(**{"contact.id": contact_id})

    async def get_by_opportunity(self, opportunity_id: int) -> list[Mail]:
        """
        Get all emails for a specific opportunity.

        Args:
            opportunity_id: Opportunity ID to filter by.

        Returns:
            List of emails linked to the opportunity.

        Example:
            >>> mails = await upsales.mail.get_by_opportunity(789)
            >>> all(m.opportunity is not None for m in mails)
            True
        """
        return await self.search(**{"opportunity.id": opportunity_id})

    async def get_with_attachments(self) -> list[Mail]:
        """
        Get all emails with attachments.

        Returns:
            List of emails that have attachments.

        Example:
            >>> with_files = await upsales.mail.get_with_attachments()
            >>> all(m.has_attachments for m in with_files)
            True
        """
        # Fetch all and filter in-memory (API might not support this directly)
        all_mails: list[Mail] = await self.list_all()
        return [m for m in all_mails if m.has_attachments]

    async def get_with_tracking(self) -> list[Mail]:
        """
        Get all emails with tracking events (opens, clicks).

        Returns:
            List of emails that have tracking events.

        Example:
            >>> tracked = await upsales.mail.get_with_tracking()
            >>> all(m.has_tracking_events for m in tracked)
            True
        """
        # Fetch all and filter in-memory
        all_mails: list[Mail] = await self.list_all()
        return [m for m in all_mails if m.has_tracking_events]

    async def get_by_thread(self, thread_id: int) -> list[Mail]:
        """
        Get all emails in a specific thread.

        Args:
            thread_id: Mail thread ID to filter by.

        Returns:
            List of emails in the thread.

        Example:
            >>> thread_mails = await upsales.mail.get_by_thread(123)
            >>> all(m.mailThreadId == 123 for m in thread_mails)
            True
        """
        return await self.list_all(mailThreadId=thread_id)

    async def get_recent(self, days: int = 7) -> list[Mail]:
        """
        Get recent emails from the last N days.

        Args:
            days: Number of days to look back (default: 7)

        Returns:
            List of emails from the last N days.

        Example:
            >>> recent = await upsales.mail.get_recent(days=7)
            >>> len(recent)
            42
        """
        from datetime import datetime, timedelta

        cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        return await self.search(
            date=f">={cutoff_date}",
            sort="-date",  # Newest first
        )

    async def search_by_subject(self, subject: str) -> list[Mail]:
        """
        Search emails by subject.

        Args:
            subject: Subject text to search for.

        Returns:
            List of emails matching the subject.

        Example:
            >>> results = await upsales.mail.search_by_subject("meeting")
            >>> all('meeting' in m.subject.lower() for m in results)
            True
        """
        # Fetch all and filter in-memory (API might not support text search)
        all_mails: list[Mail] = await self.list_all()
        return [m for m in all_mails if subject.lower() in m.subject.lower()]

    async def get_failed(self) -> list[Mail]:
        """
        Get all failed emails (with error cause).

        Returns:
            List of emails that failed to send.

        Example:
            >>> failed = await upsales.mail.get_failed()
            >>> all(m.errorCause is not None for m in failed)
            True
        """
        # Fetch all and filter in-memory
        all_mails: list[Mail] = await self.list_all()
        return [m for m in all_mails if m.errorCause is not None]
