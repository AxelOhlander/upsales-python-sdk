"""
Unit tests for JourneyStepsResource.

Tests list operations and custom methods for journey steps endpoint.
Journey steps are typically read-only and don't support standard CRUD operations.
"""

import pytest
from pytest_httpx import HTTPXMock

from upsales.http import HTTPClient
from upsales.models.journey_step import JourneyStep
from upsales.resources.journey_steps import JourneyStepsResource


class TestJourneyStepsResourceOperations:
    """Test operations for JourneyStepsResource."""

    @pytest.fixture
    def sample_journey_steps(self):
        """Sample journey steps data for testing."""
        return [
            {
                "name": "Lead",
                "value": "lead",
                "priority": 1,
                "color": "#B254E0",
                "colorName": "bright-purple",
            },
            {
                "name": "Marketing Qualified Lead (MQL)",
                "value": "mql",
                "priority": 2,
                "color": "#721A94",
                "colorName": "purple",
            },
            {
                "name": "Tilldelad",
                "value": "assigned",
                "priority": 3,
                "color": "#4A90E2",
                "colorName": "bright-blue",
            },
            {
                "name": "Sales Qualified Lead (SQL)",
                "value": "sql",
                "priority": 4,
                "color": "#3367C0",
                "colorName": "medium-blue",
            },
            {
                "name": "Pipeline",
                "value": "pipeline",
                "priority": 5,
                "color": "#002F65",
                "colorName": "blue",
            },
            {
                "name": "Förlorad affärsmöjlighet",
                "value": "lost_opportunity",
                "priority": 6,
                "color": "#6B7C93",
                "colorName": "grey-10",
            },
            {
                "name": "Kund",
                "value": "customer",
                "priority": 7,
                "color": "#5CB85C",
                "colorName": "bright-green",
            },
            {
                "name": "Diskvalificerad",
                "value": "disqualified",
                "priority": 8,
                "color": "#D33F42",
                "colorName": "red",
            },
            {
                "name": "Förlorad kund",
                "value": "lost_customer",
                "priority": 9,
                "color": "#6B7C93",
                "colorName": "grey-10",
            },
        ]

    @pytest.mark.asyncio
    async def test_list_all(self, httpx_mock: HTTPXMock, sample_journey_steps):
        """Test listing all journey steps."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/journeySteps",
            json={"error": None, "data": sample_journey_steps},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = JourneyStepsResource(http)
            results = await resource.list_all()

            assert len(results) == 9
            assert all(isinstance(step, JourneyStep) for step in results)
            assert results[0].name == "Lead"
            assert results[0].value == "lead"
            assert results[0].priority == 1
            assert results[0].color == "#B254E0"

    @pytest.mark.asyncio
    async def test_list_all_empty(self, httpx_mock: HTTPXMock):
        """Test list_all with empty response."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/journeySteps",
            json={"error": None, "data": []},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = JourneyStepsResource(http)
            results = await resource.list_all()

            assert len(results) == 0
            assert isinstance(results, list)


