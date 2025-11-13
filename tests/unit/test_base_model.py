"""
Tests for BaseModel and PartialModel.

Tests the to_update_dict() method and frozen field handling.
"""

import pytest
from pydantic import Field, ValidationError

from upsales.models.base import BaseModel, PartialModel


class SampleUser(BaseModel):
    """Sample user model with frozen and updatable fields for testing."""

    id: int = Field(frozen=True)
    created_at: str | None = Field(None, frozen=True)
    updated_at: str | None = Field(None, frozen=True)
    name: str
    email: str
    active: int = 1


class SamplePartialUser(PartialModel):
    """Sample partial user model for testing."""

    id: int
    name: str


def test_model_creation():
    """Test creating a model instance."""
    user = SampleUser(
        id=1,
        name="John",
        email="john@example.com",
        created_at="2024-01-01",
        updated_at="2024-01-02",
    )

    assert user.id == 1
    assert user.name == "John"
    assert user.email == "john@example.com"
    assert user.created_at == "2024-01-01"
    assert user.updated_at == "2024-01-02"
    assert user.active == 1


def test_frozen_field_cannot_be_modified():
    """Test that frozen fields raise error when modified."""
    user = SampleUser(
        id=1,
        name="John",
        email="john@example.com",
    )

    # Frozen fields should raise ValidationError
    with pytest.raises(ValidationError, match="frozen"):
        user.id = 2

    with pytest.raises(ValidationError, match="frozen"):
        user.created_at = "2024-01-01"


def test_updatable_field_can_be_modified():
    """Test that updatable fields can be modified."""
    user = SampleUser(
        id=1,
        name="John",
        email="john@example.com",
    )

    # Updatable fields should work fine
    user.name = "Jane"
    assert user.name == "Jane"

    user.email = "jane@example.com"
    assert user.email == "jane@example.com"

    user.active = 0
    assert user.active == 0


def test_to_update_dict_excludes_frozen_fields():
    """Test that to_update_dict excludes frozen fields."""
    user = SampleUser(
        id=1,
        name="John",
        email="john@example.com",
        created_at="2024-01-01",
        updated_at="2024-01-02",
    )

    update_dict = user.to_update_dict()

    # Frozen fields should be excluded
    assert "id" not in update_dict
    assert "created_at" not in update_dict
    assert "updated_at" not in update_dict

    # Updatable fields should be included
    assert update_dict["name"] == "John"
    assert update_dict["email"] == "john@example.com"
    assert update_dict["active"] == 1


def test_to_update_dict_with_overrides():
    """Test to_update_dict with override parameters."""
    user = SampleUser(
        id=1,
        name="John",
        email="john@example.com",
    )

    update_dict = user.to_update_dict(name="Jane", active=0)

    assert update_dict["name"] == "Jane"
    assert update_dict["active"] == 0
    assert update_dict["email"] == "john@example.com"

    # Still excludes frozen fields
    assert "id" not in update_dict


def test_to_update_dict_excludes_client():
    """Test that to_update_dict excludes _client field."""
    user = SampleUser(
        id=1,
        name="John",
        email="john@example.com",
        _client="fake_client",  # type: ignore
    )

    update_dict = user.to_update_dict()

    assert "_client" not in update_dict


def test_to_update_dict_preserves_none_values():
    """Test that to_update_dict keeps None values."""
    user = SampleUser(
        id=1,
        name="John",
        email="john@example.com",
        created_at=None,
        updated_at=None,
    )

    update_dict = user.to_update_dict()

    # None values in updatable fields should be preserved
    # (created_at and updated_at are frozen, so excluded regardless)
    assert "id" not in update_dict
    assert "created_at" not in update_dict
    assert "updated_at" not in update_dict


def test_to_update_dict_with_custom_fields():
    """Test to_update_dict with model that has custom fields."""

    class UserWithCustom(BaseModel):
        id: int = Field(frozen=True)
        name: str
        custom: list[dict] = []

    user = UserWithCustom(
        id=1,
        name="John",
        custom=[{"fieldId": 11, "value": "test"}],
    )

    update_dict = user.to_update_dict()

    assert "id" not in update_dict
    assert update_dict["name"] == "John"
    assert update_dict["custom"] == [{"fieldId": 11, "value": "test"}]


def test_to_update_dict_empty_overrides():
    """Test to_update_dict with empty overrides."""
    user = SampleUser(
        id=1,
        name="John",
        email="john@example.com",
    )

    update_dict = user.to_update_dict()

    assert "id" not in update_dict
    assert update_dict["name"] == "John"


def test_repr():
    """Test string representation."""
    user = SampleUser(
        id=1,
        name="John",
        email="john@example.com",
    )

    assert repr(user) == "<SampleUser id=1>"


def test_partial_model_repr():
    """Test partial model string representation."""
    partial = SamplePartialUser(id=1, name="John")

    assert repr(partial) == "<SamplePartialUser id=1>"


async def test_edit_not_implemented():
    """Test that edit() raises NotImplementedError on base."""
    user = SampleUser(
        id=1,
        name="John",
        email="john@example.com",
    )

    with pytest.raises(NotImplementedError, match="Subclass must implement edit"):
        await user.edit(name="Jane")


async def test_partial_fetch_full_not_implemented():
    """Test that fetch_full() raises NotImplementedError on base."""
    partial = SamplePartialUser(id=1, name="John")

    with pytest.raises(NotImplementedError, match="Subclass must implement fetch_full"):
        await partial.fetch_full()


async def test_partial_edit_not_implemented():
    """Test that edit() raises NotImplementedError on partial base."""
    partial = SamplePartialUser(id=1, name="John")

    with pytest.raises(NotImplementedError, match="Subclass must implement edit"):
        await partial.edit(name="Jane")


def test_model_with_client_reference():
    """Test model with _client reference."""

    class FakeClient:
        pass

    client = FakeClient()

    user = SampleUser(
        id=1,
        name="John",
        email="john@example.com",
        _client=client,  # type: ignore
    )

    assert user._client is client


def test_to_update_dict_with_all_frozen():
    """Test to_update_dict when all fields are frozen."""

    class AllFrozen(BaseModel):
        id: int = Field(frozen=True)
        created: str = Field(frozen=True)

    model = AllFrozen(id=1, created="2024-01-01")

    update_dict = model.to_update_dict()

    # Should be empty (all fields frozen)
    assert update_dict == {}


def test_to_update_dict_with_no_frozen():
    """Test to_update_dict when no fields are frozen."""

    class NoFrozen(BaseModel):
        id: int  # Not frozen!
        name: str

    model = NoFrozen(id=1, name="John")

    update_dict = model.to_update_dict()

    # Should include all fields (except _client)
    assert update_dict["id"] == 1
    assert update_dict["name"] == "John"
