"""Models for Soliditet clients endpoint.

This module provides models for managing Soliditet client data (purchase and refresh
company information).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pydantic import Field

from upsales.models.base import BaseModel, PartialModel

if TYPE_CHECKING:
    from typing import TypedDict, Unpack

    class SoliditetClientUpdateFields(TypedDict, total=False):
        """Available fields for updating a SoliditetClient.

        All fields are optional for updates.
        """

        options: dict[str, Any]
        properties: list[str]


class SoliditetClient(BaseModel):
    """Represents a Soliditet client with company information.

    This model contains company data purchased or refreshed from Soliditet.
    Each purchase or refresh operation deducts 1 credit.

    Note:
        This endpoint uses DUNS numbers (strings) as identifiers instead of integer IDs.

    Attributes:
        dunsNo: DUNS number identifier (primary key)
        name: Company name
        turnover: Company turnover/revenue
        headquarters: Headquarters location
        city: City location
        country: Country location
        orgNo: Organization number
        sniCode: SNI code (industry classification)
        noOfEmployeesExact: Exact number of employees

    Example:
        ```python
        # Get Soliditet client data
        client = await upsales.soliditet_clients.get("123456789")
        print(f"Company: {client.name}")
        print(f"Employees: {client.noOfEmployeesExact}")
        ```
    """

    # Override id from BaseModel - this endpoint uses DUNS numbers instead
    id: int | None = Field(None, frozen=True, description="Not used (uses dunsNo)")  # type: ignore[assignment]
    dunsNo: str | int | None = Field(None, description="DUNS number identifier")
    name: str | None = Field(None, description="Company name")
    turnover: float | None = Field(None, description="Company turnover/revenue")
    headquarters: str | None = Field(None, description="Headquarters location")
    city: str | None = Field(None, description="City location")
    country: str | None = Field(None, description="Country location")
    orgNo: str | int | None = Field(None, description="Organization number")
    sniCode: str | None = Field(None, description="SNI code (industry classification)")
    noOfEmployeesExact: int | None = Field(None, description="Exact number of employees")

    if TYPE_CHECKING:

        async def edit(self, **kwargs: Unpack[SoliditetClientUpdateFields]) -> SoliditetClient:
            """Edit this Soliditet client.

            Updates the client data by refreshing from Soliditet (deducts 1 credit).

            Args:
                **kwargs: Fields to update (options, properties)

            Returns:
                Updated SoliditetClient instance

            Raises:
                RuntimeError: If no client is available
                ValidationError: If update data is invalid
                NotFoundError: If client not found

            Example:
                ```python
                # Refresh client data
                updated = await client.edit(
                    options={"refresh": True},
                    properties=["turnover", "employees"]
                )
                ```
            """
            ...


class PartialSoliditetClient(PartialModel):
    """Partial Soliditet client model for nested references.

    Used when Soliditet client data appears in other API responses.

    Note:
        This endpoint uses DUNS numbers (strings) as identifiers instead of integer IDs.

    Attributes:
        dunsNo: DUNS number identifier (primary key)
        name: Company name

    Example:
        ```python
        # Fetch full client data
        full_client = await partial_client.fetch_full()
        ```
    """

    # Override id from PartialModel - this endpoint uses DUNS numbers instead
    id: int | None = Field(None, description="Not used (uses dunsNo)")  # type: ignore[assignment]
    dunsNo: str = Field(description="DUNS number identifier")
    name: str | None = Field(None, description="Company name")

    async def fetch_full(self) -> SoliditetClient:
        """Fetch the complete SoliditetClient object.

        Returns:
            Full SoliditetClient instance

        Raises:
            RuntimeError: If no client is available
            NotFoundError: If client not found

        Example:
            ```python
            full_client = await partial_client.fetch_full()
            print(full_client.turnover)
            ```
        """
        if not self._client:
            raise RuntimeError("No client available")
        # Note: This endpoint uses DUNS number as string ID, not integer
        result = await self._client.http.get(
            f"{self._client.soliditet_clients._endpoint}/{self.dunsNo}"
        )
        return SoliditetClient.model_validate(result)

    if TYPE_CHECKING:

        async def edit(self, **kwargs: Unpack[SoliditetClientUpdateFields]) -> SoliditetClient:
            """Edit this Soliditet client.

            Updates the client data by refreshing from Soliditet (deducts 1 credit).

            Args:
                **kwargs: Fields to update

            Returns:
                Updated SoliditetClient instance

            Raises:
                RuntimeError: If no client is available
                ValidationError: If update data is invalid
                NotFoundError: If client not found

            Example:
                ```python
                updated = await partial_client.edit(
                    options={"refresh": True},
                    properties=["turnover"]
                )
                ```
            """
            ...
