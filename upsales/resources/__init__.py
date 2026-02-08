"""
Resource managers for Upsales API endpoints.

Each resource manager handles CRUD operations for a specific API endpoint.
All use Python 3.13 type parameter syntax for clean generics.

All resource managers inherit standard CRUD from BaseResource:
- get(id) - Get single object
- list(limit, offset, **params) - Paginated list
- list_all(**params) - Auto-paginated list of all objects
- update(id, **data) - Update object
- delete(id) - Delete object
- bulk_update(ids, data, max_concurrent) - Parallel updates
- bulk_delete(ids, max_concurrent) - Parallel deletes

Example:
    >>> from upsales.resources import CompaniesResource, ProductsResource, UsersResource
    >>> from upsales.http import HTTPClient
    >>>
    >>> http = HTTPClient(token="...")
    >>> companies = CompaniesResource(http)
    >>> company = await companies.get(1)
"""

from upsales.resources.activities import ActivitiesResource
from upsales.resources.activity_list import ActivityListResource
from upsales.resources.activity_quota import ActivityQuotaResource
from upsales.resources.activity_types import ActivityTypesResource
from upsales.resources.ad_accounts import AdAccountsResource
from upsales.resources.ad_campaigns import AdCampaignsResource
from upsales.resources.ad_creatives import AdCreativesResource
from upsales.resources.agreement_groups import AgreementGroupsResource
from upsales.resources.agreements import AgreementsResource
from upsales.resources.api_keys import ApikeysResource
from upsales.resources.appointments import AppointmentsResource
from upsales.resources.banner_groups import BannerGroupsResource
from upsales.resources.base import BaseResource
from upsales.resources.bulk import BulkResource
from upsales.resources.client_category_types import ClientCategoryTypesResource
from upsales.resources.client_ip_info import ClientIpInfoResource
from upsales.resources.client_ips import ClientIpsResource
from upsales.resources.client_relations import ClientRelationsResource
from upsales.resources.clientcategories import ClientCategoriesResource
from upsales.resources.companies import CompaniesResource
from upsales.resources.contact_relations import ContactRelationsResource
from upsales.resources.contacts import ContactsResource
from upsales.resources.contract_accepted import ContractAcceptedResource
from upsales.resources.currencies import CurrenciesResource
from upsales.resources.data_source import DataSourceResource
from upsales.resources.engage_credit_transaction import EngageCreditTransactionsResource
from upsales.resources.esign_function import EsignFunctionResource
from upsales.resources.esigns import EsignsResource
from upsales.resources.events import EventsResource
from upsales.resources.file_upload import FileUploadsResource
from upsales.resources.files import FilesResource
from upsales.resources.flows import FlowsResource
from upsales.resources.form_submits import FormSubmitsResource
from upsales.resources.forms import FormsResource
from upsales.resources.functions import FunctionsResource
from upsales.resources.group_mail_categories import GroupMailCategoriesResource
from upsales.resources.image_compose import ImageComposeResource
from upsales.resources.import_mail_campaign_mail import ImportMailCampaignMailResource
from upsales.resources.import_mail_event import ImportMailEventResource
from upsales.resources.journey_steps import JourneyStepsResource
from upsales.resources.lead_channels import LeadChannelsResource
from upsales.resources.lead_sources import LeadSourcesResource
from upsales.resources.leads import LeadsResource
from upsales.resources.list_views import ListViewsResource
from upsales.resources.mail import MailResource
from upsales.resources.mail_campaigns import MailCampaignsResource
from upsales.resources.mail_domains import MailDomainsResource
from upsales.resources.mail_editor import MailEditorResource
from upsales.resources.mail_multi import MailMultiResource
from upsales.resources.mail_templates import MailTemplatesResource
from upsales.resources.mail_test import MailTestResource
from upsales.resources.market_rejectlist import MarketRejectlistsResource
from upsales.resources.metadata import MetadataResource
from upsales.resources.notification_settings import NotificationSettingsResource
from upsales.resources.notifications import NotificationsResource
from upsales.resources.onboarding_imports import OnboardingImportsResource
from upsales.resources.opportunities import OpportunitiesResource
from upsales.resources.opportunity_ai import OpportunityAIResource
from upsales.resources.order_stages import OrderStagesResource
from upsales.resources.orders import OrdersResource
from upsales.resources.pages import PagesResource
from upsales.resources.periodization import PeriodizationsResource
from upsales.resources.phone_calls import PhoneCallsResource
from upsales.resources.pricelists import PricelistsResource
from upsales.resources.product_categories import ProductCategoriesResource
from upsales.resources.products import ProductsResource
from upsales.resources.project_plan_priority import ProjectPlanPrioritiesResource
from upsales.resources.project_plan_stages import ProjectplanstagesResource
from upsales.resources.project_plan_status import ProjectPlanStatusesResource
from upsales.resources.project_plan_types import ProjectPlanTypesResource
from upsales.resources.projects import ProjectsResource
from upsales.resources.provisioning import ProvisioningResource
from upsales.resources.quota import QuotasResource
from upsales.resources.report_view import ReportViewsResource
from upsales.resources.reset_score import ResetScoreResource
from upsales.resources.resources_upload_external import ResourcesUploadExternalResource
from upsales.resources.resources_upload_internal import ResourcesUploadInternalResource
from upsales.resources.roles import RolesResource
from upsales.resources.sales_coaches import SalesCoachesResource
from upsales.resources.salesboard_cards import SalesboardCardsResource
from upsales.resources.segments import SegmentsResource
from upsales.resources.self import SelfResource
from upsales.resources.send_beam import SendBeamResource
from upsales.resources.soliditet_clients import SoliditetClientsResource
from upsales.resources.standard_creative import StandardCreativeResource
from upsales.resources.standard_integration_data import StandardIntegrationDataResource
from upsales.resources.standard_integration_settings import StandardIntegrationSettingsResource
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
from upsales.resources.trigger_attributes import TriggerAttributesResource
from upsales.resources.triggers import TriggersResource
from upsales.resources.unsub import UnsubsResource
from upsales.resources.user_defined_object_1 import UserDefinedObject1Resource
from upsales.resources.user_defined_object_2 import UserDefinedObject2Resource
from upsales.resources.user_defined_object_3 import UserDefinedObject3Resource
from upsales.resources.user_defined_object_4 import UserDefinedObject4Resource
from upsales.resources.user_defined_object_categories import UserDefinedObjectCategoriesResource
from upsales.resources.user_defined_object_definition import UserDefinedObjectDefinitionsResource
from upsales.resources.user_invites import UserInvitesResource
from upsales.resources.users import UsersResource
from upsales.resources.validate_page import ValidatePageResource
from upsales.resources.visits import VisitsResource
from upsales.resources.voice import VoiceResource

