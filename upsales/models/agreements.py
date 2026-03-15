"""
Agreement models for Upsales API.

This module provides models for recurring revenue agreements in Upsales.
"""

from typing import Any, TypedDict, Unpack

from pydantic import Field, computed_field, field_serializer

from upsales.models.base import BaseModel, PartialModel
from upsales.models.company import PartialCompany
from upsales.models.contacts import PartialContact
from upsales.models.custom_fields import CustomFields
from upsales.models.user import PartialUser
from upsales.validators import CustomFieldsList


class AgreementUpdateFields(TypedDict, total=False):
    """
    Available fields for updating an Agreement.

    All fields are optional. Only include fields you want to update.

    WARNING - Parent Agreements with Children:
        When updating a parent agreement (one that has children), you MUST
        include the full `children` array. Omitting children or sending
        `children: []` will corrupt the agreement structure or delete all
        child periods.

    Args:
        createDiffOrder: Set to True to create a diff order for mid-period
            changes. Set to False to suppress diff order creation.
        notify: Set to False to suppress notifications when updating.
    """

    description: str
    notes: str
    user: dict[str, Any]
    client: dict[str, Any]
    contact: dict[str, Any]
    project: dict[str, Any]
    stage: dict[str, Any]
    clientConnection: dict[str, Any]
    currencyRate: int
    currency: str
    custom: list[dict[str, Any]]
    orderRow: list[dict[str, Any]]
    metadata: dict[str, Any]
    priceListId: int
    invoiceRelatedClient: bool
    agreementGroupId: int
    children: list[dict[str, Any]]
    createDiffOrder: bool
    notify: bool


