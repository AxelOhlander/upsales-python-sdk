"""Engage credit transactions resource manager for Upsales API.

Provides methods to interact with the /engage/creditTransaction endpoint.

Example:
    >>> async with Upsales(token="...") as upsales:
    ...     transaction = await upsales.engage_credit_transactions.get(1)
    ...     transactions = await upsales.engage_credit_transactions.list(limit=10)
"""

from upsales.http import HTTPClient
from upsales.models.engage_credit_transaction import (
    EngageCreditTransaction,
    PartialEngageCreditTransaction,
)
from upsales.resources.base import BaseResource


class EngageCreditTransactionsResource(
    BaseResource[EngageCreditTransaction, PartialEngageCreditTransaction]
):
    """Resource manager for engage credit transaction endpoint.

    Inherits standard CRUD operations from BaseResource:
    - get(id) - Get single transaction
    - list(limit, offset, **params) - List transactions with pagination
    - list_all(**params) - Auto-paginated list of all transactions
    - create(**data) - Create new transaction
    - update(id, **data) - Update transaction
    - delete(id) - Delete transaction
    - bulk_update(ids, data, max_concurrent) - Parallel updates
    - bulk_delete(ids, max_concurrent) - Parallel deletes

    Example:
        >>> resource = EngageCreditTransactionsResource(http_client)
        >>> transaction = await resource.get(1)
        >>> all_transactions = await resource.list_all()
    """

    def __init__(self, http: HTTPClient):
        """Initialize engage credit transaction resource manager.

        Args:
            http: HTTP client for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/engage/creditTransaction",
            model_class=EngageCreditTransaction,
            partial_class=PartialEngageCreditTransaction,
        )
