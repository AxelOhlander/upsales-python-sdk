"""
Orders resource manager for Upsales API.

Provides methods to interact with the /orders endpoint using Order models.

Example:
    >>> async with Upsales(token="...") as upsales:
    ...     # Get single order
    ...     order = await upsales.orders.get(1)
    ...     print(order.description, order.expected_value)
    ...
    ...     # List orders
    ...     orders = await upsales.orders.list(limit=10)
    ...
    ...     # Get high-value opportunities
    ...     high_value = await upsales.orders.get_high_value(min_value=100000)
    ...
    ...     # Get orders by stage
    ...     qualified = await upsales.orders.get_by_stage(stage_id=5)
    ...
    ...     # Get orders with high win probability
    ...     likely_wins = await upsales.orders.get_by_probability_range(min_probability=75)
"""

from upsales.http import HTTPClient
from upsales.models.orders import Order, PartialOrder
from upsales.resources.base import BaseResource


class OrdersResource(BaseResource[Order, PartialOrder]):
    """
    Resource manager for Order endpoint.

    Inherits standard CRUD operations from BaseResource:
    - create(**data) - Create new order
    - get(id) - Get single order
    - list(limit, offset, **params) - List orders with pagination
    - list_all(**params) - Auto-paginated list of all orders
    - search(**filters) - Search with comparison operators
    - update(id, **data) - Update order
    - delete(id) - Delete order
    - bulk_update(ids, data, max_concurrent) - Parallel updates
    - bulk_delete(ids, max_concurrent) - Parallel deletes

    Additional methods:
    - get_by_company(company_id) - Get all orders for a company
    - get_by_user(user_id) - Get all orders owned by a user
    - get_by_stage(stage_id) - Get orders in specific stage
    - get_high_value(min_value) - Get orders above value threshold
    - get_by_probability_range(min_prob, max_prob) - Get orders in probability range
    - get_closing_soon(days) - Get orders closing within N days
    - get_recurring() - Get orders with recurring revenue

    Example:
        >>> orders = OrdersResource(http_client)
        >>> order = await orders.get(1)
        >>> high_value = await orders.get_high_value(100000)
        >>> by_stage = await orders.get_by_stage(5)
    """

    def __init__(self, http: HTTPClient):
        """
        Initialize orders resource manager.

        Args:
            http: HTTP client for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/orders",
            model_class=Order,
            partial_class=PartialOrder,
        )

    async def get_by_company(self, company_id: int) -> list[Order]:
        """
        Get all orders for a specific company.

        Args:
            company_id: Company ID to filter by.

        Returns:
            List of orders belonging to the company.

        Example:
            >>> orders = await upsales.orders.get_by_company(123)
            >>> len(orders)
            15
            >>> sum(o.value for o in orders)
            500000
        """
        # Note: API uses nested field syntax for filtering
        return await self.search(**{"client.id": company_id})

    async def get_by_user(self, user_id: int) -> list[Order]:
        """
        Get all orders owned by a specific user.

        Args:
            user_id: User ID to filter by.

        Returns:
            List of orders owned by the user.

        Example:
            >>> my_orders = await upsales.orders.get_by_user(10)
            >>> for order in my_orders:
            ...     print(f"{order.description}: ${order.value}")
        """
        return await self.search(**{"user.id": user_id})

    async def get_by_stage(self, stage_id: int) -> list[Order]:
        """
        Get all orders in a specific stage.

        Args:
            stage_id: Stage ID to filter by.

        Returns:
            List of orders in the stage.

        Example:
            >>> qualified = await upsales.orders.get_by_stage(5)
            >>> proposal = await upsales.orders.get_by_stage(7)
        """
        return await self.search(**{"stage.id": stage_id})

    async def get_high_value(self, min_value: int = 100000) -> list[Order]:
        """
        Get orders above a value threshold.

        Args:
            min_value: Minimum order value (default: 100000).

        Returns:
            List of orders with value >= min_value, sorted by value descending.

        Example:
            >>> high_value = await upsales.orders.get_high_value(100000)
            >>> enterprise = await upsales.orders.get_high_value(1000000)
            >>> for order in high_value:
            ...     print(f"{order.description}: ${order.value}")
        """
        return await self.search(value=f">={min_value}", sort="-value")

    async def get_by_probability_range(
        self, min_probability: int = 0, max_probability: int = 100
    ) -> list[Order]:
        """
        Get orders within a probability range.

        Args:
            min_probability: Minimum win probability (0-100, default: 0).
            max_probability: Maximum win probability (0-100, default: 100).

        Returns:
            List of orders within the probability range.

        Example:
            >>> # High probability wins (75%+)
            >>> likely_wins = await upsales.orders.get_by_probability_range(75, 100)
            >>>
            >>> # Medium probability (25-75%)
            >>> medium = await upsales.orders.get_by_probability_range(25, 75)
            >>>
            >>> # Low probability (<25%)
            >>> long_shots = await upsales.orders.get_by_probability_range(0, 25)
        """
        return await self.search(
            probability=f">={min_probability}",
            probability_max=f"<={max_probability}",
            sort="-probability",
        )

    async def get_closing_soon(self, days: int = 30) -> list[Order]:
        """
        Get orders closing within the next N days.

        Args:
            days: Number of days to look ahead (default: 30).

        Returns:
            List of orders with closeDate within next N days, sorted by close date.

        Example:
            >>> # Orders closing this month
            >>> closing_soon = await upsales.orders.get_closing_soon(30)
            >>>
            >>> # Orders closing this week
            >>> this_week = await upsales.orders.get_closing_soon(7)
        """
        from datetime import datetime, timedelta

        today = datetime.now().date()
        target_date = today + timedelta(days=days)

        return await self.search(
            closeDate=f">={today.isoformat()}",
            closeDate_max=f"<={target_date.isoformat()}",
            sort="closeDate",
        )

    async def get_recurring(self) -> list[Order]:
        """
        Get all orders with recurring revenue.

        Returns:
            List of orders where monthlyValue or annualValue > 0.

        Example:
            >>> recurring = await upsales.orders.get_recurring()
            >>> total_mrr = sum(o.monthlyValue for o in recurring)
            >>> total_arr = sum(o.annualValue for o in recurring)
            >>> print(f"Total MRR: ${total_mrr}, Total ARR: ${total_arr}")
        """
        # Get all orders and filter client-side (API may not support OR filter)
        all_orders: list[Order] = await self.list_all()
        return [order for order in all_orders if order.is_recurring]
