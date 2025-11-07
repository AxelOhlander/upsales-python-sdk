"""
Journey steps resource manager for Upsales API.

Journey steps are system-defined stages in the customer lifecycle.
This is typically a read-only configuration endpoint.
"""

from upsales.http import HTTPClient
from upsales.models.journey_step import JourneyStep


class JourneyStepsResource:
    """
    Resource manager for journey steps (customer lifecycle stages).

    Journey steps represent stages in the customer journey such as Lead,
    MQL (Marketing Qualified Lead), SQL (Sales Qualified Lead), Pipeline,
    Customer, etc.

    This is a read-only endpoint in most Upsales installations and does not
    support standard CRUD operations. It only supports listing all journey steps.

    Note: Unlike other resources, journey steps use 'value' as the identifier
    instead of 'id' (e.g., "lead", "mql", "customer").

    Example:
        >>> # Get all journey steps
        >>> steps = await upsales.journey_steps.list_all()
        >>> for step in steps:
        ...     print(f"{step.name} ({step.value})")
        Lead (lead)
        Marketing Qualified Lead (MQL) (mql)

        >>> # Get a specific journey step by value
        >>> customer_step = await upsales.journey_steps.get_by_value("customer")
        >>> print(f"Customer stage: {customer_step.name}")
    """

    def __init__(self, http: HTTPClient):
        """
        Initialize journey steps resource manager.

        Args:
            http: HTTP client for making API requests.
        """
        self.http = http
        self._endpoint = "/journeySteps"

    async def list_all(self) -> list[JourneyStep]:
        """
        Get all journey steps.

        Journey steps are typically a small, fixed set of system-defined stages,
        so this returns all available journey steps in a single request.

        Returns:
            List of all journey step instances.

        Raises:
            UpsalesError: If the API request fails.

        Example:
            >>> steps = await upsales.journey_steps.list_all()
            >>> print(f"Found {len(steps)} journey steps")
            >>> for step in steps:
            ...     print(f"  {step.priority}. {step.name} ({step.value})")
            Found 9 journey steps
              1. Lead (lead)
              2. Marketing Qualified Lead (MQL) (mql)
              3. Tilldelad (assigned)
        """
        response = await self.http.request("GET", self._endpoint)
        items = response if isinstance(response, list) else response.get("data", [])
        return [
            JourneyStep.model_validate(item, context={"client": self.http._client})
            for item in items
        ]

    async def get_by_value(self, value: str) -> JourneyStep | None:
        """
        Get a specific journey step by its value identifier.

        Args:
            value: Unique value identifier (e.g., "lead", "mql", "customer").

        Returns:
            Journey step if found, None otherwise.

        Raises:
            UpsalesError: If the API request fails.

        Example:
            >>> # Get customer journey step
            >>> customer = await upsales.journey_steps.get_by_value("customer")
            >>> if customer:
            ...     print(f"Customer step: {customer.name} (priority {customer.priority})")
            Customer step: Kund (priority 7)

            >>> # Check for non-existent step
            >>> unknown = await upsales.journey_steps.get_by_value("nonexistent")
            >>> print(unknown)  # None
        """
        steps = await self.list_all()
        return next((step for step in steps if step.value == value), None)

    async def get_by_name(self, name: str) -> JourneyStep | None:
        """
        Get a specific journey step by its display name.

        Args:
            name: Display name of the journey step (case-sensitive).

        Returns:
            Journey step if found, None otherwise.

        Raises:
            UpsalesError: If the API request fails.

        Example:
            >>> # Get by exact name
            >>> mql = await upsales.journey_steps.get_by_name("Marketing Qualified Lead (MQL)")
            >>> if mql:
            ...     print(f"MQL value: {mql.value}")
            MQL value: mql
        """
        steps = await self.list_all()
        return next((step for step in steps if step.name == name), None)

    async def get_lead_stages(self) -> list[JourneyStep]:
        """
        Get all lead-related journey steps.

        Returns journey steps that represent lead stages (lead, mql, sql, assigned).

        Returns:
            List of lead-stage journey steps.

        Raises:
            UpsalesError: If the API request fails.

        Example:
            >>> lead_stages = await upsales.journey_steps.get_lead_stages()
            >>> for stage in lead_stages:
            ...     print(f"  {stage.name} ({stage.value})")
              Lead (lead)
              Marketing Qualified Lead (MQL) (mql)
              Tilldelad (assigned)
              Sales Qualified Lead (SQL) (sql)
        """
        steps = await self.list_all()
        return [step for step in steps if step.is_lead_stage]

    async def get_customer_stages(self) -> list[JourneyStep]:
        """
        Get all customer-related journey steps.

        Returns journey steps that represent customer status (customer, lost_customer).

        Returns:
            List of customer-stage journey steps.

        Raises:
            UpsalesError: If the API request fails.

        Example:
            >>> customer_stages = await upsales.journey_steps.get_customer_stages()
            >>> for stage in customer_stages:
            ...     print(f"  {stage.name} ({stage.value})")
              Kund (customer)
              Förlorad kund (lost_customer)
        """
        steps = await self.list_all()
        return [step for step in steps if step.is_customer_stage]

    async def get_by_priority_range(
        self, min_priority: int, max_priority: int
    ) -> list[JourneyStep]:
        """
        Get journey steps within a specific priority range.

        Args:
            min_priority: Minimum priority value (inclusive).
            max_priority: Maximum priority value (inclusive).

        Returns:
            List of journey steps within the priority range, sorted by priority.

        Raises:
            UpsalesError: If the API request fails.

        Example:
            >>> # Get early-stage journey steps (priorities 1-4)
            >>> early_stages = await upsales.journey_steps.get_by_priority_range(1, 4)
            >>> for stage in early_stages:
            ...     print(f"  {stage.priority}. {stage.name}")
              1. Lead
              2. Marketing Qualified Lead (MQL)
              3. Tilldelad
              4. Sales Qualified Lead (SQL)
        """
        steps = await self.list_all()
        filtered = [step for step in steps if min_priority <= step.priority <= max_priority]
        return sorted(filtered, key=lambda s: s.priority)

    async def get_sorted_by_priority(self) -> list[JourneyStep]:
        """
        Get all journey steps sorted by priority.

        Returns:
            List of all journey steps ordered by priority (ascending).

        Raises:
            UpsalesError: If the API request fails.

        Example:
            >>> steps = await upsales.journey_steps.get_sorted_by_priority()
            >>> for step in steps:
            ...     print(f"{step.priority}. {step.name} ({step.color})")
            1. Lead (#B254E0)
            2. Marketing Qualified Lead (MQL) (#721A94)
            3. Tilldelad (#4A90E2)
        """
        steps = await self.list_all()
        return sorted(steps, key=lambda s: s.priority)
