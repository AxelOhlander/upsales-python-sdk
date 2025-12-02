"""Data source resource manager for Upsales API.

Provides methods to interact with the /function/datasource endpoint for
standard integration data source operations.

Example:
    ```python
    async with Upsales(token="...") as upsales:
        # Typeahead search
        results = await upsales.data_source.typeahead(
            integration_id=123,
            type="contact",
            query="john"
        )

        # Buy action
        result = await upsales.data_source.buy(
            integration_id=123,
            type="contact",
            data={"id": "ext123"}
        )
    ```
"""

from typing import Any

from upsales.http import HTTPClient
from upsales.models.data_source import DataSourceResponse


class DataSourceResource:
    """Resource manager for data source function endpoint.

    This resource handles integration data source operations including:
    - typeahead: Search/autocomplete operations
    - buy: Purchase/import operations
    - settings: Configuration operations
    - monitor: Monitoring operations

    Note:
        Unlike standard CRUD resources, this is a function-based endpoint
        that doesn't support get/list/update/delete operations.

    Example:
        ```python
        resource = DataSourceResource(http_client)
        results = await resource.typeahead(
            integration_id=123,
            type="contact",
            query="john"
        )
        ```
    """

    def __init__(self, http: HTTPClient):
        """Initialize data source resource manager.

        Args:
            http: HTTP client for API requests.

        Example:
            ```python
            from upsales.http import HTTPClient
            http = HTTPClient(token="your-token")
            resource = DataSourceResource(http)
            ```
        """
        self.http = http
        self.base_path = "/function/datasource"

    def _prepare_http_kwargs(self, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Prepare kwargs for HTTP client calls."""
        kwargs = dict(params or {})
        if getattr(self.http, "_auto_allow_uninitialized", False):
            kwargs["_allow_uninitialized"] = True
        return kwargs

    async def get(
        self,
        path: str,
        integration_id: int,
        **params: Any,
    ) -> DataSourceResponse:
        """Execute GET request to data source endpoint.

        Args:
            path: Path parameter for the request
            integration_id: ID of the integration
            **params: Additional query parameters

        Returns:
            DataSourceResponse with operation results.

        Raises:
            AuthenticationError: If authentication fails.
            ValidationError: If request parameters are invalid.
            UpsalesError: If the API request fails.

        Example:
            ```python
            result = await resource.get(
                path="config",
                integration_id=123,
            )
            print(result.data)
            ```
        """
        response = await self.http.get(
            f"{self.base_path}/{path}",
            **self._prepare_http_kwargs({"integrationId": integration_id, **params}),
        )
        return DataSourceResponse(**response["data"])

    async def typeahead(
        self,
        integration_id: int,
        type_: str,
        **data: Any,
    ) -> DataSourceResponse:
        """Execute typeahead (search/autocomplete) operation.

        Args:
            integration_id: ID of the integration
            type_: Type of data to search
            **data: Additional data for the search operation

        Returns:
            DataSourceResponse with search results.

        Raises:
            AuthenticationError: If authentication fails.
            ValidationError: If request parameters are invalid.
            UpsalesError: If the API request fails.

        Example:
            ```python
            results = await resource.typeahead(
                integration_id=123,
                type_="contact",
                query="john smith",
                limit=10,
            )
            for contact in results.data.get("results", []):
                print(contact)
            ```
        """
        response = await self.http.post(
            f"{self.base_path}/typeahead",
            **self._prepare_http_kwargs(),
            json={"integrationId": integration_id, "type": type_, **data},
        )
        return DataSourceResponse(**response["data"])

    async def buy(
        self,
        integration_id: int,
        type_: str,
        **data: Any,
    ) -> DataSourceResponse:
        """Execute buy (import/purchase) operation.

        Args:
            integration_id: ID of the integration
            type_: Type of data to import
            **data: Additional data for the import operation

        Returns:
            DataSourceResponse with import results.

        Raises:
            AuthenticationError: If authentication fails.
            ValidationError: If request parameters are invalid.
            UpsalesError: If the API request fails.

        Example:
            ```python
            result = await resource.buy(
                integration_id=123,
                type_="contact",
                external_id="ext_123",
                name="John Smith",
                email="john@example.com",
            )
            print(f"Imported: {result.data}")
            ```
        """
        response = await self.http.post(
            f"{self.base_path}/buy",
            **self._prepare_http_kwargs(),
            json={"integrationId": integration_id, "type": type_, **data},
        )
        return DataSourceResponse(**response["data"])

    async def settings(
        self,
        integration_id: int,
        type_: str,
        **data: Any,
    ) -> DataSourceResponse:
        """Execute settings (configuration) operation.

        Args:
            integration_id: ID of the integration
            type_: Type of settings to configure
            **data: Additional data for the configuration operation

        Returns:
            DataSourceResponse with configuration results.

        Raises:
            AuthenticationError: If authentication fails.
            ValidationError: If request parameters are invalid.
            UpsalesError: If the API request fails.

        Example:
            ```python
            result = await resource.settings(
                integration_id=123,
                type_="sync",
                enabled=True,
                interval=3600,
            )
            print(f"Settings updated: {result.success}")
            ```
        """
        response = await self.http.post(
            f"{self.base_path}/settings",
            **self._prepare_http_kwargs(),
            json={"integrationId": integration_id, "type": type_, **data},
        )
        return DataSourceResponse(**response["data"])

    async def monitor(
        self,
        integration_id: int,
        type_: str,
        **data: Any,
    ) -> DataSourceResponse:
        """Execute monitor (status check) operation.

        Args:
            integration_id: ID of the integration
            type_: Type of monitoring to perform
            **data: Additional data for the monitoring operation

        Returns:
            DataSourceResponse with monitoring results.

        Raises:
            AuthenticationError: If authentication fails.
            ValidationError: If request parameters are invalid.
            UpsalesError: If the API request fails.

        Example:
            ```python
            result = await resource.monitor(
                integration_id=123,
                type_="health",
            )
            print(f"Status: {result.data.get('status')}")
            ```
        """
        response = await self.http.post(
            f"{self.base_path}/monitor",
            **self._prepare_http_kwargs(),
            json={"integrationId": integration_id, "type": type_, **data},
        )
        return DataSourceResponse(**response["data"])


__all__ = ["DataSourceResource"]
