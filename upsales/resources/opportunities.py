"""
Opportunities resource manager for Upsales API.

Provides methods to interact with the /opportunities endpoint using Order models.

Opportunities are pipeline deals with probability 1-99% (not 0% or 100%).
They share the same data model as Orders but use a different endpoint.

Example:
    >>> async with Upsales(token="...") as upsales:
    ...     # Get single opportunity
    ...     opp = await upsales.opportunities.get(1)
    ...     print(opp.description, opp.expected_value)
    ...
    ...     # List opportunities
    ...     opps = await upsales.opportunities.list(limit=10)
    ...
    ...     # Get high-value opportunities
    ...     high_value = await upsales.opportunities.get_high_value(min_value=100000)
    ...
    ...     # Get opportunities by stage
    ...     qualified = await upsales.opportunities.get_by_stage(stage_id=5)
    ...
    ...     # Get opportunities with high win probability
    ...     likely_wins = await upsales.opportunities.get_by_probability_range(min_probability=75)
"""

from upsales.http import HTTPClient
from upsales.models.orders import Order, PartialOrder
from upsales.resources.base import BaseResource


class OpportunitiesResource(BaseResource[Order, PartialOrder]):
    """
    Resource manager for Opportunities endpoint.

    Opportunities are deals in the pipeline with probability 1-99%.
    They use the same data model as Orders but have a different API endpoint.

    Inherits standard CRUD operations from BaseResource:
    - create(**data) - Create new opportunity
    - get(id) - Get single opportunity
    - list(limit, offset, **params) - List opportunities with pagination
    - list_all(**params) - Auto-paginated list of all opportunities
    - search(**filters) - Search with comparison operators
    - update(id, **data) - Update opportunity
    - delete(id) - Delete opportunity
    - bulk_update(ids, data, max_concurrent) - Parallel updates
    - bulk_delete(ids, max_concurrent) - Parallel deletes

    Additional methods:
    - get_by_company(company_id) - Get all opportunities for a company
    - get_by_user(user_id) - Get all opportunities owned by a user
    - get_by_stage(stage_id) - Get opportunities in specific stage
    - get_high_value(min_value) - Get opportunities above value threshold
    - get_by_probability_range(min_prob, max_prob) - Get opportunities in probability range
    - get_closing_soon(days) - Get opportunities closing within N days
    - get_recurring() - Get opportunities with recurring revenue

    Example:
        >>> opportunities = OpportunitiesResource(http_client)
        >>> opp = await opportunities.get(1)
        >>> high_value = await opportunities.get_high_value(100000)
        >>> by_stage = await opportunities.get_by_stage(5)
    """

    def __init__(self, http: HTTPClient):
        """
        Initialize opportunities resource manager.

        Args:
            http: HTTP client for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/opportunities",
            model_class=Order,
            partial_class=PartialOrder,
        )

    async def get_by_company(self, company_id: int) -> list[Order]:
        """
        Get all opportunities for a specific company.

        Args:
            company_id: Company ID to filter by.

        Returns:
            List of opportunities belonging to the company.

        Example:
            >>> opps = await upsales.opportunities.get_by_company(123)
            >>> len(opps)
            15
            >>> sum(o.value for o in opps)
            500000
        """
        # Note: API uses nested field syntax for filtering
        return await self.search(**{"client.id": company_id})

    async def get_by_user(self, user_id: int) -> list[Order]:
        """
        Get all opportunities owned by a specific user.

        Args:
            user_id: User ID to filter by.

        Returns:
            List of opportunities owned by the user.

        Example:
            >>> my_opps = await upsales.opportunities.get_by_user(10)
            >>> for opp in my_opps:
            ...     print(f"{opp.description}: ${opp.value}")
        """
        return await self.search(**{"user.id": user_id})

    async def get_by_stage(self, stage_id: int) -> list[Order]:
        """
        Get all opportunities in a specific stage.

        Args:
            stage_id: Stage ID to filter by.

        Returns:
            List of opportunities in the stage.

        Example:
            >>> qualified = await upsales.opportunities.get_by_stage(5)
            >>> proposal = await upsales.opportunities.get_by_stage(7)
        """
        return await self.search(**{"stage.id": stage_id})

    async def get_high_value(self, min_value: int = 100000) -> list[Order]:
        """
        Get opportunities above a value threshold.

        Args:
            min_value: Minimum opportunity value (default: 100000).

        Returns:
            List of opportunities with value >= min_value, sorted by value descending.

        Example:
            >>> high_value = await upsales.opportunities.get_high_value(100000)
            >>> enterprise = await upsales.opportunities.get_high_value(1000000)
            >>> for opp in high_value:
            ...     print(f"{opp.description}: ${opp.value}")
        """
        return await self.search(value=f">={min_value}", sort="-value")

    async def get_by_probability_range(
        self, min_probability: int = 0, max_probability: int = 100
    ) -> list[Order]:
        """
        Get opportunities within a probability range.

        Args:
            min_probability: Minimum win probability (0-100, default: 0).
            max_probability: Maximum win probability (0-100, default: 100).

        Returns:
            List of opportunities within the probability range.

        Example:
            >>> # High probability wins (75%+)
            >>> likely_wins = await upsales.opportunities.get_by_probability_range(75, 100)
            >>>
            >>> # Medium probability (25-75%)
            >>> medium = await upsales.opportunities.get_by_probability_range(25, 75)
            >>>
            >>> # Low probability (<25%)
            >>> long_shots = await upsales.opportunities.get_by_probability_range(0, 25)
        """
        return await self.search(
            probability=f">={min_probability}",
            probability_max=f"<={max_probability}",
            sort="-probability",
        )

    async def get_closing_soon(self, days: int = 30) -> list[Order]:
        """
        Get opportunities closing within the next N days.

        Args:
            days: Number of days to look ahead (default: 30).

        Returns:
            List of opportunities with closeDate within next N days, sorted by close date.

        Example:
            >>> # Opportunities closing this month
            >>> closing_soon = await upsales.opportunities.get_closing_soon(30)
            >>>
            >>> # Opportunities closing this week
            >>> this_week = await upsales.opportunities.get_closing_soon(7)
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
        Get all opportunities with recurring revenue.

        Returns:
            List of opportunities where monthlyValue or annualValue > 0.

        Example:
            >>> recurring = await upsales.opportunities.get_recurring()
            >>> total_mrr = sum(o.monthlyValue for o in recurring)
            >>> total_arr = sum(o.annualValue for o in recurring)
            >>> print(f"Total MRR: ${total_mrr}, Total ARR: ${total_arr}")
        """
        # Get all opportunities and filter client-side (API may not support OR filter)
        all_opportunities: list[Order] = await self.list_all()
        return [opp for opp in all_opportunities if opp.is_recurring]
