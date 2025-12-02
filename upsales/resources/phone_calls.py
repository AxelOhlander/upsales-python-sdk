"""
Phone calls resource manager for Upsales API.

Provides methods to interact with the /api/v2/phoneCall endpoint for
phone call tracking and third-party phone system integrations.

Examples:
    Get a phone call:
        >>> async with Upsales(token="...") as upsales:
        ...     call = await upsales.phone_calls.get(1)
        ...     print(f"Duration: {call.durationInS}s")

    Create a phone call:
        >>> call = await upsales.phone_calls.create(
        ...     user={"id": 1},
        ...     contact={"id": 100},
        ...     client={"id": 50},
        ...     durationInS=300,
        ...     phoneNumber="+1234567890"
        ... )

    List all phone calls:
        >>> calls = await upsales.phone_calls.list(limit=50)
"""

from upsales.http import HTTPClient
from upsales.models.phone_call import PartialPhoneCall, PhoneCall
from upsales.resources.base import BaseResource


class PhoneCallsResource(BaseResource[PhoneCall, PartialPhoneCall]):
    """
    Resource manager for phone call endpoint.

    Inherits standard CRUD operations from BaseResource:
    - create(**data) - Create new phone call
    - get(id) - Get single phone call
    - list(limit, offset, **params) - List phone calls with pagination
    - list_all(**params) - Auto-paginated list of all phone calls
    - search(**filters) - Search with comparison operators
    - update(id, **data) - Update phone call
    - delete(id) - Delete phone call
    - bulk_update(ids, data, max_concurrent) - Parallel updates
    - bulk_delete(ids, max_concurrent) - Parallel deletes

    Examples:
        Create a phone call:
            >>> resource = PhoneCallsResource(http_client)
            >>> call = await resource.create(
            ...     user={"id": 1},
            ...     contact={"id": 100},
            ...     client={"id": 50}
            ... )

        Search for calls by user:
            >>> calls = await resource.search(user__id__eq=1)

        Get calls for a specific contact:
            >>> calls = await resource.list_all(contact__id=100)
    """

    def __init__(self, http: HTTPClient):
        """
        Initialize phone calls resource manager.

        Args:
            http: HTTP client for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/phoneCall",  # API endpoint
            model_class=PhoneCall,
            partial_class=PartialPhoneCall,
        )

    # Add custom methods here as needed
    # Example:
    # async def get_by_contact(self, contact_id: int) -> list[PhoneCall]:
    #     """Get all phone calls for a specific contact."""
    #     return await self.list_all(contact__id=contact_id)
