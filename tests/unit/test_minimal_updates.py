"""
Tests for minimal update functionality (to_update_dict_minimal).

Tests that updates send only changed fields + required fields,
reducing payload size and minimizing edit conflict risk.
"""

from pydantic import Field

from upsales.models.base import BaseModel


class SampleModelWithRequired(BaseModel):
    """Sample model with required update fields for testing."""

    _required_update_fields = {"email"}  # email is required for updates

    id: int = Field(frozen=True)
    name: str
    email: str
    active: int = 1
    optional_field: str | None = None


class SampleModelNoRequired(BaseModel):
    """Sample model without required update fields for testing."""

    id: int = Field(frozen=True)
    name: str
    active: int = 1


def test_minimal_update_with_required_fields():
    """Test to_update_dict_minimal includes required fields."""
    user = SampleModelWithRequired(
        id=1, name="John", email="john@example.com", active=1, optional_field="optional"
    )

    # Change only name
    minimal = user.to_update_dict_minimal(name="Jane")

    # Should include: name (changed) + email (required)
    assert "name" in minimal
    assert minimal["name"] == "Jane"

    assert "email" in minimal  # Required field auto-included
    assert minimal["email"] == "john@example.com"

    # Should NOT include: active, optional_field (not changed, not required)
    assert "active" not in minimal
    assert "optional_field" not in minimal

    # Should NOT include: id (frozen)
    assert "id" not in minimal


def test_minimal_update_without_required_fields():
    """Test to_update_dict_minimal when no required fields defined."""
    user = SampleModelNoRequired(id=1, name="John", active=1)

    # Change only name
    minimal = user.to_update_dict_minimal(name="Jane")

    # Should only include changed field
    assert minimal == {"name": "Jane"}

    # Should NOT include: active (not changed)
    assert "active" not in minimal

    # Should NOT include: id (frozen)
    assert "id" not in minimal


def test_minimal_update_multiple_changes():
    """Test to_update_dict_minimal with multiple changed fields."""
    user = SampleModelWithRequired(
        id=1, name="John", email="john@example.com", active=1, optional_field="test"
    )

    # Change name and active
    minimal = user.to_update_dict_minimal(name="Jane", active=0)

    # Should include: name, active (changed) + email (required)
    assert minimal == {
        "name": "Jane",
        "active": 0,
        "email": "john@example.com",  # Required, auto-included
    }


def test_minimal_update_changing_required_field():
    """Test changing a required field itself."""
    user = SampleModelWithRequired(id=1, name="John", email="john@example.com", active=1)

    # Change email (which is also required)
    minimal = user.to_update_dict_minimal(email="jane@example.com")

    # Should include new email value
    assert minimal == {"email": "jane@example.com"}


def test_minimal_update_frozen_fields_excluded():
    """Test that frozen fields are never included."""
    user = SampleModelWithRequired(id=1, name="John", email="john@example.com")

    # Try to override frozen field (should be ignored)
    minimal = user.to_update_dict_minimal(id=999, name="Jane")

    # id should NOT be included (frozen)
    assert "id" not in minimal

    # Only changed and required fields
    assert "name" in minimal
    assert "email" in minimal


def test_minimal_vs_full_update():
    """Compare minimal vs full update payloads."""
    user = SampleModelWithRequired(
        id=1, name="John", email="john@example.com", active=1, optional_field="test"
    )

    # Minimal update (only name changed)
    minimal = user.to_update_dict_minimal(name="Jane")

    # Full update (all fields)
    full = user.to_api_dict(name="Jane")

    # Minimal should be smaller
    assert len(minimal) < len(full)

    # Minimal should have: name (changed) + email (required)
    assert set(minimal.keys()) == {"name", "email"}

    # Full should have: all non-frozen fields
    assert "active" in full
    assert "optional_field" in full


# Coverage check
# Run: uv run pytest tests/unit/test_minimal_updates.py -v --cov=upsales/models/base.py
