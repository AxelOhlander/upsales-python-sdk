"""
Contract Accepted resource manager for Upsales API.

Provides methods to interact with the /api/v2/contractAccepted endpoint.

Example:
    >>> async with Upsales(token="...") as upsales:
    ...     contract = await upsales.contract_accepted.get(1)
    ...     contracts_list = await upsales.contract_accepted.list(limit=10)
"""

from upsales.http import HTTPClient
from upsales.models.contract_accepted import ContractAccepted, PartialContractAccepted
from upsales.resources.base import BaseResource


class ContractAcceptedResource(BaseResource[ContractAccepted, PartialContractAccepted]):
    """
    Resource manager for Contract Accepted endpoint.

    Inherits standard CRUD operations from BaseResource:
    - create(**data) - Create new contract acceptance record
    - get(id) - Get single contract acceptance record
    - list(limit, offset, **params) - List records with pagination
    - list_all(**params) - Auto-paginated list of all records
    - update(id, **data) - Update contract acceptance record
    - delete(id) - Delete contract acceptance record
    - bulk_update(ids, data, max_concurrent) - Parallel updates
    - bulk_delete(ids, max_concurrent) - Parallel deletes

    Example:
        >>> resource = ContractAcceptedResource(http_client)
        >>> contract = await resource.get(1)
        >>> new_contract = await resource.create(contractId=123)
    """

    def __init__(self, http: HTTPClient):
        """
        Initialize contract accepted resource manager.

        Args:
            http: HTTP client for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/contractAccepted",
            model_class=ContractAccepted,
            partial_class=PartialContractAccepted,
        )

    # Add custom methods here as needed
    # Example:
    # async def get_by_contract(self, contract_id: int) -> list[ContractAccepted]:
    #     """Get all acceptance records for a specific contract."""
    #     return await self.list_all(contractId=contract_id)
