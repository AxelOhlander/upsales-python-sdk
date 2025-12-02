"""Soliditet clients resource manager for Upsales API.

Provides methods to interact with the /soliditet/clients endpoint for
purchasing and refreshing company information from Soliditet.

Example:
    ```python
    async with Upsales(token="...") as upsales:
        # Purchase company data (deducts 1 credit)
        client = await upsales.soliditet_clients.create(
            duns="123456789",
            options={"refresh": False},
            properties=["turnover", "employees"]
        )

        # Refresh company data (deducts 1 credit)
        updated = await upsales.soliditet_clients.update(
            "123456789",
            options={"refresh": True},
            properties=["turnover", "employees"]
        )
    ```
"""

from typing import Any

from upsales.http import HTTPClient
from upsales.models.soliditet_clients import PartialSoliditetClient, SoliditetClient
from upsales.resources.base import BaseResource


class SoliditetClientsResource(BaseResource[SoliditetClient, PartialSoliditetClient]):
    """Resource manager for Soliditet clients endpoint.

    Inherits standard CRUD operations from BaseResource:
    - get(duns) - Get single client by DUNS number
    - create(duns, options, properties) - Purchase company data (deducts 1 credit)
    - update(duns, options, properties) - Refresh company data (deducts 1 credit)

    Note:
        Both create and update operations deduct 1 credit from your Soliditet balance.

    Example:
        ```python
        resource = SoliditetClientsResource(http_client)
        client = await resource.create(
            duns="123456789",
            options={},
            properties=["name", "turnover", "employees"]
        )
        ```
    """

    def __init__(self, http: HTTPClient):
        """Initialize soliditet clients resource manager.

        Args:
            http: HTTP client for API requests
        """
        super().__init__(
            http=http,
            endpoint="/soliditet/clients",
            model_class=SoliditetClient,
            partial_class=PartialSoliditetClient,
        )

    async def purchase(
        self, duns: str, options: dict[str, Any], properties: list[str]
    ) -> SoliditetClient:
        """Purchase company data from Soliditet.

        Deducts 1 credit from your Soliditet balance.

        Args:
            duns: DUNS number of the company
            options: Purchase options
            properties: List of properties to retrieve

        Returns:
            SoliditetClient with purchased data

        Raises:
            ValidationError: If data is invalid
            ServerError: If purchase fails

        Example:
            ```python
            client = await resource.purchase(
                duns="123456789",
                options={"refresh": False},
                properties=["name", "turnover", "employees"]
            )
            ```
        """
        return await self.create(duns=duns, options=options, properties=properties)

    async def refresh(
        self, duns: str, options: dict[str, Any], properties: list[str]
    ) -> SoliditetClient:
        """Refresh company data from Soliditet.

        Deducts 1 credit from your Soliditet balance.

        Args:
            duns: DUNS number of the company
            options: Refresh options
            properties: List of properties to retrieve

        Returns:
            SoliditetClient with refreshed data

        Raises:
            ValidationError: If data is invalid
            NotFoundError: If client not found
            ServerError: If refresh fails

        Example:
            ```python
            client = await resource.refresh(
                duns="123456789",
                options={"refresh": True},
                properties=["turnover", "employees"]
            )
            ```
        """
        # This endpoint uses PUT with DUNS string, not int ID
        response = await self._http.put(
            f"{self._endpoint}/{duns}", options=options, properties=properties
        )
        return self._model_class(**response["data"], _client=self._http._upsales_client)
