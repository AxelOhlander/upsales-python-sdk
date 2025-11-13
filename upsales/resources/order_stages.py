"""
OrderStages resource manager for Upsales API.

Provides methods to interact with the /orderStages endpoint for managing
order/opportunity pipeline stages.

Example:
    >>> async with Upsales(token="...") as upsales:
    ...     stage = await upsales.order_stages.get(1)
    ...     all_stages = await upsales.order_stages.list_all()
"""

from upsales.http import HTTPClient
from upsales.models.order_stages import OrderStage, PartialOrderStage
from upsales.resources.base import BaseResource


class OrderStagesResource(BaseResource[OrderStage, PartialOrderStage]):
    """
    Resource manager for OrderStage endpoint.

    Inherits standard CRUD operations from BaseResource:
    - create(**data) - Create new order stage
    - get(id) - Get single order stage
    - list(limit, offset, **params) - List order stages with pagination
    - list_all(**params) - Auto-paginated list of all order stages
    - search(**filters) - Search with comparison operators
    - update(id, **data) - Update order stage
    - delete(id) - Delete order stage
    - bulk_update(ids, data, max_concurrent) - Parallel updates
    - bulk_delete(ids, max_concurrent) - Parallel deletes

    Example:
        >>> order_stages = OrderStagesResource(http_client)
        >>> stage = await order_stages.get(1)
        >>> included = await order_stages.get_included()
    """

    def __init__(self, http: HTTPClient):
        """
        Initialize order stages resource manager.

        Args:
            http: HTTP client for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/orderStages",
            model_class=OrderStage,
            partial_class=PartialOrderStage,
        )

    async def get_included(self) -> list[OrderStage]:
        """
        Get all order stages included in pipeline calculations.

        Returns stages where exclude=0 (included in pipeline metrics
        and forecasting).

        Returns:
            List of order stages included in pipeline.

        Example:
            >>> included = await upsales.order_stages.get_included()
            >>> for stage in included:
            ...     print(f"{stage.name}: {stage.probability}%")
            'Qualified: 25%'
            'Proposal: 50%'
        """
        return await self.list_all(exclude=0)

    async def get_excluded(self) -> list[OrderStage]:
        """
        Get all order stages excluded from pipeline calculations.

        Returns stages where exclude=1 (not counted in pipeline
        metrics or forecasting, e.g., "Lost", "Cancelled").

        Returns:
            List of order stages excluded from pipeline.

        Example:
            >>> excluded = await upsales.order_stages.get_excluded()
            >>> for stage in excluded:
            ...     print(stage.name)
            'Lost'
            'Cancelled'
        """
        return await self.list_all(exclude=1)

    async def get_by_probability_range(self, min_prob: int, max_prob: int) -> list[OrderStage]:
        """
        Get order stages within a probability range.

        Useful for filtering stages by confidence level (e.g., high-confidence
        stages with 70%+ probability).

        Args:
            min_prob: Minimum probability (1-100).
            max_prob: Maximum probability (1-100).

        Returns:
            List of order stages in the probability range.

        Example:
            >>> # Get high-confidence stages (70%+)
            >>> high_conf = await upsales.order_stages.get_by_probability_range(70, 100)
            >>> for stage in high_conf:
            ...     print(f"{stage.name}: {stage.probability}%")
            'Negotiation: 75%'
            'Closed Won: 100%'
        """
        # Get all stages and filter by range (API doesn't support range filters well)
        all_stages: list[OrderStage] = await self.list_all(sort="probability")
        return [s for s in all_stages if min_prob <= s.probability <= max_prob]

    async def get_sorted_by_probability(self, descending: bool = False) -> list[OrderStage]:
        """
        Get all order stages sorted by probability.

        Args:
            descending: If True, sort from highest to lowest probability.
                       If False (default), sort from lowest to highest.

        Returns:
            List of order stages sorted by probability.

        Example:
            >>> # Get stages from lowest to highest probability
            >>> stages = await upsales.order_stages.get_sorted_by_probability()
            >>> for stage in stages:
            ...     print(f"{stage.name}: {stage.probability}%")
            'Qualified: 10%'
            'Discovery: 25%'
            'Closed Won: 100%'
            >>>
            >>> # Get stages from highest to lowest
            >>> stages = await upsales.order_stages.get_sorted_by_probability(descending=True)
        """
        sort_param = "-probability" if descending else "probability"
        return await self.list_all(sort=sort_param)
