"""
Tests for CustomFields helper class.

Uses Python 3.13 native type hints.
"""

import pytest

from upsales.models.custom_fields import CustomFields


def test_get_by_id(mock_custom_fields):
    """Test getting field value by ID."""
    cf = CustomFields(mock_custom_fields)
    assert cf[11] == "value1"


def test_get_by_id_not_found(mock_custom_fields):
    """Test getting non-existent field by ID."""
    cf = CustomFields(mock_custom_fields)
    assert cf.get(999, "default") == "default"


def test_get_by_alias(mock_custom_fields, field_schema):
    """Test getting field value by alias."""
    cf = CustomFields(mock_custom_fields, field_schema=field_schema)
    assert cf["CUSTOM_FIELD_1"] == "value1"


def test_get_by_alias_not_in_schema(mock_custom_fields, field_schema):
    """Test getting field by unknown alias raises KeyError."""
    cf = CustomFields(mock_custom_fields, field_schema=field_schema)

    with pytest.raises(KeyError, match="Unknown custom field alias"):
        _ = cf["UNKNOWN_ALIAS"]


def test_set_by_id(mock_custom_fields):
    """Test setting field value by ID."""
    cf = CustomFields(mock_custom_fields)
    cf[11] = "new_value"
    assert cf[11] == "new_value"


def test_set_new_field(mock_custom_fields):
    """Test setting value for new field ID."""
    cf = CustomFields(mock_custom_fields)
    cf[99] = "new_field_value"
    assert cf[99] == "new_field_value"


def test_set_by_alias(mock_custom_fields, field_schema):
    """Test setting field value by alias."""
    cf = CustomFields(mock_custom_fields, field_schema=field_schema)
    cf["CUSTOM_FIELD_1"] = "updated"
    assert cf[11] == "updated"


def test_contains(mock_custom_fields):
    """Test checking if field exists."""
    cf = CustomFields(mock_custom_fields)
    assert 11 in cf
    assert 999 not in cf


def test_contains_by_alias(mock_custom_fields, field_schema):
    """Test checking if field exists by alias."""
    cf = CustomFields(mock_custom_fields, field_schema=field_schema)
    assert "CUSTOM_FIELD_1" in cf
    assert "UNKNOWN" not in cf


def test_to_api_format(mock_custom_fields):
    """Test converting to API format."""
    cf = CustomFields(mock_custom_fields)
    cf[11] = "updated"
    cf[99] = "new"

    api_data = cf.to_api_format()

    # Should contain updated and new fields
    assert any(f["fieldId"] == 11 and f["value"] == "updated" for f in api_data)
    assert any(f["fieldId"] == 99 and f["value"] == "new" for f in api_data)


def test_repr(mock_custom_fields):
    """Test string representation."""
    cf = CustomFields(mock_custom_fields)
    repr_str = repr(cf)

    assert "CustomFields" in repr_str
    assert "11:" in repr_str


def test_get_with_default():
    """Test get with default value."""
    cf = CustomFields([])
    assert cf.get(11, "default") == "default"
    assert cf.get(11) is None