class Agreement(BaseModel):
    """
    Agreement model representing a recurring revenue agreement.

    Agreements handle subscription-style recurring revenue with automatic
    order creation based on defined intervals and periods.

    Examples:
        Create a new agreement:
            >>> agreement = await upsales.agreements.create(
            ...     description="Annual Software License",
            ...     user={"id": 1},
            ...     client={"id": 100},
            ...     stage={"id": 1},
            ...     orderRow=[{
            ...         "product": {"id": 10},
            ...         "price": 1200,
            ...         "quantity": 1
            ...     }],
            ...     metadata={
            ...         "agreementStartdate": "2025-01-01",
            ...         "agreementIntervalPeriod": 12,
            ...         "agreementOrderCreationTime": 1,
            ...         "periodLength": 12
            ...     }
            ... )

        Update an agreement:
            >>> await agreement.edit(
            ...     description="Updated Description",
            ...     metadata={"agreementEnddate": "2026-12-31"}
            ... )
    """

    # Read-only fields
    id: int = Field(frozen=True, strict=True, description="Unique agreement ID")
    regDate: str = Field(default="", frozen=True, description="Registration date (ISO 8601)")
    modDate: str = Field(default="", frozen=True, description="Last modification date (ISO 8601)")
    regBy: PartialUser | None = Field(None, frozen=True, description="User who created this")
    userRemovable: bool = Field(default=True, frozen=True, description="Whether user can delete this")
    userEditable: bool = Field(default=True, frozen=True, description="Whether user can edit this")
    value: int | float = Field(default=0, frozen=True, description="Agreement value in agreement currency")
    orderValue: int | float = Field(
        default=0, frozen=True, description="Deprecated: use value instead"
    )
    contributionMargin: int | float = Field(default=0, frozen=True, description="Contribution margin")
    contributionMarginInAgreementCurrency: int | float = Field(
        default=0, frozen=True, description="Contribution margin in agreement currency"
    )
    valueInMasterCurrency: int | float = Field(default=0, frozen=True, description="Value in master currency")
    yearlyValue: int | float = Field(default=0, frozen=True, description="Yearly value")
    yearlyValueInMasterCurrency: int | float = Field(
        default=0, frozen=True, description="Yearly value in master currency"
    )
    yearlyContributionMargin: int | float = Field(
        default=0, frozen=True, description="Yearly contribution margin"
    )
    yearlyContributionMarginInAgreementCurrency: int | float = Field(
        default=0, frozen=True, description="Yearly contribution margin in agreement currency"
    )
    purchaseCost: int | float = Field(default=0, frozen=True, description="Purchase cost")
    isParent: bool = Field(default=False, frozen=True, description="Whether this is a parent agreement")
    children: list[dict[str, Any]] = Field(
        default=[],
        description="Child agreements. WARNING: Must be included when updating parent agreements!",
    )
    parentId: Any | None = Field(None, frozen=True, description="Parent agreement ID")

    # Updatable fields
    description: str = Field(default="", description="Agreement description")
    notes: str | None = Field(None, description="Additional notes")
    user: PartialUser | None = Field(default=None, description="Responsible user")
    client: PartialCompany | None = Field(default=None, alias="client", description="Company/account")
    contact: PartialContact | None = Field(None, description="Contact person")
    project: Any | None = Field(None, description="Related project")
    stage: dict[str, Any] = Field(default_factory=dict, description="Agreement stage with id and name")
    clientConnection: Any | None = Field(None, description="Client connection")
    currencyRate: int | float = Field(default=1, description="Currency exchange rate")
    currency: str = Field(default="", description="Currency code (3 chars)")
    custom: CustomFieldsList = Field(default=[], description="Custom fields")
    orderRow: list[dict[str, Any]] = Field(
        default=[], description="Order rows with product, price, quantity"
    )
    metadata: dict[str, Any] = Field(default={}, description="Agreement metadata")
    priceListId: int = Field(description="Price list ID")
    invoiceRelatedClient: bool = Field(description="Whether to invoice related client")
    agreementGroupId: int | None = Field(None, description="Agreement group ID")
    indexIncreaseId: Any | None = Field(None, description="Index increase ID")
    latestIndexIncreaseId: Any | None = Field(None, description="Latest index increase ID")
    latestIndexIncreaseDate: Any | None = Field(None, description="Latest index increase date")

    @computed_field
    @property
    def custom_fields(self) -> CustomFields:
        """
        Access custom fields with dict-like interface.

        Returns:
            CustomFields helper for easy field access by ID or alias.

        Examples:
            >>> agreement.custom_fields.get(11)
            'value'
            >>> agreement.custom_fields.get_by_alias('FIELD_ALIAS')
            'value'
        """
        return CustomFields(self.custom)

    @field_serializer("custom", when_used="json")
    def serialize_custom_fields(self, custom: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Serialize custom fields for API requests.

        Only includes fields with non-null values.

        Args:
            custom: Custom fields list.

        Returns:
            Cleaned custom fields for API.
        """
        return [
            {"fieldId": item["fieldId"], "value": item.get("value")}
            for item in custom
            if "value" in item and item.get("value") is not None
        ]

    async def edit(self, **kwargs: Unpack[AgreementUpdateFields]) -> "Agreement":
        """
        Edit this agreement.

        Args:
            **kwargs: Fields to update. See AgreementUpdateFields for available fields.

        Returns:
            Updated agreement instance.

        Raises:
            RuntimeError: If no client available.

        Warning:
            When updating a parent agreement (isParent=True), you MUST include
            the full `children` array. Omitting it will corrupt the agreement
            structure. Send `children=self.children` to preserve existing children.

            Use `createDiffOrder=False` to suppress diff order creation for
            manual price increases. Use `notify=False` to suppress notifications.

        Examples:
            >>> # Simple update (non-parent agreement)
            >>> await agreement.edit(
            ...     description="Updated Description",
            ...     metadata={"agreementEnddate": "2026-12-31"}
            ... )
            >>>
            >>> # Safe update for parent agreement - ALWAYS include children!
            >>> await agreement.edit(
            ...     description="Updated",
            ...     children=agreement.children,  # Preserve children!
            ... )
            >>>
            >>> # Manual price increase without diff order
            >>> await agreement.edit(
            ...     orderRow=new_order_rows,
            ...     createDiffOrder=False,
            ...     notify=False,
            ... )
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.agreements.update(self.id, **self.to_api_dict(**kwargs))


class PartialAgreement(PartialModel):
    """
    Partial Agreement model for nested responses.

    Used when agreements appear in other API responses.

    Examples:
        Fetch full agreement:
            >>> full_agreement = await partial.fetch_full()

        Edit partial agreement:
            >>> await partial.edit(description="Updated")
    """

    id: int = Field(description="Unique agreement ID")
    description: str | None = Field(None, description="Agreement description")

    async def fetch_full(self) -> Agreement:
        """
        Fetch full agreement data from API.

        Returns:
            Complete Agreement instance.

        Raises:
            RuntimeError: If no client available.
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.agreements.get(self.id)

    async def edit(self, **kwargs: Unpack[AgreementUpdateFields]) -> Agreement:
        """
        Edit this agreement.

        Args:
            **kwargs: Fields to update.

        Returns:
            Updated agreement instance.

        Raises:
            RuntimeError: If no client available.
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.agreements.update(self.id, **kwargs)
