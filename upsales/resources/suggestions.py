"""
Suggestions resource manager for Upsales API.

Provides methods to interact with the /prospectingsuggestion endpoint.
This endpoint provides AI-powered suggestions for prospecting existing customers.

Example:
    >>> async with Upsales(token="...") as upsales:
    ...     suggestion = await upsales.suggestions.get(boxid=123)
    ...     updated = await upsales.suggestions.update(boxid=123, actions=[...])
"""

from typing import Any

from upsales.http import HTTPClient
from upsales.models.suggestions import PartialSuggestion, Suggestion
from upsales.resources.base import BaseResource


class SuggestionsResource(BaseResource[Suggestion, PartialSuggestion]):
    """
    Resource manager for Suggestion endpoint.

    This is a special endpoint that uses boxid instead of standard id parameter.
    Operations are limited to GET and POST based on API specification.

    Methods:
    - get(boxid) - Get suggestion by box ID
    - update(boxid, **data) - Update suggestion actions
    - create(boxid, **data) - Create suggestion (same as update)

    Example:
        >>> resource = SuggestionsResource(http_client)
        >>> suggestion = await resource.get(boxid=123)
        >>> updated = await resource.update(boxid=123, actions=[{"type": "call"}])
    """

    def __init__(self, http: HTTPClient):
        """
        Initialize suggestions resource manager.

        Args:
            http: HTTP client for API requests.
        """
        super().__init__(
            http=http,
            endpoint="/prospectingsuggestion",
            model_class=Suggestion,
            partial_class=PartialSuggestion,
        )

    async def get(self, boxid: int) -> Suggestion:
        """
        Get a suggestion by box ID.

        Args:
            boxid: The box ID to fetch suggestions for.

        Returns:
            Suggestion instance with all fields.

        Raises:
            NotFoundError: If boxid doesn't exist.
            UpsalesError: For other API errors.

        Example:
            >>> suggestion = await resource.get(boxid=123)
            >>> suggestion.actions
            [...]
        """
        response = await self._http.get(f"{self._endpoint}/{boxid}")
        return self._model_class(
            **response["data"], _client=self._http._upsales_client
        )

    async def update(self, boxid: int, **data: Any) -> Suggestion:  # type: ignore[override]
        """
        Update a suggestion's actions.

        Args:
            boxid: The box ID to update.
            **data: Fields to update (typically 'actions').

        Returns:
            Updated Suggestion instance.

        Raises:
            NotFoundError: If boxid doesn't exist.
            ValidationError: If data is invalid.
            UpsalesError: For other API errors.

        Example:
            >>> updated = await resource.update(
            ...     boxid=123,
            ...     actions=[{"type": "call", "status": "completed"}]
            ... )
        """
        response = await self._http.post(f"{self._endpoint}/{boxid}", data=data)
        return self._model_class(
            **response["data"], _client=self._http._upsales_client
        )

    async def create(self, boxid: int, **data: Any) -> Suggestion:  # type: ignore[override]
        """
        Create a suggestion (same as update for this endpoint).

        Args:
            boxid: The box ID to create suggestion for.
            **data: Fields to set (typically 'actions').

        Returns:
            Created Suggestion instance.

        Raises:
            ValidationError: If data is invalid.
            UpsalesError: For other API errors.

        Example:
            >>> suggestion = await resource.create(
            ...     boxid=123,
            ...     actions=[{"type": "email"}]
            ... )
        """
        return await self.update(boxid=boxid, **data)
