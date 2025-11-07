"""
Order models for Upsales API.

Generated from /api/v2/orders endpoint.
Analysis based on 70 samples.

Enhanced with Pydantic v2 features:
- Reusable validators (BinaryFlag, Percentage, CustomFieldsList, NonEmptyStr, PositiveInt)
- Computed fields (@computed_field)
- Field serialization (@field_serializer)
- Strict type checking
- Field descriptions (100% coverage)
- Optimized serialization via to_api_dict()
- TypedDict for IDE autocomplete

Field optionality determined by:
- Required: Field present AND non-null in 100% of samples
- Optional: Field missing OR null in any sample
- Custom fields: Always optional with default []
"""

from typing import Any, TypedDict, Unpack

from pydantic import Field, computed_field, field_serializer

from upsales.models.base import BaseModel, PartialModel
from upsales.models.company import PartialCompany
from upsales.models.contacts import PartialContact
from upsales.models.custom_fields import CustomFields
from upsales.models.orderStages import PartialOrderStage
from upsales.models.user import PartialUser
from upsales.validators import BinaryFlag, CustomFieldsList, Percentage, PositiveInt


class OrderCreateFields(TypedDict, total=False):
    """
    Required and optional fields for creating a new Order.

    REQUIRED fields (must be provided):
    - orderRow: List with at least one row containing product.id
    - date: Order date in 'YYYY-MM-DD' format
    - user: Dict with user.id (order owner)
    - stage: Dict with stage.id (pipeline stage)
    - client: Dict with client.id (company/account)

    IMPORTANT: Nested fields require minimal structure with just IDs.
    Example nested user: {"id": 10} NOT the full PartialUser object.

    All other fields are optional during creation.

    Example:
        >>> new_order = await upsales.orders.create(
        ...     orderRow=[{"product": {"id": 5}}],
        ...     date="2025-01-15",
        ...     user={"id": 10},
        ...     stage={"id": 3},
        ...     client={"id": 123},
        ...     description="New Enterprise Deal",  # Optional
        ...     probability=50,  # Optional
        ...     value=100000,  # Optional
        ... )
    """

    # REQUIRED fields for creation
    orderRow: list[dict[str, Any]]  # Required: [{"product": {"id": product_id}}]
    date: str  # Required: 'YYYY-MM-DD'
    user: dict[str, int]  # Required: {"id": user_id}
    stage: dict[str, int]  # Required: {"id": stage_id}
    client: dict[str, int]  # Required: {"id": client_id}

    # Optional core fields
    description: str
    notes: str
    closeDate: str
    probability: int
    value: int
    currency: str
    currencyRate: int

    # Optional monetary values
    oneOffValue: int
    monthlyValue: int
    annualValue: int
    purchaseCost: int
    contributionMargin: int

    # Optional relationships (also use minimal ID structure)
    contact: dict[str, int]  # Optional: {"id": contact_id}

    # Optional configuration
    priceListId: int
    recurringInterval: int
    locked: int

    # Optional custom fields
    custom: list[dict[str, Any]]


class OrderUpdateFields(TypedDict, total=False):
    """
    Available fields for updating an Order.

    All fields are optional. Use with Unpack for IDE autocomplete.
    Does not include read-only fields (id, regDate, modDate).
    """

    # Core order fields
    description: str
    notes: str
    date: str
    closeDate: str
    probability: int
    value: int
    currency: str
    currencyRate: int

    # Monetary values
    oneOffValue: int
    monthlyValue: int
    annualValue: int
    purchaseCost: int
    contributionMargin: int
    contributionMarginLocalCurrency: int

    # Master currency values (read-only, calculated by API)
    valueInMasterCurrency: int
    oneOffValueInMasterCurrency: int
    monthlyValueInMasterCurrency: int
    annualValueInMasterCurrency: int

    # Weighted values (calculated by API based on probability)
    weightedValue: int
    weightedOneOffValue: int
    weightedMonthlyValue: int
    weightedAnnualValue: int
    weightedContributionMargin: int
    weightedContributionMarginLocalCurrency: int
    weightedValueInMasterCurrency: int
    weightedOneOffValueInMasterCurrency: int
    weightedMonthlyValueInMasterCurrency: int
    weightedAnnualValueInMasterCurrency: int

    # Relationships
    client: dict[str, Any]
    contact: dict[str, Any]
    user: dict[str, Any]
    stage: dict[str, Any]
    regBy: dict[str, Any]

    # Configuration
    priceListId: int
    recurringInterval: int
    locked: int
    invoiceRelatedClient: bool
    confirmedSolution: bool
    userEditable: bool
    userRemovable: bool

    # Optional associations
    agreement: Any
    project: Any
    competitorId: Any
    lostReason: Any
    confirmedDate: Any
    confirmedBudget: Any
    marketingContribution: Any
    clientConnection: Any
    userSalesStatistics: Any

    # Lists
    orderRow: list[dict[str, Any]]
    checklist: list[Any]
    stakeholders: list[Any]
    titleCategories: list[Any]
    projectPlanOptions: list[Any]
    salesCoach: list[dict[str, Any]]
    lastIntegrationStatus: list[dict[str, Any]]

    # Statistics
    noCompletedAppointments: int
    noPostponedAppointments: int
    noTimesCallsNotAnswered: int
    noTimesClosingDateChanged: int
    noTimesOrderValueChanged: int

    # Complex objects
    risks: dict[str, Any]

    # Custom fields
    custom: list[Any]


