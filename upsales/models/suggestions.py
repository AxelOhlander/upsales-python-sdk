"""
Suggestion models for Upsales API.

Based on /api/v2/prospectingsuggestion endpoint.
This endpoint provides AI-powered suggestions for prospecting existing customers.

Enhanced with Pydantic v2 features:
- Reusable validators
- Computed fields (@computed_field)
- Field serialization (@field_serializer)
- Strict type checking
- Field descriptions
- Optimized serialization
"""

from typing import Any, TypedDict, Unpack

from pydantic import Field, computed_field

from upsales.models.base import BaseModel, PartialModel


class SuggestionUpdateFields(TypedDict, total=False):
    """
    Available fields for updating a Suggestion.

    All fields are optional. Use with Unpack for IDE autocomplete.
    """

    actions: list[Any]


class Suggestion(BaseModel):
    """
    Suggestion model from /api/v2/prospectingsuggestion.

    Represents an AI-powered prospecting suggestion for existing customers.
    This is a special endpoint that requires a boxid parameter.

    Example:
        >>> suggestion = await upsales.suggestions.get(boxid=123)
        >>> suggestion.boxid
        123
        >>> await suggestion.edit(actions=[...])  # IDE autocomplete
    """

    # Read-only fields (frozen=True, strict=True)
    boxid: int = Field(frozen=True, strict=True, description="Box ID for the suggestion")
    id: int = Field(
        default=0, frozen=True, strict=True, description="Unique suggestion ID (if available)"
    )

    # Updatable fields
    actions: list[Any] = Field(default=[], description="Actions associated with the suggestion")

    @computed_field
    @property
    def has_actions(self) -> bool:
        """Check if suggestion has any actions."""
        return len(self.actions) > 0

    async def edit(self, **kwargs: Unpack[SuggestionUpdateFields]) -> "Suggestion":
        """
        Edit this suggestion with type-safe field updates.

        Args:
            **kwargs: Fields to update (actions). Use Unpack for IDE autocomplete.

        Returns:
            Updated Suggestion instance with new field values.

        Raises:
            RuntimeError: If no client is available.

        Example:
            >>> suggestion = await upsales.suggestions.get(boxid=123)
            >>> updated = await suggestion.edit(actions=[{"type": "call"}])
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.suggestions.update(self.boxid, **self.to_api_dict(**kwargs))


class PartialSuggestion(PartialModel):
    """
    Partial Suggestion model for nested references.

    Contains minimal fields for when suggestions appear as nested objects
    in API responses.

    Example:
        >>> partial = PartialSuggestion(boxid=123)
        >>> full = await partial.fetch_full()  # Get complete Suggestion
    """

    boxid: int = Field(description="Box ID for the suggestion")

    async def fetch_full(self) -> Suggestion:
        """
        Fetch the full Suggestion object.

        Returns:
            Complete Suggestion instance with all fields.

        Raises:
            RuntimeError: If no client is available.

        Example:
            >>> partial = PartialSuggestion(boxid=123)
            >>> full = await partial.fetch_full()
            >>> full.actions
            [...]
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.suggestions.get(self.boxid)

    async def edit(self, **kwargs: Any) -> Suggestion:
        """
        Edit this suggestion with the provided field updates.

        Args:
            **kwargs: Fields to update.

        Returns:
            Updated Suggestion instance.

        Raises:
            RuntimeError: If no client is available.

        Example:
            >>> partial = PartialSuggestion(boxid=123)
            >>> updated = await partial.edit(actions=[])
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.suggestions.update(self.boxid, **kwargs)