__all__ = [
    "BaseResource",
    "ActivitiesResource",
    "AdAccountsResource",
    "AdCampaignsResource",
    "AdCreativesResource",
    "ActivityListResource",
    "ActivityQuotaResource",
    "ActivityTypesResource",
    "ApikeysResource",
    "AppointmentsResource",
    "BannerGroupsResource",
    "BulkResource",
    "ReportViewsResource",
    "ResetScoreResource",
    "NotificationSettingsResource",
    "EsignsResource",
    "EsignFunctionResource",
    "EngageCreditTransactionsResource",
    "SalesboardCardsResource",
    "OnboardingImportsResource",
    "VisitsResource",
    "UserDefinedObject1Resource",
    "UserDefinedObject2Resource",
    "UserDefinedObject3Resource",
    "UserDefinedObject4Resource",
    "UserDefinedObjectCategoriesResource",
    "UserDefinedObjectDefinitionsResource",
    "ClientCategoriesResource",
    "ClientCategoryTypesResource",
    "ClientIpInfoResource",
    "ClientRelationsResource",
    "CompaniesResource",
    "ContactRelationsResource",
    "ContractAcceptedResource",
    "ContactsResource",
    "CurrenciesResource",
    "FilesResource",
    "FileUploadsResource",
    "FlowsResource",
    "FormsResource",
    "FormSubmitsResource",
    "FunctionsResource",
    "JourneyStepsResource",
    "LeadChannelsResource",
    "LeadSourcesResource",
    "LeadsResource",
    "ListViewsResource",
    "MailResource",
    "MailCampaignsResource",
    "MailDomainsResource",
    "MailEditorResource",
    "MailTemplatesResource",
    "NotificationsResource",
    "MetadataResource",
    "OpportunitiesResource",
    "OpportunityAIResource",
    "OrdersResource",
    "OrderStagesResource",
    "PeriodizationsResource",
    "PhoneCallsResource",
    "PricelistsResource",
    "ProductCategoriesResource",
    "ProductsResource",
    "ProjectPlanPrioritiesResource",
    "ProjectplanstagesResource",
    "ProjectPlanStatusesResource",
    "ProjectPlanTypesResource",
    "ProjectsResource",
    "RolesResource",
    "SalesCoachesResource",
    "SegmentsResource",
    "StandardCreativeResource",
    "StandardIntegrationsResource",
    "StandardIntegrationSettingsResource",
    "StandardIntegrationUserSettingsResource",
    "SelfResource",
    "StaticValuesResource",
    "TicketStatusesResource",
    "TicketTypesResource",
    "TodoViewsResource",
    "TriggerAttributesResource",
    "TriggersResource",
    "UserInvitesResource",
    "UsersResource",
    "QuotasResource",
    "GroupMailCategoriesResource",
    "ImportMailEventResource",
    "ImportMailCampaignMailResource",
    "AgreementsResource",
    "AgreementGroupsResource",
    "EventsResource",
    "TicketsResource",
    "ProvisioningResource",
    "ClientIpsResource",
    "ResourcesUploadExternalResource",
    "ResourcesUploadInternalResource",
    "DataSourceResource",
    "ImageComposeResource",
    "SoliditetClientsResource",
    "MarketRejectlistsResource",
    "SuggestionsResource",
    "ValidatePageResource",
    "StandardIntegrationDataResource",
    "SendBeamResource",
    "VoiceResource",
    "SystemMailResource",
    "MailTestResource",
    "MailMultiResource",
    "PagesResource",
    "UnsubsResource",
]
