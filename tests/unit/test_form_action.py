"""
Tests for FormAction, FormActionProperty, and PartialFormAction models.

Uses Python 3.13 native type hints.
"""

from typing import Any

import pytest
from pydantic import ValidationError

from upsales.models.form_action import FormAction, FormActionProperty, PartialFormAction


@pytest.fixture
def sample_property_data() -> dict[str, Any]:
    """
    Sample form action property data.

    Returns:
        Dict with property data.
    """
    return {
        "name": "EmailTo",
        "value": "admin@company.com",
    }


@pytest.fixture
def sample_property_data_empty_value() -> dict[str, Any]:
    """
    Sample form action property with empty value.

    Returns:
        Dict with property data with empty value.
    """
    return {
        "name": "Subject",
        "value": "",
    }


@pytest.fixture
def sample_property_data_null_value() -> dict[str, Any]:
    """
    Sample form action property with null value.

    Returns:
        Dict with property data with null value.
    """
    return {
        "name": "OptionalField",
        "value": None,
    }


@pytest.fixture
def sample_action_data() -> dict[str, Any]:
    """
    Sample form action data from API.

    Returns:
        Dict with complete action data.
    """
    return {
        "id": 1,
        "action": "SendEmail",
        "properties": [
            {"name": "EmailTo", "value": "admin@company.com"},
            {"name": "Subject", "value": "New form submission"},
            {"name": "Body", "value": "A new form has been submitted."},
        ],
    }


@pytest.fixture
def sample_action_data_no_properties() -> dict[str, Any]:
    """
    Sample form action with no properties.

    Returns:
        Dict with action data without properties.
    """
    return {
        "id": 2,
        "action": "CreateTask",
        "properties": [],
    }


@pytest.fixture
def minimal_action_data() -> dict[str, Any]:
    """
    Minimal form action data (required fields only).

    Returns:
        Dict with minimum required action fields.
    """
    return {
        "id": 3,
        "action": "SendNotification",
    }


# ============================================================================
# FormActionProperty Model Tests
# ============================================================================


def test_property_creation(sample_property_data):
    """Test creating FormActionProperty with complete data."""
    prop = FormActionProperty(**sample_property_data)

    assert prop.name == "EmailTo"
    assert prop.value == "admin@company.com"
    assert prop.has_value is True


def test_property_creation_empty_value(sample_property_data_empty_value):
    """Test creating FormActionProperty with empty value."""
    prop = FormActionProperty(**sample_property_data_empty_value)

    assert prop.name == "Subject"
    assert prop.value == ""
    assert prop.has_value is False


def test_property_creation_null_value(sample_property_data_null_value):
    """Test creating FormActionProperty with null value."""
    prop = FormActionProperty(**sample_property_data_null_value)

    assert prop.name == "OptionalField"
    assert prop.value is None
    assert prop.has_value is False


def test_property_validates_required_fields():
    """Test that FormActionProperty validates required fields."""
    # Missing name
    with pytest.raises(ValidationError, match="name"):
        FormActionProperty(value="test")


def test_property_validates_non_empty_name():
    """Test that FormActionProperty validates non-empty name."""
    # Empty name
    with pytest.raises(ValidationError):
        FormActionProperty(name="", value="test")

    # Whitespace-only name
    with pytest.raises(ValidationError):
        FormActionProperty(name="   ", value="test")


def test_property_has_value_whitespace():
    """Test has_value with whitespace-only value."""
    prop = FormActionProperty(name="Test", value="   ")
    assert prop.has_value is False


def test_property_to_dict(sample_property_data):
    """Test to_dict serialization."""
    prop = FormActionProperty(**sample_property_data)
    data = prop.to_dict()

    assert data["name"] == "EmailTo"
    assert data["value"] == "admin@company.com"

    # Should NOT include computed fields
    assert "has_value" not in data


def test_property_repr(sample_property_data):
    """Test string representation."""
    prop = FormActionProperty(**sample_property_data)
    repr_str = repr(prop)

    assert "FormActionProperty" in repr_str
    assert "name=EmailTo" in repr_str


def test_property_mutability(sample_property_data):
    """Test that FormActionProperty is mutable."""
    prop = FormActionProperty(**sample_property_data)

    # Should allow assignment
    prop.value = "newemail@company.com"
    assert prop.value == "newemail@company.com"

    # Should validate on assignment
    with pytest.raises(ValidationError):
        prop.name = ""


