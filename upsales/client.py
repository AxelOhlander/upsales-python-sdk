"""
Main Upsales API client.

Uses Python 3.13 native type hints and modern features throughout.

Example:
    >>> import asyncio
    >>> from upsales import Upsales
    >>>
    >>> async def main():
    ...     # From environment variables (.env file)
    ...     async with Upsales.from_env() as upsales:
    ...         user = await upsales.users.get(1)
    ...         print(f"{user.name = }")
    >>>
    >>> # Or with explicit token
    >>> async def main():
    ...     async with Upsales(token="YOUR_TOKEN") as upsales:
    ...         user = await upsales.users.get(1)
    ...         await user.edit(name="New Name")
    >>>
    >>> asyncio.run(main())

Note:
    Built for Python 3.13+ with free-threaded mode support for optimal
    concurrent request performance. Enable with: python -X gil=0 script.py
"""

from typing import Any

from upsales.auth import AuthenticationManager
from upsales.http import HTTPClient


class Upsales:
    """
    Main Upsales API client.

    Provides access to all API resources through resource managers.
    Use as an async context manager to ensure proper cleanup.

    Args:
        token: Upsales API authentication token.
        base_url: Base API URL (default: https://power.upsales.com/api/v2).
        max_concurrent: Maximum concurrent requests (default: 50).

    Attributes:
        http: HTTP client for making API requests.
        activities: Activities resource manager for /activities endpoint.
        activity_list: Activity list resource manager for /search/activitylist endpoint (read-only).
        apikeys: API Keys resource manager for /apiKeys endpoint.
        appointments: Appointments resource manager for /appointments endpoint.
        clientcategories: Client categories resource manager for /clientcategories endpoint.
        companies: Companies resource manager for /accounts endpoint.
        contacts: Contacts resource manager for /contacts endpoint.
        currencies: Currencies resource manager for /currencies endpoint.
        files: Files resource manager for /files endpoint.
        functions: Utility functions resource manager for /function/* endpoints.
        journey_steps: Journey steps resource manager for /journeySteps endpoint.
        mail: Mail resource manager for /mail endpoint.
        mail_templates: Mail templates resource manager for /mail/templates endpoint.
        metadata: Metadata resource manager for /metadata endpoint (read-only).
        opportunity_ai: OpportunityAI resource manager for /opportunityAI endpoint (read-only).
        orders: Orders resource manager for /orders endpoint.
        pricelists: Pricelists resource manager for /pricelists endpoint.
        products: Products resource manager for /products endpoint.
        project_plan_priorities: Project plan priorities resource manager for /projectPlanPriority endpoint.
        project_plan_types: Project plan types resource manager for /projectPlanTypes endpoint.
        projects: Projects resource manager for /projects endpoint.
        roles: Roles resource manager for /roles endpoint.
        sales_coaches: Sales coaches resource manager for /salesCoaches endpoint.
        segments: Segments resource manager for /segments endpoint.
        self: Self resource manager for /self endpoint (read-only).
        standard_integrations: Standard integrations resource manager for /standardIntegration endpoint.
        static_values: Static values resource manager for /staticValues/all endpoint (read-only).
        todo_views: Todo views resource manager for /todoViews endpoint (read-only).
        trigger_attributes: Trigger attributes resource manager for /triggerAttributes endpoint (read-only).
        triggers: Triggers resource manager for /triggers endpoint.
        users: Users resource manager for /users endpoint.
        custom_fields: Custom fields resource manager for /customFields/{entity}.
        order_stages: Order stages resource manager for /orderStages endpoint.

    Example:
        >>> async with Upsales(token="YOUR_TOKEN") as upsales:
        ...     # Access resources
        ...     user = await upsales.users.get(1)
        ...     companies = await upsales.companies.list(limit=50)
        ...
        ...     # Bulk operations with parallel execution
        ...     await upsales.products.bulk_update(
        ...         ids=[1, 2, 3],
        ...         data={"active": 0}
        ...     )

    Note:
        With Python 3.13 free-threaded mode enabled, concurrent operations
        across all resource managers can achieve true parallelism without
        GIL contention:

            python -X gil=0 your_script.py

        This maximizes throughput within the Upsales API rate limits
        (200 requests per 10 seconds per API key).
    """

    def __init__(
        self,
        token: str,
        base_url: str = "https://power.upsales.com/api/v2",
        max_concurrent: int = 50,
        email: str | None = None,
        password: str | None = None,
        enable_fallback_auth: bool = False,
    ) -> None:
        """
        Initialize Upsales API client.

        Args:
            token: Upsales API token.
            base_url: Base API URL.
            max_concurrent: Max concurrent requests.
            email: Email for fallback authentication (optional).
            password: Password for fallback authentication (optional).
            enable_fallback_auth: Enable automatic token refresh (default: False).

        Example:
            >>> # Basic usage
            >>> client = Upsales(token="YOUR_TOKEN")
            >>>
            >>> # With fallback auth for sandbox environments
            >>> client = Upsales(
            ...     token="YOUR_TOKEN",
            ...     email="user@email.com",
            ...     password="password",
            ...     enable_fallback_auth=True
            ... )
        """
        # Create authentication manager if fallback is enabled
        auth_manager = None
        if enable_fallback_auth or (email and password):
            auth_manager = AuthenticationManager(
                token=token,
                email=email,
                password=password,
                enable_fallback=enable_fallback_auth,
                base_url=base_url,
            )

        self.http = HTTPClient(token, base_url, max_concurrent, auth_manager, upsales_client=self)

        # Initialize resource managers
        from upsales.resources.activities import ActivitiesResource
        from upsales.resources.activity_list import ActivityListResource
        from upsales.resources.apikeys import ApikeysResource
        from upsales.resources.appointments import AppointmentsResource
        from upsales.resources.clientcategories import ClientCategoriesResource
        from upsales.resources.companies import CompaniesResource
        from upsales.resources.contacts import ContactsResource
        from upsales.resources.currencies import CurrenciesResource
        from upsales.resources.custom_fields import CustomFieldsResource
        from upsales.resources.files import FilesResource
        from upsales.resources.forms import FormsResource
        from upsales.resources.functions import FunctionsResource
        from upsales.resources.journey_steps import JourneyStepsResource
        from upsales.resources.mail import MailResource
        from upsales.resources.mail_templates import MailTemplatesResource
        from upsales.resources.metadata import MetadataResource
        from upsales.resources.notifications import NotificationsResource
        from upsales.resources.opportunity_ai import OpportunityAIResource
        from upsales.resources.orders import OrdersResource
        from upsales.resources.orderStages import OrderStagesResource
        from upsales.resources.pricelists import PricelistsResource
        from upsales.resources.products import ProductsResource
        from upsales.resources.project_plan_types import ProjectPlanTypesResource
        from upsales.resources.projectplanpriority import ProjectPlanPrioritiesResource
        from upsales.resources.projects import ProjectsResource
        from upsales.resources.roles import RolesResource
        from upsales.resources.sales_coaches import SalesCoachesResource
        from upsales.resources.segments import SegmentsResource
        from upsales.resources.self import SelfResource
        from upsales.resources.standard_integrations import StandardIntegrationsResource
        from upsales.resources.static_values import StaticValuesResource
        from upsales.resources.todoViews import TodoViewsResource
        from upsales.resources.trigger_attributes import TriggerAttributesResource
        from upsales.resources.triggers import TriggersResource
        from upsales.resources.users import UsersResource

        self.activities = ActivitiesResource(self.http)
        self.activity_list = ActivityListResource(self.http)
        self.apikeys = ApikeysResource(self.http)
        self.appointments = AppointmentsResource(self.http)
        self.clientcategories = ClientCategoriesResource(self.http)
        self.companies = CompaniesResource(self.http)
        self.contacts = ContactsResource(self.http)
        self.currencies = CurrenciesResource(self.http)
        self.files = FilesResource(self.http)
        self.forms = FormsResource(self.http)
        self.functions = FunctionsResource(self.http)
        self.journey_steps = JourneyStepsResource(self.http)
        self.mail = MailResource(self.http)
        self.mail_templates = MailTemplatesResource(self.http)
        self.metadata = MetadataResource(self.http)
        self.opportunity_ai = OpportunityAIResource(self.http)
        self.notifications = NotificationsResource(self.http)
        self.orders = OrdersResource(self.http)
        self.pricelists = PricelistsResource(self.http)
        self.products = ProductsResource(self.http)
        self.project_plan_priorities = ProjectPlanPrioritiesResource(self.http)
        self.project_plan_types = ProjectPlanTypesResource(self.http)
        self.projects = ProjectsResource(self.http)
        self.roles = RolesResource(self.http)
        self.sales_coaches = SalesCoachesResource(self.http)
        self.segments = SegmentsResource(self.http)
        self.standard_integrations = StandardIntegrationsResource(self.http)
        self.self = SelfResource(self.http)
        self.static_values = StaticValuesResource(self.http)
        self.todo_views = TodoViewsResource(self.http)
        self.trigger_attributes = TriggerAttributesResource(self.http)
        self.triggers = TriggersResource(self.http)
        self.users = UsersResource(self.http)
        self.custom_fields = CustomFieldsResource(self.http)
        self.order_stages = OrderStagesResource(self.http)

    @classmethod
    def from_env(cls, env_file: str = ".env") -> "Upsales":
        """
        Create client from environment variables with Pydantic validation.

        Loads configuration from .env file using pydantic-settings for type-safe
        validation. Validates required fields, types, and ranges automatically.

        Args:
            env_file: Path to .env file (default: ".env").

        Returns:
            Configured Upsales instance.

        Raises:
            ValidationError: If required settings missing or invalid (from Pydantic).

        Environment Variables:
            UPSALES_TOKEN: API token (required).
            UPSALES_EMAIL: Email for fallback auth (optional, validated).
            UPSALES_PASSWORD: Password for fallback auth (optional).
            UPSALES_ENABLE_FALLBACK_AUTH: Enable fallback (true/false, default: false).
            UPSALES_BASE_URL: Custom base URL (optional, validated as URL).
            UPSALES_MAX_CONCURRENT: Max concurrent requests 1-200 (optional, default: 50).

        Example:
            >>> # .env file:
            >>> # UPSALES_TOKEN=your_token
            >>> # UPSALES_ENABLE_FALLBACK_AUTH=true
            >>> # UPSALES_EMAIL=user@email.com
            >>> # UPSALES_MAX_CONCURRENT=100
            >>>
            >>> async with Upsales.from_env() as upsales:
            ...     user = await upsales.users.get(1)

        Example with Validation:
            >>> # .env file:
            >>> # UPSALES_MAX_CONCURRENT=999  # Invalid!
            >>>
            >>> upsales = Upsales.from_env()
            Traceback (most recent call last):
            ...
            ValidationError: upsales_max_concurrent must be <= 200

        Note:
            Uses pydantic-settings for type-safe configuration. Email addresses
            are validated using the same EmailStr validator as models. Max concurrent
            is validated to be 1-200 to respect API rate limits (200 req/10sec).

            Fallback authentication is useful for sandbox environments that
            reset daily. Set UPSALES_ENABLE_FALLBACK_AUTH=true to enable
            automatic token refresh using username/password when the API
            token expires.
        """
        from upsales.settings import load_settings

        # Load and validate settings using pydantic-settings
        settings = load_settings(env_file)

        return cls(
            token=settings.upsales_token,
            base_url=str(settings.upsales_base_url),
            max_concurrent=settings.upsales_max_concurrent,
            email=settings.upsales_email,
            password=settings.upsales_password,
            enable_fallback_auth=settings.upsales_enable_fallback_auth,
        )

    async def __aenter__(self) -> "Upsales":
        """
        Enter async context manager.

        Returns:
            Self for context manager usage.
        """
        await self.http.__aenter__()
        return self

    async def __aexit__(self, *args: Any) -> None:
        """Exit async context manager and cleanup."""
        await self.http.__aexit__(*args)

    async def close(self) -> None:
        """
        Close the client and cleanup resources.

        Example:
            >>> client = Upsales(token="YOUR_TOKEN")
            >>> await upsales.__aenter__()
            >>> # ... use client ...
            >>> await upsales.close()
        """
        await self.http.close()

    def __repr__(self) -> str:
        """
        Return string representation of the client.

        Returns:
            String like "<Upsales base_url='...' >".
        """
        return f"<Upsales base_url='{self.http.base_url}'>"
