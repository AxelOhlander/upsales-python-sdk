"""
OpportunityAI resource manager for Upsales API.

This is a READ-ONLY resource that provides AI-analyzed opportunity data.
Does NOT support create/update/delete operations.

The endpoint structure is unusual:
- GET /opportunityAI: Returns list with single dict mapping opportunity IDs to AI data
- GET /opportunityAI/:id: Returns AI analysis for specific opportunity

Uses Python 3.13 features:
- Type parameter syntax [T, P] for clean generics
- Native type hints (no typing imports)
- Pattern matching for response handling
"""

from __future__ import annotations  # Required for type parameter syntax with subscripting

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from upsales.http import HTTPClient

from upsales.exceptions import UpsalesError
from upsales.models.opportunity_ai import OpportunityAI


class OpportunityAIResource:
    """
    Resource manager for OpportunityAI endpoint.

    This is a READ-ONLY resource - only GET operations are supported.
    The endpoint provides AI-analyzed opportunity data including activity
    tracking, decision maker involvement, and risk assessments.

    Args:
        http: HTTP client instance for making API requests.

    Attributes:
        _http: HTTP client for API requests.
        _endpoint: API endpoint path ("/opportunityAI").

    Example:
        >>> async with Upsales.from_env() as client:
        ...     # Get AI analysis for specific opportunity
        ...     ai_data = await client.opportunity_ai.get(45)
        ...     print(ai_data.is_decision_maker_involved)
        ...     print(ai_data.opportunity_description)
        ...
        ...     # Get all opportunities AI data
        ...     all_data = await client.opportunity_ai.get_all()
        ...     for opp_id, data in all_data.items():
        ...         print(f"Opportunity {opp_id}: {data}")

    Note:
        This resource does NOT support:
        - create() - No POST endpoint
        - update() - No PUT/PATCH endpoint
        - delete() - No DELETE endpoint
        - list() - Use get_all() instead for the special format
        - search() - Not applicable for this endpoint
    """

    def __init__(self, http: HTTPClient) -> None:
        """
        Initialize OpportunityAI resource manager.

        Args:
            http: HTTP client instance.
        """
        self._http = http
        self._endpoint = "/opportunityAI"

    async def get(self, opportunity_id: int) -> OpportunityAI:
        """
        Get AI analysis for a specific opportunity.

        Args:
            opportunity_id: ID of the opportunity to get AI data for.

        Returns:
            OpportunityAI object with complete AI analysis.

        Raises:
            NotFoundError: If opportunity ID doesn't exist.
            AuthenticationError: If API token is invalid.
            ServerError: If server error occurs.

        Example:
            >>> async with Upsales.from_env() as client:
            ...     ai_data = await client.opportunity_ai.get(45)
            ...     print(f"Decision maker involved: {ai_data.is_decision_maker_involved}")
            ...     print(f"Value: {ai_data.opportunity_value}")
        """
        response = await self._http.get(f"{self._endpoint}/{opportunity_id}")
        data = response.get("data", {})

        # Inject _client reference for potential future methods
        return OpportunityAI.model_validate(data, context={"_client": self._http})

    async def get_all(self) -> dict[int, dict[str, Any]]:
        """
        Get AI analysis for all opportunities.

        The API returns a list containing a single dict that maps opportunity IDs
        to their AI analysis. This method extracts that dict and converts string
        keys to integers for easier use.

        Returns:
            Dictionary mapping opportunity IDs (int) to AI analysis data (dict).
            Each value contains: meeting, activity, allActivity, notOld,
            confirmedDate, confirmedBudget, confirmedSolution, notPassedDate,
            todo, phonecall, futurePhonecall, checklist.

        Raises:
            AuthenticationError: If API token is invalid.
            ServerError: If server error occurs.
            UpsalesError: If response format is unexpected.

        Example:
            >>> async with Upsales.from_env() as client:
            ...     all_data = await client.opportunity_ai.get_all()
            ...     for opp_id, data in all_data.items():
            ...         print(f"Opportunity {opp_id}:")
            ...         if data.get('meeting'):
            ...             print(f"  Meeting: {data['meeting']['description']}")
            ...         print(f"  Confirmed budget: {data['confirmedBudget']}")

        Note:
            This endpoint returns a different structure than get():
            - get(): Returns full OpportunityAI object with nested opportunity
            - get_all(): Returns simplified analysis data without full opportunity details
        """
        response = await self._http.get(self._endpoint)
        data = response.get("data", [])

        # API returns list with single dict mapping opportunity IDs to data
        if not isinstance(data, list) or len(data) == 0:
            raise UpsalesError(
                f"Unexpected response format from {self._endpoint}: "
                f"expected list with one item, got {type(data)}"
            )

        opportunities_data = data[0]
        if not isinstance(opportunities_data, dict):
            raise UpsalesError(
                f"Unexpected data format from {self._endpoint}: "
                f"expected dict, got {type(opportunities_data)}"
            )

        # Convert string keys to integers for easier use
        return {int(opp_id): ai_data for opp_id, ai_data in opportunities_data.items()}