# ============================================================================
# FormAction Model Tests
# ============================================================================


def test_action_creation(sample_action_data):
    """Test creating FormAction with complete data."""
    action = FormAction(**sample_action_data)

    assert action.id == 1
    assert action.action == "SendEmail"
    assert action.property_count == 3
    assert action.has_properties is True
    assert len(action.properties) == 3

    # Check properties are parsed correctly
    assert isinstance(action.properties[0], FormActionProperty)
    assert action.properties[0].name == "EmailTo"
    assert action.properties[0].value == "admin@company.com"


def test_action_creation_no_properties(sample_action_data_no_properties):
    """Test creating FormAction with no properties."""
    action = FormAction(**sample_action_data_no_properties)

    assert action.id == 2
    assert action.action == "CreateTask"
    assert action.property_count == 0
    assert action.has_properties is False
    assert len(action.properties) == 0


def test_action_minimal_creation(minimal_action_data):
    """Test creating FormAction with minimal required fields."""
    action = FormAction(**minimal_action_data)

    assert action.id == 3
    assert action.action == "SendNotification"
    assert action.property_count == 0
    assert action.has_properties is False


def test_action_validates_required_fields():
    """Test that FormAction validates required fields."""
    # Missing id
    with pytest.raises(ValidationError, match="id"):
        FormAction(action="SendEmail", properties=[])

    # Missing action
    with pytest.raises(ValidationError, match="action"):
        FormAction(id=1, properties=[])


def test_action_validates_non_empty_action():
    """Test that FormAction validates non-empty action."""
    # Empty action
    with pytest.raises(ValidationError):
        FormAction(id=1, action="", properties=[])

    # Whitespace-only action
    with pytest.raises(ValidationError):
        FormAction(id=1, action="   ", properties=[])


def test_action_get_property(sample_action_data):
    """Test get_property method."""
    action = FormAction(**sample_action_data)

    # Existing properties
    assert action.get_property("EmailTo") == "admin@company.com"
    assert action.get_property("Subject") == "New form submission"
    assert action.get_property("Body") == "A new form has been submitted."

    # Non-existent property
    assert action.get_property("NonExistent") is None


def test_action_get_property_empty_list(sample_action_data_no_properties):
    """Test get_property on action with no properties."""
    action = FormAction(**sample_action_data_no_properties)

    assert action.get_property("EmailTo") is None
    assert action.get_property("Anything") is None


def test_action_get_property_names(sample_action_data):
    """Test get_property_names method."""
    action = FormAction(**sample_action_data)

    names = action.get_property_names()
    assert names == ["EmailTo", "Subject", "Body"]


def test_action_get_property_names_empty(sample_action_data_no_properties):
    """Test get_property_names on action with no properties."""
    action = FormAction(**sample_action_data_no_properties)

    names = action.get_property_names()
    assert names == []


def test_action_to_dict(sample_action_data):
    """Test to_dict serialization."""
    action = FormAction(**sample_action_data)
    data = action.to_dict()

    assert data["id"] == 1
    assert data["action"] == "SendEmail"
    assert "properties" in data
    assert len(data["properties"]) == 3

    # Should NOT include computed fields
    assert "property_count" not in data
    assert "has_properties" not in data


def test_action_repr(sample_action_data):
    """Test string representation."""
    action = FormAction(**sample_action_data)
    repr_str = repr(action)

    assert "FormAction" in repr_str
    assert "id=1" in repr_str
    assert "action=SendEmail" in repr_str


def test_action_mutability(sample_action_data):
    """Test that FormAction is mutable."""
    action = FormAction(**sample_action_data)

    # Should allow assignment
    action.action = "CreateTask"
    assert action.action == "CreateTask"

    # Should validate on assignment
    with pytest.raises(ValidationError):
        action.action = ""


# ============================================================================
# PartialFormAction Model Tests
# ============================================================================


def test_partial_action_creation(sample_action_data):
    """Test creating PartialFormAction with complete data."""
    action = PartialFormAction(**sample_action_data)

    assert action.id == 1
    assert action.action == "SendEmail"
    assert action.property_count == 3
    assert len(action.properties) == 3

    # Properties should be raw dicts in partial
    assert isinstance(action.properties[0], dict)
    assert action.properties[0]["name"] == "EmailTo"


