"""
Integration tests for TriggerAttributesResource using VCR.py.

These tests make real API calls on first run and record responses to cassettes.
Subsequent runs replay from cassettes (fast, no API calls).

Tests cover:
- get() - Get all trigger attributes
- get_entity_attributes() - Get attributes for specific entity
- get_criteria_attributes() - Get only criteria attributes
- get_attribute_by_id() - Get attribute by ID
"""

import pytest

from upsales import Upsales


@pytest.mark.asyncio
async def test_get_trigger_attributes():
    """Test getting all trigger attributes."""
    async with Upsales.from_env() as upsales:
        attrs = await upsales.trigger_attributes.get()

        # Verify response structure
        assert attrs is not None
        assert len(attrs.entity_types) > 0
        assert attrs.total_attributes > 0

        # Verify common entity types exist
        assert "Client" in attrs.entity_types
        assert "Contact" in attrs.entity_types
        assert "Order" in attrs.entity_types
        assert "Activity" in attrs.entity_types

        # Verify computed fields
        assert attrs.entity_types == sorted(attrs.entity_types)  # Should be sorted


@pytest.mark.asyncio
async def test_get_entity_attributes():
    """Test getting attributes for specific entity type."""
    async with Upsales.from_env() as upsales:
        # Get Client attributes
        client_attrs = await upsales.trigger_attributes.get_entity_attributes("Client")

        # Verify we got a list of attributes
        assert isinstance(client_attrs, list)
        assert len(client_attrs) > 0

        # Verify attribute structure
        first_attr = client_attrs[0]
        assert hasattr(first_attr, "id")
        assert hasattr(first_attr, "name")
        assert hasattr(first_attr, "type")
        assert hasattr(first_attr, "lang")
        assert hasattr(first_attr, "asCriteria")

        # Verify computed fields work
        assert hasattr(first_attr, "can_be_criteria")
        assert hasattr(first_attr, "entity_type")
        assert hasattr(first_attr, "field_name")

        # Check that Client.Name exists
        name_attr = next((a for a in client_attrs if a.id == "Client.Name"), None)
        assert name_attr is not None
        assert name_attr.name == "Name"
        assert name_attr.entity_type == "Client"
        assert name_attr.field_name == "Name"


@pytest.mark.asyncio
async def test_get_criteria_attributes():
    """Test getting only criteria attributes."""
    async with Upsales.from_env() as upsales:
        # Get Contact criteria attributes
        criteria = await upsales.trigger_attributes.get_criteria_attributes("Contact")

        # Verify all are criteria attributes
        assert isinstance(criteria, list)
        assert len(criteria) > 0
        assert all(attr.can_be_criteria for attr in criteria)
        assert all(attr.asCriteria for attr in criteria)


@pytest.mark.asyncio
async def test_get_attribute_by_id():
    """Test getting single attribute by ID."""
    async with Upsales.from_env() as upsales:
        # Get specific attribute
        attr = await upsales.trigger_attributes.get_attribute_by_id("Client.Name")

        # Verify attribute found and correct
        assert attr is not None
        assert attr.id == "Client.Name"
        assert attr.name == "Name"
        assert attr.type == "string"
        assert attr.entity_type == "Client"
        assert attr.field_name == "Name"

        # Test non-existent attribute
        not_found = await upsales.trigger_attributes.get_attribute_by_id("NonExistent.Field")
        assert not_found is None
