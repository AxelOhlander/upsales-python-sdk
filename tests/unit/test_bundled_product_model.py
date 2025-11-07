"""
Tests for BundledProduct and PartialBundledProduct models.

Uses Python 3.13 native type hints.
"""

from typing import Any

import pytest
from pydantic import ValidationError

from upsales.models.bundled_product import BundledProduct, PartialBundledProduct


@pytest.fixture
def sample_bundled_product_data() -> dict[str, Any]:
    """
    Sample bundled product data.

    Returns:
        Dict with complete bundled product data.
    """
    return {
        "id": 123,
        "name": "Widget A",
        "quantity": 2,
    }


@pytest.fixture
def minimal_bundled_product_data() -> dict[str, Any]:
    """
    Minimal bundled product data (defaults quantity to 1).

    Returns:
        Dict with minimum required bundled product fields.
    """
    return {
        "id": 456,
        "name": "Widget B",
    }


# ============================================================================
# BundledProduct Model Tests
# ============================================================================


def test_bundled_product_creation(sample_bundled_product_data):
    """Test creating BundledProduct with complete data."""
    bundled = BundledProduct(**sample_bundled_product_data)

    assert bundled.id == 123
    assert bundled.name == "Widget A"
    assert bundled.quantity == 2


def test_bundled_product_minimal_creation(minimal_bundled_product_data):
    """Test creating BundledProduct with minimal required fields."""
    bundled = BundledProduct(**minimal_bundled_product_data)

    assert bundled.id == 456
    assert bundled.name == "Widget B"
    assert bundled.quantity == 1  # Default value


def test_bundled_product_validates_required_fields():
    """Test that BundledProduct validates required fields."""
    # Missing id
    with pytest.raises(ValidationError, match="id"):
        BundledProduct(name="Widget")

    # Missing name
    with pytest.raises(ValidationError, match="name"):
        BundledProduct(id=123)


def test_bundled_product_validates_non_empty_name():
    """Test that BundledProduct validates non-empty name."""
    # Empty name
    with pytest.raises(ValidationError):
        BundledProduct(id=123, name="")

    # Whitespace-only name
    with pytest.raises(ValidationError):
        BundledProduct(id=123, name="   ")


def test_bundled_product_validates_positive_quantity():
    """Test that BundledProduct validates positive quantity."""
    # Negative quantity
    with pytest.raises(ValidationError):
        BundledProduct(id=123, name="Widget", quantity=-1)

    # Zero quantity is allowed (non-negative)
    bundled = BundledProduct(id=123, name="Widget", quantity=0)
    assert bundled.quantity == 0


def test_bundled_product_id_frozen():
    """Test that id field is frozen (read-only)."""
    bundled = BundledProduct(id=123, name="Widget", quantity=2)

    # Attempting to modify frozen field should raise ValidationError
    with pytest.raises(ValidationError, match="frozen"):
        bundled.id = 999


def test_bundled_product_display_name_single(minimal_bundled_product_data):
    """Test display_name computed field for single unit."""
    bundled = BundledProduct(**minimal_bundled_product_data)

    # Quantity is 1, so no "(x1)" suffix
    assert bundled.display_name == "Widget B"


def test_bundled_product_display_name_multiple(sample_bundled_product_data):
    """Test display_name computed field for multiple units."""
    bundled = BundledProduct(**sample_bundled_product_data)

    # Quantity is 2, so includes "(x2)" suffix
    assert bundled.display_name == "Widget A (x2)"


def test_bundled_product_display_name_large_quantity():
    """Test display_name computed field with large quantity."""
    bundled = BundledProduct(id=123, name="Widget C", quantity=100)

    assert bundled.display_name == "Widget C (x100)"


def test_bundled_product_is_single_unit():
    """Test is_single_unit computed field."""
    # Single unit
    bundled_single = BundledProduct(id=123, name="Widget", quantity=1)
    assert bundled_single.is_single_unit is True

    # Multiple units
    bundled_multiple = BundledProduct(id=123, name="Widget", quantity=5)
    assert bundled_multiple.is_single_unit is False

    # Zero units (edge case)
    bundled_zero = BundledProduct(id=123, name="Widget", quantity=0)
    assert bundled_zero.is_single_unit is False


def test_bundled_product_to_api_dict(sample_bundled_product_data):
    """Test to_api_dict serialization."""
    bundled = BundledProduct(**sample_bundled_product_data)
    data = bundled.to_api_dict()

    # Should include updatable fields
    assert data["name"] == "Widget A"
    assert data["quantity"] == 2

    # Should NOT include frozen fields
    assert "id" not in data

    # Should NOT include computed fields
    assert "display_name" not in data
    assert "is_single_unit" not in data


def test_bundled_product_to_api_dict_with_overrides():
    """Test to_api_dict with overrides."""
    bundled = BundledProduct(id=123, name="Widget A", quantity=2)
    data = bundled.to_api_dict(quantity=5, name="Widget B")

    assert data["name"] == "Widget B"
    assert data["quantity"] == 5
    assert "id" not in data