def test_partial_action_minimal_creation(minimal_action_data):
    """Test creating PartialFormAction with minimal required fields."""
    action = PartialFormAction(**minimal_action_data)

    assert action.id == 3
    assert action.action == "SendNotification"
    assert action.property_count == 0


def test_partial_action_validates_required_fields():
    """Test that PartialFormAction validates required fields."""
    # Missing id
    with pytest.raises(ValidationError, match="id"):
        PartialFormAction(action="SendEmail")

    # Missing action
    with pytest.raises(ValidationError, match="action"):
        PartialFormAction(id=1)


def test_partial_action_allows_empty_action():
    """Test that PartialFormAction allows empty action (less strict)."""
    # PartialFormAction uses str, not NonEmptyStr, so empty strings are allowed
    action = PartialFormAction(id=1, action="")

    assert action.action == ""


def test_partial_action_to_full(sample_action_data):
    """Test converting PartialFormAction to full FormAction."""
    partial = PartialFormAction(**sample_action_data)
    full = partial.to_full()

    assert isinstance(full, FormAction)
    assert full.id == partial.id
    assert full.action == partial.action
    assert full.property_count == partial.property_count

    # Properties should be converted to FormActionProperty objects
    assert isinstance(full.properties[0], FormActionProperty)
    assert full.properties[0].name == "EmailTo"


def test_partial_action_to_full_validates():
    """Test that to_full() validates when converting."""
    # PartialFormAction allows empty action, but FormAction doesn't
    partial = PartialFormAction(id=1, action="")

    # Should raise ValidationError when converting to FormAction
    with pytest.raises(ValidationError):
        partial.to_full()


def test_partial_action_repr():
    """Test string representation of PartialFormAction."""
    action = PartialFormAction(id=1, action="SendEmail", properties=[])
    repr_str = repr(action)

    assert "PartialFormAction" in repr_str
    assert "id=1" in repr_str
    assert "action=SendEmail" in repr_str


# ============================================================================
# Integration Tests
# ============================================================================


def test_action_in_list():
    """Test using FormAction in a list (like Form.actions)."""
    actions = [
        FormAction(id=1, action="SendEmail", properties=[]),
        FormAction(id=2, action="CreateTask", properties=[]),
        FormAction(id=3, action="SendNotification", properties=[]),
    ]

    # Filter by action type
    email_actions = [a for a in actions if a.action == "SendEmail"]
    assert len(email_actions) == 1
    assert email_actions[0].id == 1


def test_action_property_iteration(sample_action_data):
    """Test iterating over action properties."""
    action = FormAction(**sample_action_data)

    property_dict = {prop.name: prop.value for prop in action.properties}
    assert property_dict["EmailTo"] == "admin@company.com"
    assert property_dict["Subject"] == "New form submission"
    assert property_dict["Body"] == "A new form has been submitted."


def test_action_extra_fields():
    """Test that FormAction allows extra fields from API."""
    # API might return extra fields we don't know about yet
    data = {
        "id": 1,
        "action": "SendEmail",
        "properties": [],
        "unknown_field": "some_value",
    }

    # Should not raise error (extra="allow" in config)
    action = FormAction(**data)
    assert action.action == "SendEmail"


def test_partial_action_extra_fields():
    """Test that PartialFormAction allows extra fields from API."""
    data = {
        "id": 1,
        "action": "SendEmail",
        "properties": [],
        "future_field": 123,
    }

    # Should not raise error (extra="allow" in config)
    action = PartialFormAction(**data)
    assert action.action == "SendEmail"


def test_action_property_with_special_characters():
    """Test FormActionProperty with special characters in value."""
    prop = FormActionProperty(
        name="EmailSubject",
        value="New form: {{form_name}} - Contact: {{contact_email}}",
    )

    assert "{{form_name}}" in prop.value
    assert prop.has_value is True


def test_action_get_property_case_sensitive():
    """Test that get_property is case-sensitive."""
    action = FormAction(
        id=1,
        action="SendEmail",
        properties=[
            {"name": "EmailTo", "value": "admin@example.com"},
            {"name": "emailto", "value": "other@example.com"},
        ],
    )

    # Should be case-sensitive
    assert action.get_property("EmailTo") == "admin@example.com"
    assert action.get_property("emailto") == "other@example.com"
    assert action.get_property("EMAILTO") is None