class TestJourneyStepsResourceCustomMethods:
    """Test custom methods specific to JourneyStepsResource."""

    @pytest.fixture
    def sample_journey_steps(self):
        """Sample journey steps for custom method testing."""
        return [
            {
                "name": "Lead",
                "value": "lead",
                "priority": 1,
                "color": "#B254E0",
                "colorName": "bright-purple",
            },
            {
                "name": "Marketing Qualified Lead (MQL)",
                "value": "mql",
                "priority": 2,
                "color": "#721A94",
                "colorName": "purple",
            },
            {
                "name": "Tilldelad",
                "value": "assigned",
                "priority": 3,
                "color": "#4A90E2",
                "colorName": "bright-blue",
            },
            {
                "name": "Sales Qualified Lead (SQL)",
                "value": "sql",
                "priority": 4,
                "color": "#3367C0",
                "colorName": "medium-blue",
            },
            {
                "name": "Pipeline",
                "value": "pipeline",
                "priority": 5,
                "color": "#002F65",
                "colorName": "blue",
            },
            {
                "name": "Förlorad affärsmöjlighet",
                "value": "lost_opportunity",
                "priority": 6,
                "color": "#6B7C93",
                "colorName": "grey-10",
            },
            {
                "name": "Kund",
                "value": "customer",
                "priority": 7,
                "color": "#5CB85C",
                "colorName": "bright-green",
            },
            {
                "name": "Diskvalificerad",
                "value": "disqualified",
                "priority": 8,
                "color": "#D33F42",
                "colorName": "red",
            },
            {
                "name": "Förlorad kund",
                "value": "lost_customer",
                "priority": 9,
                "color": "#6B7C93",
                "colorName": "grey-10",
            },
        ]

    @pytest.mark.asyncio
    async def test_get_by_value(self, httpx_mock: HTTPXMock, sample_journey_steps):
        """Test get_by_value() custom method."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/journeySteps",
            json={"error": None, "data": sample_journey_steps},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = JourneyStepsResource(http)
            result = await resource.get_by_value("customer")

            assert result is not None
            assert isinstance(result, JourneyStep)
            assert result.value == "customer"
            assert result.name == "Kund"
            assert result.priority == 7
            assert result.is_customer_stage

    @pytest.mark.asyncio
    async def test_get_by_value_not_found(self, httpx_mock: HTTPXMock, sample_journey_steps):
        """Test get_by_value() when step not found."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/journeySteps",
            json={"error": None, "data": sample_journey_steps},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = JourneyStepsResource(http)
            result = await resource.get_by_value("nonexistent")

            assert result is None

    @pytest.mark.asyncio
    async def test_get_by_name(self, httpx_mock: HTTPXMock, sample_journey_steps):
        """Test get_by_name() custom method."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/journeySteps",
            json={"error": None, "data": sample_journey_steps},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = JourneyStepsResource(http)
            result = await resource.get_by_name("Marketing Qualified Lead (MQL)")

            assert result is not None
            assert isinstance(result, JourneyStep)
            assert result.name == "Marketing Qualified Lead (MQL)"
            assert result.value == "mql"
            assert result.is_lead_stage

    @pytest.mark.asyncio
    async def test_get_by_name_not_found(self, httpx_mock: HTTPXMock, sample_journey_steps):
        """Test get_by_name() when step not found."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/journeySteps",
            json={"error": None, "data": sample_journey_steps},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = JourneyStepsResource(http)
            result = await resource.get_by_name("Nonexistent Step")

            assert result is None

    @pytest.mark.asyncio
    async def test_get_lead_stages(self, httpx_mock: HTTPXMock, sample_journey_steps):
        """Test get_lead_stages() custom method."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/journeySteps",
            json={"error": None, "data": sample_journey_steps},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = JourneyStepsResource(http)
            results = await resource.get_lead_stages()

            assert len(results) == 4
            assert all(isinstance(step, JourneyStep) for step in results)
            assert all(step.is_lead_stage for step in results)
            expected_values = {"lead", "mql", "sql", "assigned"}
            assert {step.value for step in results} == expected_values

    @pytest.mark.asyncio
    async def test_get_customer_stages(self, httpx_mock: HTTPXMock, sample_journey_steps):
        """Test get_customer_stages() custom method."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/journeySteps",
            json={"error": None, "data": sample_journey_steps},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = JourneyStepsResource(http)
            results = await resource.get_customer_stages()

            assert len(results) == 2
            assert all(isinstance(step, JourneyStep) for step in results)
            assert all(step.is_customer_stage for step in results)
            expected_values = {"customer", "lost_customer"}
            assert {step.value for step in results} == expected_values

    @pytest.mark.asyncio
    async def test_get_by_priority_range(self, httpx_mock: HTTPXMock, sample_journey_steps):
        """Test get_by_priority_range() custom method."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/journeySteps",
            json={"error": None, "data": sample_journey_steps},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = JourneyStepsResource(http)
            results = await resource.get_by_priority_range(1, 4)

            assert len(results) == 4
            assert all(isinstance(step, JourneyStep) for step in results)
            assert all(1 <= step.priority <= 4 for step in results)
            # Verify sorted by priority
            assert results[0].priority == 1
            assert results[1].priority == 2
            assert results[2].priority == 3
            assert results[3].priority == 4

    @pytest.mark.asyncio
    async def test_get_sorted_by_priority(self, httpx_mock: HTTPXMock, sample_journey_steps):
        """Test get_sorted_by_priority() custom method."""
        # Shuffle the data to test sorting
        import random

        shuffled = sample_journey_steps.copy()
        random.shuffle(shuffled)

        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/journeySteps",
            json={"error": None, "data": shuffled},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = JourneyStepsResource(http)
            results = await resource.get_sorted_by_priority()

            assert len(results) == 9
            assert all(isinstance(step, JourneyStep) for step in results)
            # Verify sorted ascending by priority
            priorities = [step.priority for step in results]
            assert priorities == sorted(priorities)
            assert results[0].priority == 1
            assert results[-1].priority == 9


class TestJourneyStepModelComputedFields:
    """Test computed fields on JourneyStep model."""

    @pytest.fixture
    def sample_journey_steps(self):
        """Sample journey steps for testing computed fields."""
        return [
            {
                "name": "Lead",
                "value": "lead",
                "priority": 1,
                "color": "#B254E0",
                "colorName": "bright-purple",
            },
            {
                "name": "Pipeline",
                "value": "pipeline",
                "priority": 5,
                "color": "#002F65",
                "colorName": "blue",
            },
            {
                "name": "Kund",
                "value": "customer",
                "priority": 7,
                "color": "#5CB85C",
                "colorName": "bright-green",
            },
            {
                "name": "Diskvalificerad",
                "value": "disqualified",
                "priority": 8,
                "color": "#D33F42",
                "colorName": "red",
            },
        ]

    @pytest.mark.asyncio
    async def test_is_lead_stage_computed_field(self, httpx_mock: HTTPXMock, sample_journey_steps):
        """Test is_lead_stage computed field."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/journeySteps",
            json={"error": None, "data": sample_journey_steps},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = JourneyStepsResource(http)
            results = await resource.list_all()

            # Lead should be a lead stage
            lead = next(s for s in results if s.value == "lead")
            assert lead.is_lead_stage
            assert not lead.is_customer_stage
            assert not lead.is_opportunity_stage
            assert not lead.is_negative_outcome

    @pytest.mark.asyncio
    async def test_is_opportunity_stage_computed_field(
        self, httpx_mock: HTTPXMock, sample_journey_steps
    ):
        """Test is_opportunity_stage computed field."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/journeySteps",
            json={"error": None, "data": sample_journey_steps},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = JourneyStepsResource(http)
            results = await resource.list_all()

            # Pipeline should be an opportunity stage
            pipeline = next(s for s in results if s.value == "pipeline")
            assert pipeline.is_opportunity_stage
            assert not pipeline.is_lead_stage
            assert not pipeline.is_customer_stage
            assert not pipeline.is_negative_outcome

    @pytest.mark.asyncio
    async def test_is_customer_stage_computed_field(
        self, httpx_mock: HTTPXMock, sample_journey_steps
    ):
        """Test is_customer_stage computed field."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/journeySteps",
            json={"error": None, "data": sample_journey_steps},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = JourneyStepsResource(http)
            results = await resource.list_all()

            # Customer should be a customer stage
            customer = next(s for s in results if s.value == "customer")
            assert customer.is_customer_stage
            assert not customer.is_lead_stage
            assert not customer.is_opportunity_stage
            assert not customer.is_negative_outcome

    @pytest.mark.asyncio
    async def test_is_negative_outcome_computed_field(
        self, httpx_mock: HTTPXMock, sample_journey_steps
    ):
        """Test is_negative_outcome computed field."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/journeySteps",
            json={"error": None, "data": sample_journey_steps},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = JourneyStepsResource(http)
            results = await resource.list_all()

            # Disqualified should be a negative outcome
            disqualified = next(s for s in results if s.value == "disqualified")
            assert disqualified.is_negative_outcome
            assert not disqualified.is_lead_stage
            assert not disqualified.is_customer_stage
            assert not disqualified.is_opportunity_stage