class Order(BaseModel):
    """
    Order model from /api/v2/orders.

    Represents an order (opportunity/deal) in the Upsales system with full data.
    Enhanced with Pydantic v2 validators, computed fields, and optimized serialization.

    Generated from 70 samples with field analysis.

    CREATING ORDERS:
        Use OrderCreateFields TypedDict for required field reference.
        Required fields use MINIMAL nested structure with just IDs:
        - orderRow: [{"product": {"id": product_id}}]
        - date: "YYYY-MM-DD"
        - user: {"id": user_id}
        - stage: {"id": stage_id}
        - client: {"id": client_id}

    UPDATING ORDERS:
        Use OrderUpdateFields TypedDict for IDE autocomplete.
        All fields optional, nested objects can be full or minimal.

    Example Create:
        >>> new_order = await upsales.orders.create(
        ...     orderRow=[{"product": {"id": 5}}],
        ...     date="2025-01-15",
        ...     user={"id": 10},
        ...     stage={"id": 3},
        ...     client={"id": 123},
        ...     description="New Enterprise Deal",
        ...     probability=50,
        ...     value=100000,
        ... )

    Example Read:
        >>> order = await upsales.orders.get(1)
        >>> order.description
        'New Enterprise Deal'
        >>> order.is_locked  # Computed property
        False
        >>> order.expected_value  # Computed from value * probability
        45000.0
        >>> order.custom_fields[11]  # Access custom fields
        'value'

    Example Update:
        >>> await order.edit(probability=75, value=100000)  # IDE autocomplete
    """

    # Read-only fields (frozen=True, strict=True)
    id: PositiveInt = Field(frozen=True, strict=True, description="Unique order ID")
    regDate: str = Field(frozen=True, description="Registration date (ISO 8601)")
    modDate: str = Field(frozen=True, description="Last modification date (ISO 8601)")

    # Core order fields
    description: str = Field(description="Order description/title")
    date: str = Field(description="Order date (ISO 8601)")
    probability: Percentage = Field(description="Win probability percentage (0-100)")
    value: int = Field(default=0, description="Order value in local currency")
    currency: str = Field(default="SEK", description="Currency code (ISO 4217)")
    currencyRate: int = Field(default=1, description="Exchange rate to master currency")

    # Monetary values
    oneOffValue: int = Field(default=0, description="One-time value in local currency")
    monthlyValue: int = Field(default=0, description="Monthly recurring value in local currency")
    annualValue: int = Field(default=0, description="Annual recurring value in local currency")
    purchaseCost: int = Field(default=0, description="Purchase cost in local currency")
    contributionMargin: int = Field(default=0, description="Contribution margin in local currency")
    contributionMarginLocalCurrency: int = Field(
        default=0, description="Contribution margin (local)"
    )

    # Master currency values (calculated by API)
    valueInMasterCurrency: int = Field(default=0, description="Order value in master currency")
    oneOffValueInMasterCurrency: int = Field(
        default=0, description="One-time value in master currency"
    )
    monthlyValueInMasterCurrency: int = Field(
        default=0, description="Monthly value in master currency"
    )
    annualValueInMasterCurrency: int = Field(
        default=0, description="Annual value in master currency"
    )

    # Weighted values (calculated by API based on probability)
    weightedValue: int = Field(default=0, description="Weighted value (value * probability / 100)")
    weightedOneOffValue: int = Field(default=0, description="Weighted one-time value")
    weightedMonthlyValue: int = Field(default=0, description="Weighted monthly value")
    weightedAnnualValue: int = Field(default=0, description="Weighted annual value")
    weightedContributionMargin: int = Field(default=0, description="Weighted contribution margin")
    weightedContributionMarginLocalCurrency: int = Field(
        default=0, description="Weighted contribution margin (local)"
    )
    weightedValueInMasterCurrency: int = Field(
        default=0, description="Weighted value in master currency"
    )
    weightedOneOffValueInMasterCurrency: int = Field(
        default=0, description="Weighted one-time value in master currency"
    )
    weightedMonthlyValueInMasterCurrency: int = Field(
        default=0, description="Weighted monthly value in master currency"
    )
    weightedAnnualValueInMasterCurrency: int = Field(
        default=0, description="Weighted annual value in master currency"
    )

    # Relationships (nested objects - use dict for complex/varying structures)
    client: PartialCompany = Field(description="Associated company/account")
    user: PartialUser = Field(description="Order owner/responsible user")
    stage: PartialOrderStage | None = Field(default=None, description="Order stage/pipeline phase")
    regBy: PartialUser | None = Field(default=None, description="User who registered the order")
    contact: PartialContact | None = Field(default=None, description="Primary contact person")

    # Configuration
    priceListId: PositiveInt = Field(default=0, description="Associated price list ID")
    recurringInterval: PositiveInt = Field(
        default=0, description="Recurring interval (0=one-time, 1=monthly, 12=annual)"
    )
    locked: BinaryFlag = Field(default=0, description="Lock status (0=unlocked, 1=locked)")
    invoiceRelatedClient: bool = Field(default=False, description="Invoice related to client")
    confirmedSolution: bool = Field(default=False, description="Solution confirmed by customer")
    userEditable: bool = Field(default=True, description="User can edit this order")
    userRemovable: bool = Field(default=True, description="User can delete this order")

    # Optional dates and references
    closeDate: str | None = Field(default=None, description="Expected close date (ISO 8601)")
    notes: str | None = Field(default=None, description="Order notes/comments")
    confirmedDate: Any | None = Field(default=None, description="Date when order was confirmed")
    confirmedBudget: Any | None = Field(default=None, description="Confirmed budget amount")
    agreement: Any | None = Field(default=None, description="Associated agreement")
    project: Any | None = Field(default=None, description="Associated project")
    competitorId: Any | None = Field(default=None, description="Competitor ID")
    lostReason: Any | None = Field(default=None, description="Reason for lost order")
    marketingContribution: Any | None = Field(
        default=None, description="Marketing contribution data"
    )
    clientConnection: Any | None = Field(default=None, description="Client connection data")
    userSalesStatistics: Any | None = Field(default=None, description="User sales statistics")

    # Lists
    orderRow: list[dict[str, Any]] = Field(
        default_factory=list, description="Order rows/line items"
    )
    checklist: list[Any] = Field(default_factory=list, description="Order checklist items")
    stakeholders: list[Any] = Field(default_factory=list, description="Order stakeholders")
    titleCategories: list[Any] = Field(default_factory=list, description="Order categories")
    projectPlanOptions: list[Any] = Field(default_factory=list, description="Project plan options")
    salesCoach: list[dict[str, Any]] = Field(
        default_factory=list, description="Sales coach assignments"
    )
    lastIntegrationStatus: list[dict[str, Any]] = Field(
        default_factory=list, description="Last integration status"
    )

    # Statistics (counters)
    noCompletedAppointments: PositiveInt = Field(
        default=0, description="Number of completed appointments"
    )
    noPostponedAppointments: PositiveInt = Field(
        default=0, description="Number of postponed appointments"
    )
    noTimesCallsNotAnswered: PositiveInt = Field(
        default=0, description="Number of unanswered calls"
    )
    noTimesClosingDateChanged: PositiveInt = Field(
        default=0, description="Number of close date changes"
    )
    noTimesOrderValueChanged: PositiveInt = Field(default=0, description="Number of value changes")

    # Complex objects
    risks: dict[str, Any] = Field(default_factory=dict, description="Order risk assessment data")

    # Custom fields (validated structure)
    custom: CustomFieldsList = Field(
        default_factory=list, description="Custom fields with validated structure"
    )
    periodization: dict[str, Any] | None = Field(
        None, description="Revenue periodization data for recurring orders"
    )

    @computed_field
    @property
    def custom_fields(self) -> CustomFields:
        """
        Access custom fields with dict-like interface.

        Returns:
            CustomFields helper for easy access by ID or alias.

        Example:
            >>> order.custom_fields[11]  # By field ID
            'value'
            >>> order.custom_fields.get(11, "default")
            'value'
            >>> order.custom_fields.by_alias("ORDER_TYPE")
            'Enterprise'
        """
        return CustomFields(self.custom)

    @computed_field
    @property
    def is_locked(self) -> bool:
        """
        Check if order is locked.

        Returns:
            True if locked flag is 1, False otherwise.

        Example:
            >>> order.is_locked
            False
            >>> await order.edit(locked=1)
            >>> order.is_locked
            True
        """
        return self.locked == 1

    @computed_field
    @property
    def expected_value(self) -> float:
        """
        Calculate expected value based on probability.

        Expected value = value * (probability / 100)

        Returns:
            Order value weighted by win probability.

        Example:
            >>> order.value = 100000
            >>> order.probability = 45
            >>> order.expected_value
            45000.0
        """
        if self.value and self.probability is not None:
            return (self.value * self.probability) / 100
        return 0.0

    @computed_field
    @property
    def is_recurring(self) -> bool:
        """
        Check if order has recurring revenue.

        Returns:
            True if monthlyValue or annualValue is greater than 0.

        Example:
            >>> order.monthlyValue = 5000
            >>> order.is_recurring
            True
        """
        return bool(self.monthlyValue > 0 or self.annualValue > 0)

    @computed_field
    @property
    def margin_percentage(self) -> float:
        """
        Calculate contribution margin as percentage of order value.

        Returns:
            Margin percentage (0-100), or 0 if value is 0.

        Example:
            >>> order.value = 100000
            >>> order.contributionMargin = 35000
            >>> order.margin_percentage
            35.0
        """
        if self.value and self.value > 0:
            return (self.contributionMargin / self.value) * 100
        return 0.0

    @field_serializer("custom", when_used="json")
    def serialize_custom_fields(self, custom: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """
        Serialize custom fields for API requests.

        Removes fields without values to keep API payloads clean.

        Args:
            custom: List of custom field dicts from model.

        Returns:
            Cleaned list with only fields that have values.

        Example:
            >>> # Removes items without 'value' key
            >>> [{"fieldId": 11, "value": "data"}]  # Kept
            >>> [{"fieldId": 12}]  # Removed (no value)
        """
        return [
            {"fieldId": item["fieldId"], "value": item.get("value")}
            for item in custom
            if "value" in item and item.get("value") is not None
        ]

    async def edit(self, **kwargs: Unpack[OrderUpdateFields]) -> "Order":
        """
        Edit this order via the API.

        Uses to_api_dict() for Pydantic v2 optimized serialization (5-50x faster).
        Automatically excludes frozen fields and handles field aliases.

        Args:
            **kwargs: Fields to update (from OrderUpdateFields TypedDict).

        Returns:
            Updated Order object with fresh data from API.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> order = await upsales.orders.get(1)
            >>> updated = await order.edit(
            ...     probability=75,
            ...     value=150000,
            ...     closeDate="2025-12-31"
            ... )
            >>> print(updated.expected_value)
            112500.0
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.orders.update(self.id, **self.to_api_dict(**kwargs))


class PartialOrder(PartialModel):
    """
    Partial Order for nested responses.

    Contains minimal fields for when Order appears nested in other
    API responses (e.g., as related order, parent order, etc.).

    Use fetch_full() to get complete Order object with all fields.

    Example:
        >>> company = await upsales.companies.get(1)
        >>> related_order = company.related_order  # PartialOrder
        >>> full_order = await related_order.fetch_full()  # Now Order
    """

    # Minimum fields for partial order
    id: PositiveInt = Field(frozen=True, strict=True, description="Unique order ID")
    description: str | None = Field(default=None, description="Order description/title")
    value: int | None = Field(default=None, description="Order value")
    probability: Percentage | None = Field(
        default=None, description="Win probability percentage (0-100)"
    )

    async def fetch_full(self) -> Order:
        """
        Fetch complete order data from API.

        Returns:
            Full Order object with all fields populated.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> partial = company.related_order  # PartialOrder
            >>> full = await partial.fetch_full()  # Order
            >>> full.custom_fields[11]  # Now available
            'value'
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.orders.get(self.id)

    async def edit(self, **kwargs: Unpack[OrderUpdateFields]) -> Order:
        """
        Edit order via partial reference.

        Args:
            **kwargs: Fields to update.

        Returns:
            Updated full Order object from API.

        Raises:
            RuntimeError: If no client reference available.

        Example:
            >>> partial = company.related_order  # PartialOrder
            >>> updated = await partial.edit(probability=90)  # Returns Order
            >>> updated.expected_value
            90000.0
        """
        if not self._client:
            raise RuntimeError("No client available")
        return await self._client.orders.update(self.id, **kwargs)
