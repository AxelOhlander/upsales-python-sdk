"""
Sales Coaches resource manager for Upsales API.

Provides methods to interact with the /salesCoaches endpoint.

Example:
    >>> async with Upsales.from_env() as upsales:
    ...     # Get a sales coach
    ...     coach = await upsales.sales_coaches.get(1)
    ...     print(f"Coach: {coach.name}")
    ...
    ...     # List all active coaches
    ...     coaches = await upsales.sales_coaches.list_active()
    ...
    ...     # Update coach settings
    ...     await upsales.sales_coaches.update(1, budgetActive=True)
"""

from upsales.http import HTTPClient
from upsales.models.sales_coaches import PartialSalesCoach, SalesCoach
from upsales.resources.base import BaseResource


class SalesCoachesResource(BaseResource[SalesCoach, PartialSalesCoach]):
    """
    Resource manager for Sales Coaches endpoint.

    Sales Coaches help teams qualify opportunities using the BANT methodology
    (Budget, Authority, Need, Timing). This resource provides standard CRUD
    operations plus helper methods for filtering and searching coaches.

    Inherits standard CRUD operations from BaseResource:
    - get(id) - Get single sales coach
    - list(limit, offset, **params) - List coaches with pagination
    - list_all(**params) - Auto-paginated list of all coaches
    - create(**data) - Create new coach
    - update(id, **data) - Update coach
    - delete(id) - Delete coach
    - bulk_update(ids, data, max_concurrent) - Parallel updates
    - bulk_delete(ids, max_concurrent) - Parallel deletes

    Example:
        >>> # Get a specific coach
        >>> coach = await upsales.sales_coaches.get(1)
        >>> print(f"Coach: {coach.name}")
        >>>
        >>> # List all coaches
        >>> all_coaches = await upsales.sales_coaches.list_all()
        >>>
        >>> # Get only active coaches
        >>> active_coaches = await upsales.sales_coaches.list_active()
        >>>
        >>> # Find coach by name
        >>> coach = await upsales.sales_coaches.get_by_name("Enterprise Sales")
    """

    def __init__(self, http: HTTPClient):
        """
        Initialize sales coaches resource manager.

        Args:
            http: HTTP client for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/salesCoaches",
            model_class=SalesCoach,
            partial_class=PartialSalesCoach,
        )

    async def list_active(self) -> list[SalesCoach]:
        """
        Get all active sales coaches.

        Returns:
            List of active sales coaches (where active=True).

        Example:
            >>> active_coaches = await upsales.sales_coaches.list_active()
            >>> for coach in active_coaches:
            ...     print(f"Active coach: {coach.name}")
        """
        all_coaches: list[SalesCoach] = await self.list_all()
        return [coach for coach in all_coaches if coach.active]

    async def get_by_name(self, name: str) -> SalesCoach | None:
        """
        Get sales coach by name.

        Performs case-insensitive search for exact name match.

        Args:
            name: Sales coach name to search for.

        Returns:
            SalesCoach object if found, None otherwise.

        Example:
            >>> coach = await upsales.sales_coaches.get_by_name("Enterprise Sales")
            >>> if coach:
            ...     print(f"Found coach with ID: {coach.id}")
            ... else:
            ...     print("Coach not found")
        """
        all_coaches: list[SalesCoach] = await self.list_all()
        for coach in all_coaches:
            if coach.name.lower() == name.lower():
                return coach
        return None

    async def list_with_budget_tracking(self) -> list[SalesCoach]:
        """
        Get all coaches with budget tracking enabled.

        Returns:
            List of coaches where budgetActive=True.

        Example:
            >>> budget_coaches = await upsales.sales_coaches.list_with_budget_tracking()
            >>> print(f"Found {len(budget_coaches)} coaches tracking budget")
        """
        all_coaches: list[SalesCoach] = await self.list_all()
        return [coach for coach in all_coaches if coach.budgetActive]

    async def list_with_decision_maker_tracking(self) -> list[SalesCoach]:
        """
        Get all coaches with decision maker tracking enabled.

        Returns:
            List of coaches where decisionMakersActive=True.

        Example:
            >>> dm_coaches = await upsales.sales_coaches.list_with_decision_maker_tracking()
            >>> for coach in dm_coaches:
            ...     print(f"{coach.name}: {len(coach.decisionMakersTitles)} required titles")
        """
        all_coaches: list[SalesCoach] = await self.list_all()
        return [coach for coach in all_coaches if coach.decisionMakersActive]

    async def list_with_full_bant(self) -> list[SalesCoach]:
        """
        Get all coaches with full BANT tracking enabled.

        Returns coaches where all four BANT dimensions are enabled:
        - budgetActive (Budget)
        - decisionMakersActive (Authority)
        - solutionActive (Need)
        - timeframeActive (Timing)

        Returns:
            List of coaches with all BANT dimensions enabled.

        Example:
            >>> full_bant_coaches = await upsales.sales_coaches.list_with_full_bant()
            >>> print(f"{len(full_bant_coaches)} coaches use complete BANT methodology")
        """
        all_coaches: list[SalesCoach] = await self.list_all()
        return [
            coach
            for coach in all_coaches
            if (
                coach.budgetActive
                and coach.decisionMakersActive
                and coach.solutionActive
                and coach.timeframeActive
            )
        ]

    async def list_assigned_to_user(self, user_id: int) -> list[SalesCoach]:
        """
        Get all coaches assigned to a specific user.

        Args:
            user_id: User ID to filter by.

        Returns:
            List of coaches where user_id is in the users list.

        Example:
            >>> user_coaches = await upsales.sales_coaches.list_assigned_to_user(123)
            >>> print(f"User has {len(user_coaches)} assigned coaches")
        """
        all_coaches: list[SalesCoach] = await self.list_all()
        return [coach for coach in all_coaches if user_id in coach.users]

    async def list_assigned_to_role(self, role_id: int) -> list[SalesCoach]:
        """
        Get all coaches assigned to a specific role.

        Args:
            role_id: Role ID to filter by.

        Returns:
            List of coaches where role_id is in the roles list.

        Example:
            >>> role_coaches = await upsales.sales_coaches.list_assigned_to_role(5)
            >>> for coach in role_coaches:
            ...     print(f"Role can use: {coach.name}")
        """
        all_coaches: list[SalesCoach] = await self.list_all()
        return [coach for coach in all_coaches if role_id in coach.roles]
