"""
Agreement Groups resource manager for Upsales API.

Provides methods to interact with the /agreementGroups endpoint.

Agreement groups manage timelines of agreements for a single client,
allowing current and future agreements with non-overlapping date ranges.

Example:
    >>> async with Upsales(token="...") as upsales:
    ...     group = await upsales.agreement_groups.get(1)
    ...     client_groups = await upsales.agreement_groups.get_for_client(99)
"""

from typing import Any

from upsales.http import HTTPClient
from upsales.models.agreement_groups import AgreementGroup, PartialAgreementGroup
from upsales.resources.base import BaseResource


class AgreementGroupsResource(BaseResource[AgreementGroup, PartialAgreementGroup]):
    """
    Resource manager for Agreement Groups endpoint.

    Agreement groups allow managing current and future agreements together
    for a single client with automatic current agreement determination.

    Inherits standard CRUD operations from BaseResource:
    - get(id) - Get single agreement group with agreements
    - list(limit, offset, **params) - List groups with pagination
    - list_all(**params) - Auto-paginated list of all groups
    - create(**data) - Create new agreement group with agreements
    - update(id, **data) - Update group and its agreements
    - delete(id) - Delete group (also deletes all agreements in it!)
    - count(**params) - Count groups matching criteria

    Additional methods:
    - get_by_agreement(agreement_id) - Get group containing an agreement
    - get_for_client(client_id) - Get all active groups for a client
    - move_to_client(group_id, client_id, contact_id) - Move group to another client

    Example:
        >>> # Create a group with current and future agreements
        >>> group = await upsales.agreement_groups.create(
        ...     client={"id": 99},
        ...     agreements=[
        ...         {
        ...             "description": "2025 subscription",
        ...             "client": {"id": 99},
        ...             "user": {"id": 7},
        ...             "stage": {"id": 3},
        ...             "currency": "SEK",
        ...             "orderRow": [{"product": {"id": 55}, "quantity": 10, "price": 100}],
        ...             "metadata": {
        ...                 "agreementStartdate": "2025-01-01",
        ...                 "agreementInvoiceStartdate": "2025-01-01",
        ...                 "periodLength": 12,
        ...                 "agreementIntervalPeriod": 12,
        ...                 "agreementOrderCreationTime": 0
        ...             }
        ...         },
        ...         {
        ...             "description": "2026 subscription (future)",
        ...             "client": {"id": 99},
        ...             "user": {"id": 7},
        ...             "stage": {"id": 3},
        ...             "currency": "SEK",
        ...             "orderRow": [{"product": {"id": 55}, "quantity": 10, "price": 120}],
        ...             "metadata": {
        ...                 "agreementStartdate": "2026-01-01",
        ...                 "agreementInvoiceStartdate": "2026-01-01",
        ...                 "periodLength": 12,
        ...                 "agreementIntervalPeriod": 12,
        ...                 "agreementOrderCreationTime": 0
        ...             }
        ...         }
        ...     ]
        ... )
    """

    def __init__(self, http: HTTPClient):
        """
        Initialize agreement groups resource manager.

        Args:
            http: HTTP client for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/agreementGroups",
            model_class=AgreementGroup,
            partial_class=PartialAgreementGroup,
        )

    async def get_by_agreement(self, agreement_id: int) -> AgreementGroup:
        """
        Get the agreement group containing a specific agreement.

        If the agreement is not part of a group, returns a synthetic group
        with that agreement as the current and only agreement.

        Args:
            agreement_id: ID of the agreement.

        Returns:
            AgreementGroup containing the agreement.

        Example:
            >>> group = await upsales.agreement_groups.get_by_agreement(123)
            >>> print(f"Group ID: {group.id}")
            >>> print(f"Agreements in group: {len(group.agreements)}")
        """
        request_kwargs = self._prepare_http_kwargs()
        response = await self._http.get(
            f"{self._endpoint}/agreement/{agreement_id}",
            **request_kwargs,
        )
        return self._model_class(**response, _client=self._http._upsales_client)

    async def get_for_client(self, client_id: int) -> list[AgreementGroup]:
        """
        Get all active agreement groups for a client.

        Returns only active groups (where current agreement hasn't ended
        and has started creating orders).

        Args:
            client_id: Client/company ID.

        Returns:
            List of active agreement groups for the client.

        Example:
            >>> groups = await upsales.agreement_groups.get_for_client(99)
            >>> for group in groups:
            ...     print(f"{group.currentAgreement.description}: "
            ...           f"{len(group.agreements)} agreements")
        """
        request_kwargs = self._prepare_http_kwargs()
        response = await self._http.get(
            f"{self._endpoint}/client/{client_id}",
            **request_kwargs,
        )
        # Response is a list directly
        if isinstance(response, list):
            return [
                self._model_class(**item, _client=self._http._upsales_client) for item in response
            ]
        # Handle wrapped response
        data = response.get("data", response)
        if isinstance(data, list):
            return [self._model_class(**item, _client=self._http._upsales_client) for item in data]
        return []

    async def move_to_client(
        self,
        group_id: int,
        client_id: int,
        contact_id: int | None = None,
    ) -> AgreementGroup:
        """
        Move an agreement group to a different client.

        Moves the group and all its agreements to the new client.
        Optionally assigns a new contact.

        Args:
            group_id: Agreement group ID to move.
            client_id: Target client/company ID.
            contact_id: Optional new contact ID.

        Returns:
            Updated AgreementGroup with new client.

        Example:
            >>> # Move group 10 to client 200
            >>> group = await upsales.agreement_groups.move_to_client(
            ...     group_id=10,
            ...     client_id=200,
            ...     contact_id=500  # Optional new contact
            ... )
            >>> print(f"Group now belongs to client {group.client.id}")
        """
        request_kwargs = self._prepare_http_kwargs()
        data: dict[str, Any] = {
            "agreementGroupId": group_id,
            "clientId": client_id,
        }
        if contact_id is not None:
            data["contactId"] = contact_id

        response = await self._http.post(
            f"{self._endpoint}/moveToClient",
            **request_kwargs,
            **data,
        )
        return self._model_class(**response["data"], _client=self._http._upsales_client)
