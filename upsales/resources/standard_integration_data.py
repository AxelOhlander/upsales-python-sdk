"""Standard Integration Data resource manager for Upsales API.

Provides methods to interact with the /api/v2/function/standardIntegrationData endpoint.

Example:
    >>> async with Upsales(token="...") as upsales:
    ...     result = await upsales.standard_integration_data.execute(
    ...         type="test",
    ...         integrationId=123
    ...     )
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class StandardIntegrationDataResource:
    """Resource manager for Standard Integration Data function endpoint.

    This is a function endpoint (POST-only) for standard integration operations
    including test, values, config, OAuth, and events.

    Example:
        >>> resource = StandardIntegrationDataResource(http_client)
        >>> result = await resource.execute(type="test", integrationId=123)
        >>> oauth_result = await resource.execute(type="oauth", integrationId=456)
    """

    def __init__(self, http: HTTPClient):
        """Initialize standard integration data resource manager.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/function/standardIntegrationData"

    async def execute(
        self,
        type: Literal[  # noqa: A002
            "test",
            "values",
            "configButton",
            "testUser",
            "valuesUser",
            "userConfigButton",
            "oauth",
            "events",
        ],
        integrationId: int | None = None,  # noqa: N803
        data: dict[str, Any] | None = None,
        userIds: list[int] | None = None,  # noqa: N803
    ) -> dict[str, Any]:
        """Execute a standard integration operation.

        Args:
            type: Operation type (test, values, configButton, testUser,
                  valuesUser, userConfigButton, oauth, events)
            integrationId: Optional integration identifier
            data: Optional data payload for the operation
            userIds: Optional list of user IDs

        Returns:
            Response data from the API operation

        Raises:
            ValidationError: If required fields are missing or invalid
            UpsalesError: If API request fails

        Example:
            >>> # Test integration
            >>> result = await resource.execute(
            ...     type="test",
            ...     integrationId=123,
            ...     data={"key": "value"}
            ... )
            >>>
            >>> # OAuth operation
            >>> oauth_result = await resource.execute(
            ...     type="oauth",
            ...     integrationId=456
            ... )
            >>>
            >>> # Events operation with user IDs
            >>> events_result = await resource.execute(
            ...     type="events",
            ...     integrationId=789,
            ...     userIds=[1, 2, 3]
            ... )
        """
        # Build request payload
        payload: dict[str, Any] = {"type": type}

        if integrationId is not None:
            payload["integrationId"] = integrationId

        if data is not None:
            payload["data"] = data

        if userIds is not None:
            payload["userIds"] = userIds

        # Execute POST request
        response = await self._http.post(self._endpoint, json=payload)
        return response

    async def test(self, integrationId: int, data: dict[str, Any] | None = None) -> dict[str, Any]:  # noqa: N803
        """Test a standard integration.

        Args:
            integrationId: Integration identifier
            data: Optional test data

        Returns:
            Test result from the API

        Example:
            >>> result = await resource.test(
            ...     integrationId=123,
            ...     data={"param": "value"}
            ... )
        """
        return await self.execute(type="test", integrationId=integrationId, data=data)

    async def get_values(
        self,
        integrationId: int,
        data: dict[str, Any] | None = None,  # noqa: N803
    ) -> dict[str, Any]:
        """Get values from a standard integration.

        Args:
            integrationId: Integration identifier
            data: Optional data for values query

        Returns:
            Values from the API

        Example:
            >>> values = await resource.get_values(integrationId=123)
        """
        return await self.execute(type="values", integrationId=integrationId, data=data)

    async def config_button(
        self,
        integrationId: int,
        data: dict[str, Any] | None = None,  # noqa: N803
    ) -> dict[str, Any]:
        """Execute config button action for a standard integration.

        Args:
            integrationId: Integration identifier
            data: Optional configuration data

        Returns:
            Configuration result from the API

        Example:
            >>> result = await resource.config_button(
            ...     integrationId=123,
            ...     data={"setting": "value"}
            ... )
        """
        return await self.execute(type="configButton", integrationId=integrationId, data=data)

    async def oauth(self, integrationId: int, data: dict[str, Any] | None = None) -> dict[str, Any]:  # noqa: N803
        """Execute OAuth operation for a standard integration.

        Args:
            integrationId: Integration identifier
            data: Optional OAuth data (code, state, etc.)

        Returns:
            OAuth result from the API

        Example:
            >>> result = await resource.oauth(
            ...     integrationId=123,
            ...     data={"code": "auth_code", "state": "state_token"}
            ... )
        """
        return await self.execute(type="oauth", integrationId=integrationId, data=data)

    async def get_events(
        self,
        integrationId: int,
        data: dict[str, Any] | None = None,  # noqa: N803
    ) -> dict[str, Any]:
        """Get events from a standard integration.

        Args:
            integrationId: Integration identifier
            data: Optional data for events query

        Returns:
            Events from the API

        Example:
            >>> events = await resource.get_events(integrationId=123)
        """
        return await self.execute(type="events", integrationId=integrationId, data=data)

    async def test_user(
        self,
        integrationId: int,
        userIds: list[int],
        data: dict[str, Any] | None = None,  # noqa: N803
    ) -> dict[str, Any]:
        """Test user-specific integration.

        Args:
            integrationId: Integration identifier
            userIds: List of user IDs to test
            data: Optional test data

        Returns:
            Test result from the API

        Example:
            >>> result = await resource.test_user(
            ...     integrationId=123,
            ...     userIds=[1, 2, 3],
            ...     data={"param": "value"}
            ... )
        """
        return await self.execute(
            type="testUser", integrationId=integrationId, userIds=userIds, data=data
        )

    async def get_values_user(
        self,
        integrationId: int,
        userIds: list[int],
        data: dict[str, Any] | None = None,  # noqa: N803
    ) -> dict[str, Any]:
        """Get user-specific values from a standard integration.

        Args:
            integrationId: Integration identifier
            userIds: List of user IDs
            data: Optional data for values query

        Returns:
            User-specific values from the API

        Example:
            >>> values = await resource.get_values_user(
            ...     integrationId=123,
            ...     userIds=[1, 2]
            ... )
        """
        return await self.execute(
            type="valuesUser", integrationId=integrationId, userIds=userIds, data=data
        )

    async def user_config_button(
        self,
        integrationId: int,
        userIds: list[int],
        data: dict[str, Any] | None = None,  # noqa: N803
    ) -> dict[str, Any]:
        """Execute user-specific config button action.

        Args:
            integrationId: Integration identifier
            userIds: List of user IDs
            data: Optional configuration data

        Returns:
            Configuration result from the API

        Example:
            >>> result = await resource.user_config_button(
            ...     integrationId=123,
            ...     userIds=[1],
            ...     data={"setting": "value"}
            ... )
        """
        return await self.execute(
            type="userConfigButton", integrationId=integrationId, userIds=userIds, data=data
        )
