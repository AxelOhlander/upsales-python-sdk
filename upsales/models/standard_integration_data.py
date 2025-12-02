"""Standard Integration Data models for Upsales API.

This module provides models for standard integration operations including
test, values, config, OAuth, and events.
"""

from __future__ import annotations

from typing import Any, Literal, TypedDict, Unpack

from pydantic import Field

from upsales.models.base import BaseModel


class StandardIntegrationDataCreateFields(TypedDict, total=False):
    """Available fields for creating standard integration data operations.

    All fields are optional as they depend on the operation type.
    """

    type: Literal[
        "test",
        "values",
        "configButton",
        "testUser",
        "valuesUser",
        "userConfigButton",
        "oauth",
        "events",
    ]
    integrationId: int
    data: dict[str, Any]
    userIds: list[int]


class StandardIntegrationData(BaseModel):
    """Standard Integration Data model for function endpoint operations.

    This model represents the request/response for standard integration
    operations including testing, configuration, OAuth, and events.

    Attributes:
        type: Operation type (test, values, configButton, testUser, valuesUser,
              userConfigButton, oauth, events)
        integrationId: Optional integration identifier
        data: Optional data payload for the operation
        userIds: Optional list of user IDs

    Example:
        >>> # Test integration
        >>> operation = StandardIntegrationData(
        ...     type="test",
        ...     integrationId=123,
        ...     data={"key": "value"}
        ... )
        >>>
        >>> # OAuth operation
        >>> oauth_op = StandardIntegrationData(
        ...     type="oauth",
        ...     integrationId=456
        ... )
    """

    type: Literal[
        "test",
        "values",
        "configButton",
        "testUser",
        "valuesUser",
        "userConfigButton",
        "oauth",
        "events",
    ] = Field(description="Operation type")

    integrationId: int | None = Field(None, description="Integration identifier")

    data: dict[str, Any] | None = Field(None, description="Data payload for the operation")

    userIds: list[int] | None = Field(None, description="List of user IDs")

    async def execute(
        self, **kwargs: Unpack[StandardIntegrationDataCreateFields]
    ) -> dict[str, Any]:
        """Execute the standard integration operation.

        This method sends the operation to the Upsales API and returns
        the response data.

        Args:
            **kwargs: Additional fields to update before execution

        Returns:
            Response data from the API

        Raises:
            RuntimeError: If no client is available

        Example:
            >>> operation = StandardIntegrationData(type="test")
            >>> result = await operation.execute(integrationId=123)
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.standard_integration_data.execute(**self.to_api_dict(**kwargs))


# No PartialModel needed for function endpoints
