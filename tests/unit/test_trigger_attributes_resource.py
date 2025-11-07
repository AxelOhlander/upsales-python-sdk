"""
Unit tests for TriggerAttributesResource.

Note: TriggerAttributes endpoint is different from standard CRUD resources:
- Returns dict by entity type (not a list)
- Read-only (no create/update/delete)
- Contains attribute definitions for automation triggers

Tests cover:
- get() - Get all trigger attributes
- get_entity_attributes() - Get attributes for specific entity
- get_criteria_attributes() - Get only criteria attributes
- get_attribute_by_id() - Get single attribute by ID
- find_attributes_by_type() - Find attributes by data type
- get_select_attributes() - Get select/dropdown attributes
- get_attributes_by_feature() - Get attributes by feature flag
- get_entity_types() - Get list of entity types
"""

import pytest
from pytest_httpx import HTTPXMock

from upsales.http import HTTPClient
from upsales.models.trigger_attributes import TriggerAttribute, TriggerAttributes
from upsales.resources.trigger_attributes import TriggerAttributesResource


class TestTriggerAttributesResource:
    """Test TriggerAttributesResource operations."""

    @pytest.fixture
    def sample_trigger_attributes(self):
        """Sample trigger attributes data for testing."""
        return {
            "Client": [
                {
                    "id": "Client.Name",
                    "name": "Name",
                    "type": "string",
                    "lang": "default.name",
                    "asCriteria": True,
                },
                {
                    "id": "Client.Phone",
                    "name": "Phone",
                    "type": "string",
                    "lang": "default.phone",
                    "asCriteria": True,
                },
                {
                    "id": "Client.UserId",
                    "name": "UserId",
                    "type": "user",
                    "lang": "default.accountManager",
                    "selectText": "name",
                    "asCriteria": True,
                },
                {
                    "id": "Client.Country",
                    "name": "Country",
                    "type": "country",
                    "lang": "address.country",
                    "selectText": "lang",
                    "asCriteria": False,
                },
                {
                    "id": "Client.RegistrationDate",
                    "name": "RegistrationDate",
                    "type": "date",
                    "lang": "default.founded",
                    "feature": "NEW_FIELDS",
                    "asCriteria": True,
                },
            ],
            "Contact": [
                {
                    "id": "Contact.Name",
                    "name": "Name",
                    "type": "string",
                    "lang": "default.name",
                    "asCriteria": True,
                },
                {
                    "id": "Contact.Email",
                    "name": "Email",
                    "type": "string",
                    "lang": "default.email",
                    "asCriteria": True,
                },
                {
                    "id": "Contact.Active",
                    "name": "Active",
                    "type": "boolean",
                    "lang": "default.active",
                    "asCriteria": True,
                },
            ],
            "Order": [
                {
                    "id": "Order.Description",
                    "name": "Description",
                    "type": "string",
                    "lang": "default.description",
                    "asCriteria": True,
                },
                {
                    "id": "Order.Probability",
                    "name": "Probability",
                    "type": "integer",
                    "min": 0,
                    "max": 100,
                    "lang": "default.probability",
                    "asCriteria": True,
                },
            ],
        }

    @pytest.fixture
    def sample_api_response(self, sample_trigger_attributes):
        """Sample API response for trigger attributes."""
        return {"error": None, "data": sample_trigger_attributes}

    @pytest.mark.asyncio
    async def test_get(self, httpx_mock: HTTPXMock, sample_api_response):
        """Test getting all trigger attributes."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/triggerAttributes",
            json=sample_api_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = TriggerAttributesResource(http)
            result = await resource.get()

            assert isinstance(result, TriggerAttributes)
            assert len(result.entity_types) == 3
            assert "Client" in result.entity_types
            assert "Contact" in result.entity_types
            assert "Order" in result.entity_types
            assert result.total_attributes == 10

    @pytest.mark.asyncio
    async def test_get_entity_attributes(self, httpx_mock: HTTPXMock, sample_api_response):
        """Test getting attributes for specific entity."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/triggerAttributes",
            json=sample_api_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = TriggerAttributesResource(http)
            results = await resource.get_entity_attributes("Client")

            assert isinstance(results, list)
            assert len(results) == 5
            assert all(isinstance(attr, TriggerAttribute) for attr in results)
            assert results[0].id == "Client.Name"
            assert results[0].name == "Name"
            assert results[0].type == "string"

    @pytest.mark.asyncio
    async def test_get_criteria_attributes(self, httpx_mock: HTTPXMock, sample_api_response):
        """Test getting only criteria attributes."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/triggerAttributes",
            json=sample_api_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = TriggerAttributesResource(http)
            results = await resource.get_criteria_attributes("Client")

            assert isinstance(results, list)
            assert len(results) == 4  # Country has asCriteria=False
            assert all(attr.can_be_criteria for attr in results)
            assert all(attr.asCriteria for attr in results)
            # Country should not be in results
            assert not any(attr.id == "Client.Country" for attr in results)

    @pytest.mark.asyncio
    async def test_get_attribute_by_id(self, httpx_mock: HTTPXMock, sample_api_response):
        """Test getting single attribute by ID."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/triggerAttributes",
            json=sample_api_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = TriggerAttributesResource(http)
            result = await resource.get_attribute_by_id("Client.Name")

            assert result is not None
            assert isinstance(result, TriggerAttribute)
            assert result.id == "Client.Name"
            assert result.name == "Name"
            assert result.type == "string"
            assert result.can_be_criteria is True

    @pytest.mark.asyncio
    async def test_get_attribute_by_id_not_found(self, httpx_mock: HTTPXMock, sample_api_response):
        """Test getting non-existent attribute returns None."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/triggerAttributes",
            json=sample_api_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = TriggerAttributesResource(http)
            result = await resource.get_attribute_by_id("NonExistent.Field")

            assert result is None

    @pytest.mark.asyncio
    async def test_find_attributes_by_type_all_entities(
        self, httpx_mock: HTTPXMock, sample_api_response
    ):
        """Test finding attributes by type across all entities."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/triggerAttributes",
            json=sample_api_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = TriggerAttributesResource(http)
            results = await resource.find_attributes_by_type("string")

            assert isinstance(results, list)
            assert (
                len(results) == 5
            )  # Client.Name, Client.Phone, Contact.Name, Contact.Email, Order.Description
            assert all(attr.type == "string" for attr in results)

    @pytest.mark.asyncio
    async def test_find_attributes_by_type_single_entity(
        self, httpx_mock: HTTPXMock, sample_api_response
    ):
        """Test finding attributes by type for single entity."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/triggerAttributes",
            json=sample_api_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = TriggerAttributesResource(http)
            results = await resource.find_attributes_by_type("string", "Client")

            assert isinstance(results, list)
            assert len(results) == 2  # Client.Name, Client.Phone
            assert all(attr.type == "string" for attr in results)
            assert all(attr.entity_type == "Client" for attr in results)

    @pytest.mark.asyncio
    async def test_get_select_attributes(self, httpx_mock: HTTPXMock, sample_api_response):
        """Test getting select/dropdown type attributes."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/triggerAttributes",
            json=sample_api_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = TriggerAttributesResource(http)
            results = await resource.get_select_attributes("Client")

            assert isinstance(results, list)
            assert len(results) == 2  # Client.UserId, Client.Country
            assert all(attr.is_select_type for attr in results)
            assert all(attr.selectText is not None for attr in results)

    @pytest.mark.asyncio
    async def test_get_attributes_by_feature(self, httpx_mock: HTTPXMock, sample_api_response):
        """Test getting attributes by feature flag."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/triggerAttributes",
            json=sample_api_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = TriggerAttributesResource(http)
            results = await resource.get_attributes_by_feature("NEW_FIELDS")

            assert isinstance(results, list)
            assert len(results) == 1  # Client.RegistrationDate
            assert all(attr.feature == "NEW_FIELDS" for attr in results)
            assert results[0].id == "Client.RegistrationDate"

    @pytest.mark.asyncio
    async def test_get_entity_types(self, httpx_mock: HTTPXMock, sample_api_response):
        """Test getting list of entity types."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/triggerAttributes",
            json=sample_api_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = TriggerAttributesResource(http)
            results = await resource.get_entity_types()

            assert isinstance(results, list)
            assert len(results) == 3
            assert "Client" in results
            assert "Contact" in results
            assert "Order" in results
            # Should be sorted
            assert results == sorted(results)

    @pytest.mark.asyncio
    async def test_trigger_attribute_computed_fields(
        self, httpx_mock: HTTPXMock, sample_api_response
    ):
        """Test TriggerAttribute model computed fields."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/triggerAttributes",
            json=sample_api_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = TriggerAttributesResource(http)
            attr = await resource.get_attribute_by_id("Client.Name")

            assert attr is not None
            assert attr.can_be_criteria is True
            assert attr.is_select_type is False
            assert attr.has_range is False
            assert attr.requires_feature is False
            assert attr.entity_type == "Client"
            assert attr.field_name == "Name"

    @pytest.mark.asyncio
    async def test_trigger_attribute_select_type(self, httpx_mock: HTTPXMock, sample_api_response):
        """Test TriggerAttribute select type attributes."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/triggerAttributes",
            json=sample_api_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = TriggerAttributesResource(http)
            attr = await resource.get_attribute_by_id("Client.UserId")

            assert attr is not None
            assert attr.is_select_type is True
            assert attr.selectText == "name"

    @pytest.mark.asyncio
    async def test_trigger_attribute_with_range(self, httpx_mock: HTTPXMock, sample_api_response):
        """Test TriggerAttribute with min/max range."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/triggerAttributes",
            json=sample_api_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = TriggerAttributesResource(http)
            attr = await resource.get_attribute_by_id("Order.Probability")

            assert attr is not None
            assert attr.has_range is True
            assert attr.min == 0
            assert attr.max == 100

    @pytest.mark.asyncio
    async def test_trigger_attribute_with_feature(self, httpx_mock: HTTPXMock, sample_api_response):
        """Test TriggerAttribute with feature flag."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/triggerAttributes",
            json=sample_api_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = TriggerAttributesResource(http)
            attr = await resource.get_attribute_by_id("Client.RegistrationDate")

            assert attr is not None
            assert attr.requires_feature is True
            assert attr.feature == "NEW_FIELDS"

    @pytest.mark.asyncio
    async def test_trigger_attributes_model_methods(
        self, httpx_mock: HTTPXMock, sample_api_response
    ):
        """Test TriggerAttributes model helper methods."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/triggerAttributes",
            json=sample_api_response,
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            resource = TriggerAttributesResource(http)
            attrs = await resource.get()

            # Test get_entity_attributes
            client_attrs = attrs.get_entity_attributes("Client")
            assert len(client_attrs) == 5

            # Test get_criteria_attributes
            criteria = attrs.get_criteria_attributes("Client")
            assert len(criteria) == 4
            assert all(attr.can_be_criteria for attr in criteria)

            # Test get_attribute_by_id
            attr = attrs.get_attribute_by_id("Contact.Email")
            assert attr is not None
            assert attr.name == "Email"

            # Test find_attributes_by_type
            string_attrs = attrs.find_attributes_by_type("string")
            assert len(string_attrs) == 5

            # Test get_select_attributes
            selects = attrs.get_select_attributes("Client")
            assert len(selects) == 2

            # Test get_attributes_by_feature
            feature_attrs = attrs.get_attributes_by_feature("NEW_FIELDS")
            assert len(feature_attrs) == 1