def test_bundled_product_repr(sample_bundled_product_data):
    """Test string representation."""
    bundled = BundledProduct(**sample_bundled_product_data)
    repr_str = repr(bundled)

    assert "BundledProduct" in repr_str
    assert "id=123" in repr_str


def test_bundled_product_mutability(sample_bundled_product_data):
    """Test that BundledProduct is mutable."""
    bundled = BundledProduct(**sample_bundled_product_data)

    # Should allow assignment
    bundled.name = "Widget Updated"
    assert bundled.name == "Widget Updated"

    bundled.quantity = 10
    assert bundled.quantity == 10

    # Should validate on assignment
    with pytest.raises(ValidationError):
        bundled.name = ""

    with pytest.raises(ValidationError):
        bundled.quantity = -1


# Note: Async tests for edit() behavior are covered in integration tests
# Since BundledProduct.edit() requires parent product context and raises
# NotImplementedError, full testing of edit behavior is not applicable here


# ============================================================================
# PartialBundledProduct Model Tests
# ============================================================================


def test_partial_bundled_product_creation(sample_bundled_product_data):
    """Test creating PartialBundledProduct with complete data."""
    partial = PartialBundledProduct(**sample_bundled_product_data)

    assert partial.id == 123
    assert partial.name == "Widget A"


def test_partial_bundled_product_minimal_creation():
    """Test creating PartialBundledProduct with minimal required fields."""
    partial = PartialBundledProduct(id=456, name="Widget B")

    assert partial.id == 456
    assert partial.name == "Widget B"


def test_partial_bundled_product_validates_required_fields():
    """Test that PartialBundledProduct validates required fields."""
    # Missing id
    with pytest.raises(ValidationError, match="id"):
        PartialBundledProduct(name="Widget")

    # Missing name
    with pytest.raises(ValidationError, match="name"):
        PartialBundledProduct(id=123)


def test_partial_bundled_product_id_frozen():
    """Test that id field is frozen (read-only)."""
    partial = PartialBundledProduct(id=123, name="Widget")

    # Attempting to modify frozen field should raise ValidationError
    with pytest.raises(ValidationError, match="frozen"):
        partial.id = 999


def test_partial_bundled_product_display_name():
    """Test display_name computed field on PartialBundledProduct."""
    partial = PartialBundledProduct(id=123, name="Widget A")

    assert partial.display_name == "Widget A"


def test_partial_bundled_product_repr():
    """Test string representation of PartialBundledProduct."""
    partial = PartialBundledProduct(id=123, name="Widget A")
    repr_str = repr(partial)

    assert "PartialBundledProduct" in repr_str
    assert "id=123" in repr_str


# ============================================================================
# Integration Tests
# ============================================================================


def test_bundled_product_in_list():
    """Test using BundledProduct in a list (like Product.bundle)."""
    bundle = [
        BundledProduct(id=1, name="Widget A", quantity=2),
        BundledProduct(id=2, name="Widget B", quantity=1),
        BundledProduct(id=3, name="Widget C", quantity=5),
    ]

    # Filter single units
    single_units = [b for b in bundle if b.is_single_unit]
    assert len(single_units) == 1
    assert single_units[0].name == "Widget B"

    # Get display names
    display_names = [b.display_name for b in bundle]
    assert display_names == ["Widget A (x2)", "Widget B", "Widget C (x5)"]


def test_bundled_product_extra_fields():
    """Test that BundledProduct allows extra fields from API."""
    # API might return extra fields we don't know about yet
    data = {
        "id": 123,
        "name": "Widget A",
        "quantity": 2,
        "unknown_field": "some_value",
        "future_field": 999,
    }

    # Should not raise error (extra="allow" in config)
    bundled = BundledProduct(**data)
    assert bundled.id == 123
    assert bundled.name == "Widget A"


def test_partial_bundled_product_extra_fields():
    """Test that PartialBundledProduct allows extra fields from API."""
    data = {
        "id": 123,
        "name": "Widget A",
        "description": "Some description we don't have in model",
    }

    # Should not raise error (extra="allow" in config)
    partial = PartialBundledProduct(**data)
    assert partial.id == 123


def test_bundled_product_whitespace_handling():
    """Test that name validator strips whitespace."""
    bundled = BundledProduct(id=123, name="  Widget A  ", quantity=2)

    # Should strip whitespace
    assert bundled.name == "Widget A"


def test_bundled_product_type_validation():
    """Test that BundledProduct validates field types."""
    # id must be int
    with pytest.raises(ValidationError):
        BundledProduct(id="not_an_int", name="Widget", quantity=2)

    # quantity must be int
    with pytest.raises(ValidationError):
        BundledProduct(id=123, name="Widget", quantity="not_an_int")

    # name must be string
    with pytest.raises(ValidationError):
        BundledProduct(id=123, name=123, quantity=2)
