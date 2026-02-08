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
    Built for Python 3.13+ with modern async patterns for efficient
    concurrent request handling.
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
        agreement_groups: Agreement groups resource manager for /agreementGroups endpoint.
        activity_types: Activity types resource manager for /activitytypes/activity endpoint.
        ad_accounts: Ad accounts resource manager for /:customerId/engage/account endpoint.
        ad_campaigns: Ad campaigns resource manager for /api/v2/:customerId/engage/campaign endpoint.
        ad_creatives: Ad creatives resource manager for /api/v2/:customerId/engage/creative endpoint.
        activity_quota: Activity quota resource manager for /activityQuota endpoint.
        apikeys: API Keys resource manager for /apiKeys endpoint.
        appointments: Appointments resource manager for /appointments endpoint.
        bulk: Bulk prospecting save resource manager for /prospectingbulk endpoint (POST-only).
        client_categories: Client categories resource manager for /client_categories endpoint.
        client_category_types: Client category types resource manager for /clientCategoryTypes endpoint.
        client_ip_info: Client IP info resource manager for /function/clientIpInfo endpoint (POST-only).
        client_ips: Client IP whitelist resource manager for /clientIps endpoint.
        client_relations: Client relations resource manager for /clientrelations endpoint.
        companies: Companies resource manager for /accounts endpoint.
        contact_relations: Contact relations resource manager for /contactrelation endpoint.
        contract_accepted: Contract accepted resource manager for /contractAccepted endpoint.
        contacts: Contacts resource manager for /contacts endpoint.
        currencies: Currencies resource manager for /currencies endpoint.
        data_source: Data source resource manager for /function/datasource endpoint (function-based).
        esign_function: E-signature function resource manager for /function/esign endpoint (settings and download).
        engage_credit_transactions: Engage credit transactions resource manager for /engage/creditTransaction endpoint.
        events: Events resource manager for /events endpoint.
        files: Files resource manager for /files endpoint.
        file_uploads: File uploads resource manager for /file/upload endpoint.
        flows: Flows resource manager for /flows endpoint.
        form_submits: Form submissions resource manager for /formSubmits endpoint (requires admin or mailAdmin).
        functions: Utility functions resource manager for /function/* endpoints.
        group_mail_categories: Group mail categories resource manager for /groupMailCategories endpoint.
        image_compose: Image composition resource manager for /image/compose endpoint (POST-only).
        import_mail_event: Mail event import resource manager for /import/mailevent endpoint (POST-only).
        import_mail_campaign_mail: Mail campaign mail import resource manager for /import/mailcampaign/mail endpoint (POST-only).
        journey_steps: Journey steps resource manager for /journeySteps endpoint.
        leads: Leads resource manager for /leads endpoint.
        list_views: List views resource manager for /listViews/:entity endpoint.
        mail: Mail resource manager for /mail endpoint.
        mail_multi: Batch email sending resource manager for /mail/multi endpoint (POST-only).
        mail_campaigns: Mail campaigns resource manager for /mailCampaigns endpoint.
        mail_templates: Mail templates resource manager for /mail/templates endpoint.
        mail_domains: Mail domains resource manager for /mail/domains endpoint.
        mail_test: Mail test resource manager for /mail/test endpoint (POST-only, send test emails).
        market_rejectlist: Market rejectlist resource manager for /marketRejectlist endpoint.
        metadata: Metadata resource manager for /metadata endpoint (read-only).
        opportunities: Opportunities resource manager for /opportunities endpoint.
        opportunity_ai: OpportunityAI resource manager for /opportunityAI endpoint (read-only).
        orders: Orders resource manager for /orders endpoint.
        pages: Pages resource manager for /pages endpoint.
        periodization: Periodization resource manager for /periodization endpoint.
        phone_calls: Phone calls resource manager for /phoneCall endpoint.
        pricelists: Pricelists resource manager for /pricelists endpoint.
        product_categories: Product categories resource manager for /productCategories endpoint.
        products: Products resource manager for /products endpoint.
        project_plan_priorities: Project plan priorities resource manager for /projectPlanPriority endpoint.
        project_plan_stages: Project plan stages resource manager for /projectPlanStages endpoint.
        project_plan_statuses: Project plan statuses resource manager for /ProjectPlanStatus endpoint.
        project_plan_types: Project plan types resource manager for /projectPlanTypes endpoint.
        projects: Projects resource manager for /projects endpoint.
        resources_upload_external: External resource upload manager for /resources/upload/external endpoint.
        resources_upload_internal: Internal resource upload manager for /resources/upload/internal endpoint.
        roles: Roles resource manager for /roles endpoint.
        sales_coaches: Sales coaches resource manager for /salesCoaches endpoint.
        segments: Segments resource manager for /segments endpoint.
        soliditet_clients: Soliditet clients resource manager for /soliditet/clients endpoint.
        self: Self resource manager for /self endpoint (read-only).
        standard_creative: Standard creative resource manager for /standardCreative endpoint (read-only).
        standard_integrations: Standard integrations resource manager for /standardIntegration endpoint.
        standard_integration_settings: Standard integration settings resource manager for /standardIntegrationSettings endpoint.
        standard_integration_user_settings: Standard integration user settings resource manager for /standardIntegrationUserSettings endpoint.
        standard_integration_data: Standard integration data function endpoint for operations (test, values, config, OAuth, events).
        static_values: Static values resource manager for /staticValues/all endpoint (read-only).
        suggestions: Suggestions resource manager for /prospectingsuggestion endpoint.
        ticket_statuses: Ticket statuses resource manager for /ticketStatus endpoint.
        ticket_types: Ticket types resource manager for /ticketType endpoint.
        tickets: Tickets resource manager for /tickets endpoint.
        todo_views: Todo views resource manager for /todoViews endpoint (read-only).
        trigger_attributes: Trigger attributes resource manager for /triggerAttributes endpoint (read-only).
        triggers: Triggers resource manager for /triggers endpoint.
        user_invites: User invites resource manager for /userInvites endpoint.
        users: Users resource manager for /users endpoint.
        custom_fields: Custom fields resource manager for /customFields/{entity}.
        order_stages: Order stages resource manager for /orderStages endpoint.
        quota: Quotas resource manager for /quota endpoint.
        voice: Voice/phone integration resource manager for /function/voice endpoint.
        system_mail: System mail resource manager for /function/system-mail endpoint (POST-only).

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
        Uses asyncio for efficient concurrent operations across all resource
        managers, maximizing throughput within the Upsales API rate limits
        (200 requests per 10 seconds per API key).

        The bottleneck for bulk operations is typically network I/O and
        API rate limits, not CPU or the GIL.
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
        from upsales.resources.account_manager_history import (
            AccountManagerHistoryResource,
        )
        from upsales.resources.activities import ActivitiesResource
        from upsales.resources.activity_list import ActivityListResource
        from upsales.resources.activity_quota import ActivityQuotaResource
        from upsales.resources.activity_types import ActivityTypesResource
        from upsales.resources.ad_accounts import AdAccountsResource
        from upsales.resources.ad_campaigns import AdCampaignsResource
        from upsales.resources.ad_creatives import AdCreativesResource
        from upsales.resources.ad_credits import AdCreditsResource
        from upsales.resources.ad_locations import AdLocationsResource
        from upsales.resources.agreement_groups import AgreementGroupsResource
        from upsales.resources.agreements import AgreementsResource
        from upsales.resources.api_keys import ApikeysResource
        from upsales.resources.appointments import AppointmentsResource
        from upsales.resources.assign import AssignResource
        from upsales.resources.banner_groups import BannerGroupsResource
        from upsales.resources.bulk import BulkResource
        from upsales.resources.cancel_esign import CancelEsignResource
        from upsales.resources.client_category_types import ClientCategoryTypesResource
        from upsales.resources.client_form import ClientFormResource
        from upsales.resources.client_ip_info import ClientIpInfoResource
        from upsales.resources.client_ips import ClientIpsResource
        from upsales.resources.client_relations import ClientRelationsResource
        from upsales.resources.clientcategories import ClientCategoriesResource
        from upsales.resources.companies import CompaniesResource
        from upsales.resources.contact_relations import ContactRelationsResource
        from upsales.resources.contacts import ContactsResource
        from upsales.resources.contract import ContractsResource
        from upsales.resources.contract_accepted import ContractAcceptedResource
        from upsales.resources.currencies import CurrenciesResource
        from upsales.resources.custom_fields import CustomFieldsResource
        from upsales.resources.customfields_accounts import CustomfieldsAccountsResource
        from upsales.resources.data_source import DataSourceResource
        from upsales.resources.delete_log import DeleteLogResource
        from upsales.resources.docebo_sso import DoceboSSOResource
        from upsales.resources.email_duplicates import EmailDuplicatesResource
        from upsales.resources.email_suggest import EmailSuggestResource
        from upsales.resources.email_suggestion import EmailSuggestionResource
        from upsales.resources.engage_credit_transaction import EngageCreditTransactionsResource
        from upsales.resources.engage_site_template import EngageSiteTemplateResource
        from upsales.resources.esign_function import EsignFunctionResource
        from upsales.resources.esigns import EsignsResource
        from upsales.resources.events import EventsResource
        from upsales.resources.events_prior import EventsPriorResource
        from upsales.resources.export import ExportResource
        from upsales.resources.file_download import FileDownloadResource
        from upsales.resources.file_upload import FileUploadsResource
        from upsales.resources.files import FilesResource
        from upsales.resources.find_prospect import FindProspectResource
        from upsales.resources.flow_contacts import FlowContactsResource
        from upsales.resources.flows import FlowsResource
        from upsales.resources.form_submits import FormSubmitsResource
        from upsales.resources.forms import FormsResource
        from upsales.resources.forms_external_lead_source import FormsExternalLeadSourceResource
        from upsales.resources.functions import FunctionsResource
        from upsales.resources.group_mail_categories import GroupMailCategoriesResource
        from upsales.resources.group_structure import GroupStructureResource
        from upsales.resources.image_compose import ImageComposeResource
        from upsales.resources.import_mail_campaign import ImportMailCampaignResource
        from upsales.resources.import_mail_campaign_mail import ImportMailCampaignMailResource
        from upsales.resources.import_mail_event import ImportMailEventResource
        from upsales.resources.industries import IndustriesResource
        from upsales.resources.integration_log import IntegrationLogResource
        from upsales.resources.journey_step_history import JourneyStepHistoryResource
        from upsales.resources.journey_steps import JourneyStepsResource
        from upsales.resources.landing_page_template import LandingPageTemplateResource
        from upsales.resources.lead_channels import LeadChannelsResource
        from upsales.resources.lead_sources import LeadSourcesResource
        from upsales.resources.lead_sources2 import LeadSources2Resource
        from upsales.resources.leads import LeadsResource
        from upsales.resources.leads2 import Leads2Resource
        from upsales.resources.links import LinksResource
        from upsales.resources.list_views import ListViewsResource
        from upsales.resources.looker_explores import LookerExploresResource
        from upsales.resources.looker_looks import LookerLooksResource
        from upsales.resources.looker_sso import LookerSSOResource
        from upsales.resources.lookup import LookupResource
        from upsales.resources.mail import MailResource
        from upsales.resources.mail_by_thread import MailByThreadResource
        from upsales.resources.mail_campaign_info import MailCampaignInfoResource
        from upsales.resources.mail_campaigns import MailCampaignsResource
        from upsales.resources.mail_domains import MailDomainsResource
        from upsales.resources.mail_editor import MailEditorResource
        from upsales.resources.mail_multi import MailMultiResource
        from upsales.resources.mail_templates import MailTemplatesResource
        from upsales.resources.mail_templates_recently_used import MailTemplatesRecentlyUsedResource
        from upsales.resources.mail_templates_used_in import MailTemplatesUsedInResource
        from upsales.resources.mail_test import MailTestResource
        from upsales.resources.market_rejectlist import MarketRejectlistsResource
        from upsales.resources.metadata import MetadataResource
        from upsales.resources.notification_settings import NotificationSettingsResource
        from upsales.resources.notifications import NotificationsResource
        from upsales.resources.notify import NotifyResource
        from upsales.resources.onboarding_imports import OnboardingImportsResource
        from upsales.resources.opportunities import OpportunitiesResource
        from upsales.resources.opportunity_ai import OpportunityAIResource
        from upsales.resources.order_stages import OrderStagesResource
        from upsales.resources.orders import OrdersResource
        from upsales.resources.pages import PagesResource
        from upsales.resources.periodization import PeriodizationsResource
        from upsales.resources.phone_calls import PhoneCallsResource
        from upsales.resources.placeholder import PlaceholderResource
        from upsales.resources.pricelists import PricelistsResource
        from upsales.resources.product_categories import ProductCategoriesResource
        from upsales.resources.products import ProductsResource
        from upsales.resources.project_plan_priority import ProjectPlanPrioritiesResource
        from upsales.resources.project_plan_stages import ProjectplanstagesResource
        from upsales.resources.project_plan_status import ProjectPlanStatusesResource
        from upsales.resources.project_plan_types import ProjectPlanTypesResource
        from upsales.resources.projects import ProjectsResource
        from upsales.resources.provisioning import ProvisioningResource
        from upsales.resources.quick_search import QuickSearchResource
        from upsales.resources.quota import QuotasResource
        from upsales.resources.report import ReportResource
        from upsales.resources.report_client_company_type import ReportClientCompanyTypeResource
        from upsales.resources.report_view import ReportViewsResource
        from upsales.resources.report_widget import ReportWidgetResource
        from upsales.resources.report_widget_metadata import ReportWidgetMetadataResource
        from upsales.resources.reset_score import ResetScoreResource
        from upsales.resources.resources_download_adgear import ResourcesDownloadAdgearResource
        from upsales.resources.resources_download_internal import ResourcesDownloadInternalResource
        from upsales.resources.resources_upload_external import ResourcesUploadExternalResource
        from upsales.resources.resources_upload_internal import ResourcesUploadInternalResource
        from upsales.resources.role_settings import RoleSettingsResource
        from upsales.resources.roles import RolesResource
        from upsales.resources.sales_coaches import SalesCoachesResource
        from upsales.resources.salesboard_cards import SalesboardCardsResource
        from upsales.resources.scoreboard import ScoreboardResource
        from upsales.resources.segments import SegmentsResource
        from upsales.resources.self import SelfResource
        from upsales.resources.send_beam import SendBeamResource
        from upsales.resources.send_esign_reminder import SendEsignReminderResource
        from upsales.resources.signals_feed import SignalsFeedResource
        from upsales.resources.soliditet_clients import SoliditetClientsResource
        from upsales.resources.soliditet_matcher import SoliditetMatcherResource
        from upsales.resources.soliditet_search import SoliditetSearchResource
        from upsales.resources.soliditet_search_buy import SoliditetSearchBuyResource
        from upsales.resources.standard_creative import StandardCreativeResource
        from upsales.resources.standard_field import StandardFieldsResource
        from upsales.resources.standard_integration_data import (
            StandardIntegrationDataResource,
        )
        from upsales.resources.standard_integration_settings import (
            StandardIntegrationSettingsResource,
        )
        from upsales.resources.standard_integration_user import StandardIntegrationUserResource
        from upsales.resources.standard_integration_user_settings import (
            StandardIntegrationUserSettingsResource,
        )
        from upsales.resources.standard_integrations import StandardIntegrationsResource
        from upsales.resources.static_values import StaticValuesResource
        from upsales.resources.suggestions import SuggestionsResource
        from upsales.resources.system_mail import SystemMailResource
        from upsales.resources.ticket_statuses import TicketStatusesResource
        from upsales.resources.ticket_types import TicketTypesResource
        from upsales.resources.tickets import TicketsResource
        from upsales.resources.todo_views import TodoViewsResource
        from upsales.resources.translate_tags import TranslateTagsResource
        from upsales.resources.trigger_attributes import TriggerAttributesResource
        from upsales.resources.triggers import TriggersResource
        from upsales.resources.unread_notifications import UnreadNotificationsResource
        from upsales.resources.unsub import UnsubsResource
        from upsales.resources.user_defined_object_1 import UserDefinedObject1Resource
        from upsales.resources.user_defined_object_2 import UserDefinedObject2Resource
        from upsales.resources.user_defined_object_3 import UserDefinedObject3Resource
        from upsales.resources.user_defined_object_4 import UserDefinedObject4Resource
        from upsales.resources.user_defined_object_categories import (
            UserDefinedObjectCategoriesResource,
        )
        from upsales.resources.user_defined_object_definition import (
            UserDefinedObjectDefinitionsResource,
        )
        from upsales.resources.user_invites import UserInvitesResource
        from upsales.resources.users import UsersResource
        from upsales.resources.validate_page import ValidatePageResource
        from upsales.resources.visits import VisitsResource
        from upsales.resources.voice import VoiceResource
        from upsales.resources.what_is_my_ip import WhatIsMyIpResource
        from upsales.resources.worker_status import WorkerStatusResource

        self.activities = ActivitiesResource(self.http)
        self.activity_list = ActivityListResource(self.http)
        self.activity_types = ActivityTypesResource(self.http)
        self.activity_quota = ActivityQuotaResource(self.http)
        self.ad_accounts = AdAccountsResource(self.http)
        self.ad_campaigns = AdCampaignsResource(self.http)
        self.ad_creatives = AdCreativesResource(self.http)
        self.agreement_groups = AgreementGroupsResource(self.http)
        self.agreements = AgreementsResource(self.http)
        self.apikeys = ApikeysResource(self.http)
        self.appointments = AppointmentsResource(self.http)
        self.banner_groups = BannerGroupsResource(self.http)
        self.resources_upload_internal = ResourcesUploadInternalResource(self.http)
        self.bulk = BulkResource(self.http)
        self.report_views = ReportViewsResource(self.http)
        self.reset_score = ResetScoreResource(self.http)
        self.resources_upload_external = ResourcesUploadExternalResource(self.http)
        self.notification_settings = NotificationSettingsResource(self.http)
        self.esigns = EsignsResource(self.http)
        self.esign_function = EsignFunctionResource(self.http)
        self.engage_credit_transactions = EngageCreditTransactionsResource(self.http)
        self.salesboard_cards = SalesboardCardsResource(self.http)
        self.onboarding_imports = OnboardingImportsResource(self.http)
        self.visits = VisitsResource(self.http)
        self.user_defined_object_1 = UserDefinedObject1Resource(self.http)
        self.user_defined_object_2 = UserDefinedObject2Resource(self.http)
        self.user_defined_object_3 = UserDefinedObject3Resource(self.http)
        self.user_defined_object_4 = UserDefinedObject4Resource(self.http)
        self.user_defined_object_categories = UserDefinedObjectCategoriesResource(self.http)
        self.user_defined_object_definitions = UserDefinedObjectDefinitionsResource(self.http)
        self.client_categories = ClientCategoriesResource(self.http)
        self.client_category_types = ClientCategoryTypesResource(self.http)
        self.client_ip_info = ClientIpInfoResource(self.http)
        self.client_ips = ClientIpsResource(self.http)
        self.client_relations = ClientRelationsResource(self.http)
        self.companies = CompaniesResource(self.http)
        self.contact_relations = ContactRelationsResource(self.http)
        self.contract_accepted = ContractAcceptedResource(self.http)
        self.contacts = ContactsResource(self.http)
        self.currencies = CurrenciesResource(self.http)
        self.data_source = DataSourceResource(self.http)
        self.events = EventsResource(self.http)
        self.files = FilesResource(self.http)
        self.file_uploads = FileUploadsResource(self.http)
        self.form_submits = FormSubmitsResource(self.http)
        self.flows = FlowsResource(self.http)
        self.forms = FormsResource(self.http)
        self.functions = FunctionsResource(self.http)
        self.group_mail_categories = GroupMailCategoriesResource(self.http)
        self.import_mail_campaign_mail = ImportMailCampaignMailResource(self.http)
        self.import_mail_event = ImportMailEventResource(self.http)
        self.list_views = ListViewsResource(self.http)
        self.journey_steps = JourneyStepsResource(self.http)
        self.lead_channels = LeadChannelsResource(self.http)
        self.lead_sources = LeadSourcesResource(self.http)
        self.leads = LeadsResource(self.http)
        self.mail = MailResource(self.http)
        self.mail_multi = MailMultiResource(self.http)
        self.mail_campaigns = MailCampaignsResource(self.http)
        self.mail_templates = MailTemplatesResource(self.http)
        self.mail_domains = MailDomainsResource(self.http)
        self.mail_editor = MailEditorResource(self.http)
        self.mail_test = MailTestResource(self.http)
        self.market_rejectlist = MarketRejectlistsResource(self.http)
        self.metadata = MetadataResource(self.http)
        self.opportunities = OpportunitiesResource(self.http)
        self.opportunity_ai = OpportunityAIResource(self.http)
        self.notifications = NotificationsResource(self.http)
        self.notify = NotifyResource(self.http)
        self.orders = OrdersResource(self.http)
        self.pages = PagesResource(self.http)
        self.periodization = PeriodizationsResource(self.http)
        self.phone_calls = PhoneCallsResource(self.http)
        self.pricelists = PricelistsResource(self.http)
        self.product_categories = ProductCategoriesResource(self.http)
        self.products = ProductsResource(self.http)
        self.project_plan_priorities = ProjectPlanPrioritiesResource(self.http)
        self.project_plan_stages = ProjectplanstagesResource(self.http)
        self.project_plan_statuses = ProjectPlanStatusesResource(self.http)
        self.project_plan_types = ProjectPlanTypesResource(self.http)
        self.projects = ProjectsResource(self.http)
        self.roles = RolesResource(self.http)
        self.sales_coaches = SalesCoachesResource(self.http)
        self.segments = SegmentsResource(self.http)
        self.send_beam = SendBeamResource(self.http)
        self.soliditet_clients = SoliditetClientsResource(self.http)
        self.standard_creative = StandardCreativeResource(self.http)
        self.standard_integrations = StandardIntegrationsResource(self.http)
        self.standard_integration_data = StandardIntegrationDataResource(self.http)
        self.standard_integration_settings = StandardIntegrationSettingsResource(self.http)
        self.standard_integration_user_settings = StandardIntegrationUserSettingsResource(self.http)
        self.self = SelfResource(self.http)
        self.static_values = StaticValuesResource(self.http)
        self.suggestions = SuggestionsResource(self.http)
        self.provisioning = ProvisioningResource(self.http)
        self.ticket_statuses = TicketStatusesResource(self.http)
        self.ticket_types = TicketTypesResource(self.http)
        self.tickets = TicketsResource(self.http)
        self.todo_views = TodoViewsResource(self.http)
        self.trigger_attributes = TriggerAttributesResource(self.http)
        self.triggers = TriggersResource(self.http)
        self.unsub = UnsubsResource(self.http)
        self.user_invites = UserInvitesResource(self.http)
        self.users = UsersResource(self.http)
        self.custom_fields = CustomFieldsResource(self.http)
        self.order_stages = OrderStagesResource(self.http)
        self.quota = QuotasResource(self.http)
        self.image_compose = ImageComposeResource(self.http)
        self.voice = VoiceResource(self.http)
        self.validate_page = ValidatePageResource(self.http)
        self.system_mail = SystemMailResource(self.http)
        self.assign = AssignResource(self.http)
        self.account_manager_history = AccountManagerHistoryResource(self.http)
        self.cancel_esign = CancelEsignResource(self.http)
        self.send_esign_reminder = SendEsignReminderResource(self.http)
        self.contracts = ContractsResource(self.http)
        self.customfields_accounts = CustomfieldsAccountsResource(self.http)
        self.export = ExportResource(self.http)
        self.import_mail_campaign = ImportMailCampaignResource(self.http)
        self.integration_log = IntegrationLogResource(self.http)
        self.soliditet_matcher = SoliditetMatcherResource(self.http)
        self.soliditet_search_buy = SoliditetSearchBuyResource(self.http)
        self.standard_fields = StandardFieldsResource(self.http)
        self.translate_tags = TranslateTagsResource(self.http)
        self.quick_search = QuickSearchResource(self.http)
        self.lookup = LookupResource(self.http)
        self.find_prospect = FindProspectResource(self.http)
        self.email_duplicates = EmailDuplicatesResource(self.http)
        self.email_suggest = EmailSuggestResource(self.http)
        self.email_suggestion = EmailSuggestionResource(self.http)
        self.report = ReportResource(self.http)
        self.report_widget = ReportWidgetResource(self.http)
        self.report_widget_metadata = ReportWidgetMetadataResource(self.http)
        self.report_client_company_type = ReportClientCompanyTypeResource(self.http)
        self.scoreboard = ScoreboardResource(self.http)
        self.mail_by_thread = MailByThreadResource(self.http)
        self.mail_campaign_info = MailCampaignInfoResource(self.http)
        self.mail_templates_recently_used = MailTemplatesRecentlyUsedResource(self.http)
        self.mail_templates_used_in = MailTemplatesUsedInResource(self.http)
        self.leads2 = Leads2Resource(self.http)
        self.lead_sources2 = LeadSources2Resource(self.http)
        self.looker_sso = LookerSSOResource(self.http)
        self.looker_explores = LookerExploresResource(self.http)
        self.looker_looks = LookerLooksResource(self.http)
        self.docebo_sso = DoceboSSOResource(self.http)
        self.standard_integration_user = StandardIntegrationUserResource(self.http)
        self.unread_notifications = UnreadNotificationsResource(self.http)
        self.signals_feed = SignalsFeedResource(self.http)
        self.ad_credits = AdCreditsResource(self.http)
        self.ad_locations = AdLocationsResource(self.http)
        self.file_download = FileDownloadResource(self.http)
        self.resources_download_adgear = ResourcesDownloadAdgearResource(self.http)
        self.resources_download_internal = ResourcesDownloadInternalResource(self.http)
        self.client_form = ClientFormResource(self.http)
        self.forms_external_lead_source = FormsExternalLeadSourceResource(self.http)
        self.landing_page_templates = LandingPageTemplateResource(self.http)
        self.engage_site_templates = EngageSiteTemplateResource(self.http)
        self.flow_contacts = FlowContactsResource(self.http)
        self.journey_step_history = JourneyStepHistoryResource(self.http)
        self.soliditet_search = SoliditetSearchResource(self.http)
        self.delete_log = DeleteLogResource(self.http)
        self.events_prior = EventsPriorResource(self.http)
        self.group_structure = GroupStructureResource(self.http)
        self.industries = IndustriesResource(self.http)
        self.links = LinksResource(self.http)
        self.placeholder = PlaceholderResource(self.http)
        self.role_settings = RoleSettingsResource(self.http)
        self.what_is_my_ip = WhatIsMyIpResource(self.http)
        self.worker_status = WorkerStatusResource(self.http)
        from upsales.resources.mail_bounce import MailBounceResource
        from upsales.resources.social_events_default_templates import (
            SocialEventsDefaultTemplatesResource,
        )
        from upsales.resources.user_defined_object_category_types import (
            UserDefinedObjectCategoryTypesResource,
        )

        self.mail_bounce = MailBounceResource(self.http)
        self.social_events_default_templates = SocialEventsDefaultTemplatesResource(self.http)
        self.user_defined_object_category_types = UserDefinedObjectCategoryTypesResource(self.http)
        from upsales.resources.contact_categories import ContactCategoriesResource
        from upsales.resources.contact_category_types import ContactCategoryTypesResource

        self.contact_categories = ContactCategoriesResource(self.http)
        self.contact_category_types = ContactCategoryTypesResource(self.http)

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
