"""
Phone call models for Upsales API.

This module provides models for phone call tracking, typically used for
third-party integrations with phone systems.

Examples:
    Create a phone call record:
        >>> from upsales import Upsales
        >>> async with Upsales.from_env() as upsales:
        ...     call = await upsales.phone_calls.create(
        ...         user={"id": 1},
        ...         contact={"id": 100},
        ...         client={"id": 50},
        ...         durationInS=300,
        ...         phoneNumber="+1234567890",
        ...         type="Outbound"
        ...     )
        ...     print(f"Call ID: {call.id}")

    Update a phone call:
        >>> call = await upsales.phone_calls.get(1)
        >>> await call.edit(status=1, conversationUrl="https://...")

    List all phone calls:
        >>> calls = await upsales.phone_calls.list(limit=50)
"""

from typing import Any, TypedDict, Unpack

from pydantic import Field

from upsales.models.base import BaseModel, PartialModel
from upsales.models.company import PartialCompany
from upsales.models.contacts import PartialContact
from upsales.models.user import PartialUser


class PhoneCallUpdateFields(TypedDict, total=False):
    """
    Available fields for updating a PhoneCall.

    All fields are optional when updating.

    Attributes:
        durationInS: Duration of call in seconds.
        user: User who made/received the call (dict with 'id' key).
        type: Call type (max 45 chars).
        conversationUrl: URL to call recording (max 512 chars).
        contact: Contact associated with call (dict with 'id' key).
        date: Call date and time (YYYY-MM-DD HH:mm:ss format).
        status: Call status code.
        phoneNumber: Phone number called/received (max 45 chars).
        related: Related objects list.
        client: Company associated with call (dict with 'id' key).
        externalId: External system identifier (max 512 chars).
    """

    durationInS: int
    user: dict[str, Any]
    type: str
    conversationUrl: str | None
    contact: dict[str, Any]
    date: str
    status: int
    phoneNumber: str
    related: list[dict[str, Any]]
    client: dict[str, Any]
    externalId: str


class PhoneCall(BaseModel):
    """
    Phone call record from Upsales API.

    Represents a phone call interaction with a contact, typically created
    by third-party phone system integrations.

    Attributes:
        id: Unique phone call identifier (read-only).
        durationInS: Duration of the call in seconds.
        user: User who made or received the call.
        type: Type/category of the call (e.g., "Outbound", "Inbound").
        conversationUrl: URL to the call recording, if available.
        contact: Contact who was called or who called.
        date: Date and time of the call.
        status: Status code of the call.
        phoneNumber: Phone number that was called or received the call.
        related: List of related objects (activities, opportunities, etc.).
        client: Company associated with the call.
        externalId: External identifier from the phone system.

    Examples:
        Create a phone call:
            >>> call = await upsales.phone_calls.create(
            ...     user={"id": 1},
            ...     contact={"id": 100},
            ...     client={"id": 50},
            ...     durationInS=180
            ... )

        Update call status:
            >>> await call.edit(status=1, conversationUrl="https://recording.url")

        Access related objects:
            >>> print(f"User: {call.user.id}")
            >>> print(f"Contact: {call.contact.id}")
            >>> print(f"Company: {call.client.id}")
    """

    # Read-only fields
    id: int = Field(frozen=True, strict=True, description="Unique phone call identifier")

    # Required relationships
    user: PartialUser = Field(description="User who made/received the call")
    contact: PartialContact = Field(description="Contact associated with call")
    client: PartialCompany = Field(description="Company associated with call")

    # Call details
    durationInS: int = Field(default=0, description="Duration of call in seconds")
    phoneNumber: str = Field(default="", description="Phone number (max 45 chars)")
    date: str = Field(default="", description="Call date and time (YYYY-MM-DD HH:mm:ss)")
    type: str = Field(default="", description="Call type (max 45 chars)")
    status: int = Field(default=0, description="Call status code")

    # Optional fields
    conversationUrl: str | None = Field(None, description="URL to call recording (max 512 chars)")
    externalId: str = Field(default="", description="External system identifier (max 512 chars)")
    related: list[dict[str, Any]] = Field(default=[], description="Related objects")

    async def edit(self, **kwargs: Unpack[PhoneCallUpdateFields]) -> "PhoneCall":
        """
        Edit this phone call.

        Updates the phone call with the provided fields. Only specified fields
        will be updated; others remain unchanged.

        Args:
            **kwargs: Fields to update (see PhoneCallUpdateFields).

        Returns:
            Updated phone call instance.

        Raises:
            RuntimeError: If no client is available.
            ValidationError: If provided data is invalid.
            NotFoundError: If phone call no longer exists.

        Examples:
            Update call duration and status:
                >>> call = await upsales.phone_calls.get(1)
                >>> updated = await call.edit(
                ...     durationInS=300,
                ...     status=1
                ... )

            Add recording URL:
                >>> await call.edit(
                ...     conversationUrl="https://recording.example.com/call123"
                ... )
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.phone_calls.update(self.id, **self.to_api_dict(**kwargs))


class PartialPhoneCall(PartialModel):
    """
    Partial phone call for nested responses.

    Used when phone call data appears nested within other objects.
    Contains only the ID; use fetch_full() to get complete data.

    Attributes:
        id: Unique phone call identifier.

    Examples:
        Fetch full phone call data:
            >>> partial_call = activity.phone_call  # Nested in activity
            >>> full_call = await partial_call.fetch_full()
            >>> print(f"Duration: {full_call.durationInS}s")
    """

    id: int = Field(description="Unique phone call identifier")

    async def fetch_full(self) -> PhoneCall:
        """
        Fetch the complete phone call data.

        Returns:
            Full phone call instance with all fields.

        Raises:
            RuntimeError: If no client is available.
            NotFoundError: If phone call no longer exists.

        Examples:
            >>> partial = activity.phone_call
            >>> full = await partial.fetch_full()
            >>> print(full.durationInS, full.phoneNumber)
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.phone_calls.get(self.id)

    async def edit(self, **kwargs: Unpack[PhoneCallUpdateFields]) -> PhoneCall:
        """
        Edit this phone call.

        Args:
            **kwargs: Fields to update.

        Returns:
            Updated phone call instance.

        Raises:
            RuntimeError: If no client is available.

        Examples:
            >>> await partial.edit(status=1)
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.phone_calls.update(self.id, **kwargs)
