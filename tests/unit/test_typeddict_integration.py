"""
Tests for TypedDict integration with models.

Tests IDE autocomplete patterns and type safety.
"""

from typing import TypedDict, Unpack

import pytest
from pydantic import Field

from upsales.models.base import BaseModel


class UserUpdateFields(TypedDict, total=False):
    """TypedDict for user updates."""

    name: str
    email: str
    administrator: int
    active: int


class User(BaseModel):
    """Test user with TypedDict integration."""

    id: int = Field(frozen=True)
    created_at: str | None = Field(None, frozen=True)
    name: str
    email: str
    administrator: int
    active: int = 1

    async def edit(self, **kwargs: Unpack[UserUpdateFields]) -> "User":
        """Edit with TypedDict."""
        # In real implementation, would call API
        # For tests, just update fields
        for key, value in kwargs.items():
            setattr(self, key, value)
        return self


def test_typeddict_has_correct_fields():
    """Test that TypedDict includes only updatable fields."""
    expected_fields = {"name", "email", "administrator", "active"}
    actual_fields = set(UserUpdateFields.__annotations__.keys())

    assert actual_fields == expected_fields


def test_typeddict_excludes_frozen_fields():
    """Test that TypedDict excludes frozen fields."""
    typeddict_fields = set(UserUpdateFields.__annotations__.keys())

    # Frozen fields should NOT be in TypedDict
    assert "id" not in typeddict_fields
    assert "created_at" not in typeddict_fields


def test_typeddict_field_types():
    """Test that TypedDict has correct types."""
    assert UserUpdateFields.__annotations__["name"] == str
    assert UserUpdateFields.__annotations__["email"] == str
    assert UserUpdateFields.__annotations__["administrator"] == int
    assert UserUpdateFields.__annotations__["active"] == int


def test_typeddict_total_false():
    """Test that TypedDict has total=False."""
    # TypedDict with total=False means all fields are optional
    # We can verify this works by creating instances with subsets
    partial: UserUpdateFields = {"name": "John"}
    assert partial["name"] == "John"

    full: UserUpdateFields = {
        "name": "John",
        "email": "john@example.com",
        "administrator": 1,
        "active": 1,
    }
    assert full["name"] == "John"


@pytest.mark.asyncio
async def test_edit_with_typeddict_kwargs():
    """Test edit() accepts TypedDict kwargs."""
    user = User(
        id=1,
        name="John",
        email="john@example.com",
        administrator=0,
    )

    # Should accept any subset of TypedDict fields
    updated = await user.edit(name="Jane")
    assert updated.name == "Jane"

    updated = await user.edit(name="Bob", administrator=1)
    assert updated.name == "Bob"
    assert updated.administrator == 1


@pytest.mark.asyncio
async def test_edit_with_all_fields():
    """Test edit() with all TypedDict fields."""
    user = User(
        id=1,
        name="John",
        email="john@example.com",
        administrator=0,
    )

    updated = await user.edit(
        name="Jane",
        email="jane@example.com",
        administrator=1,
        active=0,
    )

    assert updated.name == "Jane"
    assert updated.email == "jane@example.com"
    assert updated.administrator == 1
    assert updated.active == 0


def test_model_and_typeddict_field_alignment():
    """Test that TypedDict fields match updatable model fields."""
    # Get all non-frozen fields from model
    updatable_fields = {
        name for name, field in User.model_fields.items() if not field.frozen and name != "_client"
    }

    # Get TypedDict fields
    typeddict_fields = set(UserUpdateFields.__annotations__.keys())

    # They should match (except _client which is internal)
    assert typeddict_fields == updatable_fields


def test_typeddict_doesnt_allow_readonly():
    """
    Test that TypedDict pattern prevents readonly field updates.

    Note: This is a compile-time check (mypy/pyright), not runtime.
    This test documents the expected behavior.
    """
    # This would be a type error if checked by mypy:
    # invalid: UserUpdateFields = {"id": 999}  # ❌ Type error

    # Only valid fields are accepted:
    valid: UserUpdateFields = {"name": "John"}  # ✅ OK
    assert valid["name"] == "John"


def test_integration_with_to_update_dict():
    """Test that TypedDict + to_update_dict() work together."""

    class TestUser(BaseModel):
        id: int = Field(frozen=True)
        name: str
        email: str

        async def edit(self, **kwargs: Unpack[UserUpdateFields]) -> "TestUser":
            """Edit using to_update_dict."""
            # This simulates the real pattern
            update_dict = self.to_update_dict(**kwargs)

            # Update fields
            for key, value in update_dict.items():
                if hasattr(self, key):
                    setattr(self, key, value)

            return self

    user = TestUser(id=1, name="John", email="john@example.com")

    # to_update_dict should exclude frozen fields even if passed
    update_dict = user.to_update_dict(id=999, name="Jane")

    # id should be excluded (frozen)
    assert "id" not in update_dict
    assert update_dict["name"] == "Jane"


def test_multiple_typeddict_models():
    """Test multiple models with their own TypedDicts."""

    class ProductUpdateFields(TypedDict, total=False):
        name: str
        price: float
        active: int

    class Product(BaseModel):
        id: int = Field(frozen=True)
        name: str
        price: float
        active: int

        async def edit(self, **kwargs: Unpack[ProductUpdateFields]) -> "Product":
            for key, value in kwargs.items():
                setattr(self, key, value)
            return self

    # User and Product have different TypedDicts
    assert "email" in UserUpdateFields.__annotations__
    assert "email" not in ProductUpdateFields.__annotations__

    assert "price" in ProductUpdateFields.__annotations__
    assert "price" not in UserUpdateFields.__annotations__


def test_typeddict_documentation():
    """Test that TypedDict has docstring."""
    assert UserUpdateFields.__doc__ is not None
    assert (
        "updatable" in UserUpdateFields.__doc__.lower()
        or "update" in UserUpdateFields.__doc__.lower()
    )
