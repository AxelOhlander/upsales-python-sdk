"""
Data models for Upsales API objects.

All models use Python 3.13 native type hints and Pydantic v2 advanced features:
- Reusable validators for consistent validation
- Computed fields for derived properties
- Optimized serialization (5-50x faster)
- Field descriptions for documentation
- TypedDict for IDE autocomplete

Example:
    >>> from upsales.models import User, Company, Product
    >>>
    >>> # Models validate on creation and assignment
    >>> user = User(id=1, name="John", email="john@example.com", active=1)
    >>> user.name = "Jane"  # Validated assignment
    >>>
    >>> # Computed fields provide convenience
    >>> user.is_admin  # Boolean helper
    >>> user.custom_fields[11]  # Dict-like custom fields access
"""

from upsales.models.activities import Activity, ActivityUpdateFields, PartialActivity
from upsales.models.activity_list_item import ActivityListItem
from upsales.models.activity_quota import (
    ActivityQuota,
    ActivityQuotaUpdateFields,
    PartialActivityQuota,
)
from upsales.models.activity_types import (
    ActivityType,
    ActivityTypeUpdateFields,
    PartialActivityType,
)
from upsales.models.ad_accounts import AdAccount, PartialAdAccount
from upsales.models.ad_campaign import AdCampaign as NestedAdCampaign
from upsales.models.ad_campaign import PartialAdCampaign as PartialNestedAdCampaign
from upsales.models.ad_campaigns import (
    AdCampaign,
    AdCampaignUpdateFields,
    PartialAdCampaign,
)
from upsales.models.ad_creatives import (
    AdCreative,
    PartialAdCreative,
)
from upsales.models.address import Address, PartialAddress
from upsales.models.address_list import AddressList
from upsales.models.address_types import VALID_ADDRESS_TYPES, AddressType
from upsales.models.agreement_groups import (
    AgreementGroup,
    AgreementGroupUpdateFields,
    PartialAgreementGroup,
)
from upsales.models.agreements import Agreement, AgreementUpdateFields, PartialAgreement
from upsales.models.api_keys import ApiKey, ApiKeyUpdateFields, PartialApiKey
from upsales.models.appointments import Appointment, AppointmentUpdateFields, PartialAppointment
from upsales.models.assignment import Assignment, PartialAssignment
from upsales.models.banner_groups import BannerGroup, PartialBannerGroup
from upsales.models.base import BaseModel, PartialModel
from upsales.models.bulk import (
    BulkSaveFields,
    BulkSaveRequest,
    BulkSaveResponse,
    PartialBulkSaveRequest,
)
from upsales.models.bundled_product import (
    BundledProduct,
    BundledProductUpdateFields,
    PartialBundledProduct,
)
from upsales.models.campaign import PartialCampaign
from upsales.models.category import PartialCategory
from upsales.models.client_categories import (
    ClientCategory,
    ClientCategoryUpdateFields,
    PartialClientCategory,
)
from upsales.models.client_category_types import (
    ClientCategoryType,
    ClientCategoryTypeUpdateFields,
    PartialClientCategoryType,
)
from upsales.models.client_ip_info import ClientIpInfo
from upsales.models.client_ips import ClientIp, ClientIpUpdateFields, PartialClientIp
from upsales.models.client_relations import (
    ClientRelation,
    ClientRelationUpdateFields,
    PartialClientRelation,
)
from upsales.models.company import Company, PartialCompany
from upsales.models.contact_relations import (
    ContactRelation,
    ContactRelationUpdateFields,
    PartialContactRelation,
)
from upsales.models.contacts import (
    Contact,
    ContactCreateFields,
    ContactUpdateFields,
    PartialContact,
)
from upsales.models.contract_accepted import (
    ContractAccepted,
    ContractAcceptedUpdateFields,
    PartialContractAccepted,
)
from upsales.models.currency import Currency, CurrencyUpdateFields, PartialCurrency
from upsales.models.currency_configuration import (
    CurrencyConfiguration,
    PartialCurrencyConfiguration,
)
from upsales.models.custom_field import (
    CustomField,
    CustomFieldType,
    PartialCustomField,
)
from upsales.models.custom_fields import CustomFields
from upsales.models.data_source import (
    DataSourceRequest,
    DataSourceResponse,
    PartialDataSourceResponse,
)
from upsales.models.engage_credit_transaction import (
    EngageCreditTransaction,
    PartialEngageCreditTransaction,
)
from upsales.models.esign_function import (
    EsignFunctionSettings,
    EsignFunctionSettingsFields,
)
from upsales.models.esigns import Esign, PartialEsign
from upsales.models.events import Event, EventCreateFields, EventUpdateFields, PartialEvent
from upsales.models.file_upload import FileUpload, FileUploadUpdateFields, PartialFileUpload
from upsales.models.files import File, FileUpdateFields, PartialFile
from upsales.models.flows import Flow, FlowUpdateFields, PartialFlow
from upsales.models.form_action import FormAction, FormActionProperty, PartialFormAction
from upsales.models.form_element import (
    FormElement,
    FormElementUpdateFields,
    PartialFormElement,
)
from upsales.models.form_field import FormField, PartialFormField
from upsales.models.form_submits import (
    FormSubmit,
    FormSubmitUpdateFields,
    PartialFormSubmit,
)
from upsales.models.forms import Form, FormUpdateFields, PartialForm
from upsales.models.group_mail_categories import (
    GroupMailCategory,
    GroupMailCategoryUpdateFields,
    PartialGroupMailCategory,
)
from upsales.models.image_compose import ImageComposeCreateFields, ImageComposeResponse
from upsales.models.import_mail_campaign_mail import (
    ImportMailCampaignMailRequest,
    ImportMailCampaignMailResponse,
)
from upsales.models.import_mail_event import (
    ImportMailEventResponse,
    MailEvent,
    MailEventType,
    SkippedEvent,
)
from upsales.models.journey_step import JourneyStep, JourneyStepUpdateFields, PartialJourneyStep
from upsales.models.lead_channels import LeadChannel, PartialLeadChannel
from upsales.models.lead_sources import LeadSource, PartialLeadSource
from upsales.models.leads import Lead, LeadUpdateFields, PartialLead
from upsales.models.list_views import ListView, ListViewUpdateFields, PartialListView
from upsales.models.mail import Mail, MailUpdateFields, PartialMail
from upsales.models.mail_campaigns import (
    MailCampaign,
    MailCampaignUpdateFields,
    PartialMailCampaign,
)
from upsales.models.mail_domains import MailDomain, PartialMailDomain
from upsales.models.mail_editor import MailEditorToken
from upsales.models.mail_multi import MailMultiItem, MailMultiRequest, MailMultiResponse
from upsales.models.mail_templates import (
    MailTemplate,
    MailTemplateUpdateFields,
    PartialMailTemplate,
)
from upsales.models.mail_test import MailTestResponse, MailTestSendFields
from upsales.models.market_rejectlist import (
    MarketRejectlist,
    MarketRejectlistUpdateFields,
    PartialMarketRejectlist,
)
from upsales.models.metadata import Currency as MetadataCurrency
from upsales.models.metadata import FieldDefinition, Metadata, MetadataUser, SystemParams
from upsales.models.notification_settings import NotificationSetting, PartialNotificationSetting
from upsales.models.notifications import (
    Notification,
    PartialNotification,
)
from upsales.models.notify import NotifyRequest
from upsales.models.onboarding_imports import OnboardingImport, PartialOnboardingImport
from upsales.models.opportunity_ai import OpportunityAI, PartialOpportunityAI
from upsales.models.order_stages import OrderStage, OrderStageUpdateFields, PartialOrderStage
from upsales.models.orders import Order, OrderCreateFields, OrderUpdateFields, PartialOrder
from upsales.models.pages import Page, PageUpdateFields, PartialPage
from upsales.models.periodization import (
    PartialPeriodization,
    Periodization,
    PeriodizationCreateFields,
    PeriodizationUpdateFields,
)
from upsales.models.phone_call import (
    PartialPhoneCall,
    PhoneCall,
    PhoneCallUpdateFields,
)
from upsales.models.price_tier import PartialPriceTier, PriceTier
from upsales.models.pricelist import PartialPricelist, Pricelist, PricelistUpdateFields
from upsales.models.processed_by import PartialProcessedBy, ProcessedBy
from upsales.models.product import PartialProduct, Product
from upsales.models.product_categories import (
    PartialProductCategory,
    ProductCategory,
    ProductCategoryUpdateFields,
)
from upsales.models.project_plan_priority import (
    PartialProjectPlanPriority,
    ProjectPlanPriority,
    ProjectPlanPriorityUpdateFields,
)
from upsales.models.project_plan_stages import (
    PartialProjectPlanStage,
    ProjectPlanStage,
    ProjectPlanStageUpdateFields,
)
from upsales.models.project_plan_status import (
    PartialProjectPlanStatus,
    ProjectPlanStatus,
    ProjectPlanStatusUpdateFields,
)
from upsales.models.project_plan_types import (
    PartialProjectPlanType,
    ProjectPlanType,
    ProjectPlanTypeUpdateFields,
)
from upsales.models.projects import PartialProject, Project, ProjectUpdateFields
from upsales.models.provisioning import PartialProvisioningRequest, ProvisioningRequest
from upsales.models.quota import PartialQuota, Quota, QuotaUpdateFields
from upsales.models.report_view import PartialReportView, ReportView
from upsales.models.reset_score import (
    PartialResetScore,
    ResetScoreRequest,
    ResetScoreResponse,
)
from upsales.models.resources_upload_external import (
    PartialResourcesUploadExternal,
    ResourcesUploadExternal,
    ResourcesUploadExternalUpdateFields,
)
from upsales.models.resources_upload_internal import (
    PartialResourcesUploadInternal,
    ResourcesUploadInternal,
    ResourcesUploadInternalUpdateFields,
)
from upsales.models.roles import PartialRole, Role, RoleUpdateFields
from upsales.models.sales_coaches import PartialSalesCoach, SalesCoach, SalesCoachUpdateFields
from upsales.models.salesboard_cards import PartialSalesboardCard, SalesboardCard
from upsales.models.segments import PartialSegment, Segment, SegmentUpdateFields
from upsales.models.self import AccountManager, ClientDetail, Self, SelfClient, VersionData
from upsales.models.send_beam import SendBeam, SendBeamCreateFields
from upsales.models.soliditet_clients import (
    PartialSoliditetClient,
    SoliditetClient,
)
from upsales.models.standard_creative import (
    PartialStandardCreative,
    StandardCreative,
)
from upsales.models.standard_integration import (
    PartialStandardIntegration,
    StandardIntegration,
    StandardIntegrationUpdateFields,
)
from upsales.models.standard_integration_data import (
    StandardIntegrationData,
    StandardIntegrationDataCreateFields,
)
from upsales.models.standard_integration_settings import (
    PartialStandardIntegrationSettings,
    StandardIntegrationSettings,
    StandardIntegrationSettingsUpdateFields,
)
from upsales.models.standard_integration_user_settings import (
    PartialStandardIntegrationUserSettings,
    StandardIntegrationUserSettings,
    StandardIntegrationUserSettingsUpdateFields,
)
from upsales.models.static_values import CreditRating, IndustryCode, StaticValue, StaticValues
from upsales.models.suggestions import PartialSuggestion, Suggestion, SuggestionUpdateFields
from upsales.models.system_mail import (
    SystemMailCreateFields,
    SystemMailRequest,
    SystemMailResponse,
)
from upsales.models.ticket_statuses import (
    PartialTicketStatus,
    TicketStatus,
    TicketStatusUpdateFields,
)
from upsales.models.ticket_types import PartialTicketType, TicketType, TicketTypeUpdateFields
from upsales.models.tickets import PartialTicket, Ticket, TicketUpdateFields
from upsales.models.todo_views import TodoView
from upsales.models.trigger_attributes import TriggerAttribute, TriggerAttributes
from upsales.models.triggers import PartialTrigger, Trigger, TriggerUpdateFields
from upsales.models.user import PartialUser, User, UserUpdateFields
from upsales.models.user_defined_object_1 import PartialUserDefinedObject1, UserDefinedObject1
from upsales.models.user_defined_object_2 import PartialUserDefinedObject2, UserDefinedObject2
from upsales.models.user_defined_object_3 import PartialUserDefinedObject3, UserDefinedObject3
from upsales.models.user_defined_object_4 import PartialUserDefinedObject4, UserDefinedObject4
from upsales.models.user_defined_object_categories import (
    PartialUserDefinedObjectCategory,
    UserDefinedObjectCategory,
    UserDefinedObjectCategoryUpdateFields,
)
from upsales.models.user_defined_object_definition import (
    PartialUserDefinedObjectDefinition,
    UserDefinedObjectDefinition,
)
from upsales.models.user_invites import (
    PartialUserInvite,
    UserInvite,
    UserInviteUpdateFields,
)
from upsales.models.validate_page import ValidatePageRequest, ValidatePageResponse
from upsales.models.visits import PartialVisit, Visit
from upsales.models.voice import (
    PartialVoiceOperation,
    VoiceCallData,
    VoiceOperation,
    VoiceRecording,
)

# Rebuild models with forward references after all models are imported
# This resolves Pydantic v2 forward reference issues
Company.model_rebuild()
Form.model_rebuild()
FormSubmit.model_rebuild()
MailCampaign.model_rebuild()
MarketRejectlist.model_rebuild()
Ticket.model_rebuild()

__all__ = [
    "BaseModel",
    "PartialModel",
    "BulkSaveFields",
    "BulkSaveRequest",
    "ResetScoreRequest",
    "ResetScoreResponse",
    "PartialResetScore",
    "BulkSaveResponse",
    "PartialBulkSaveRequest",
    "BannerGroup",
    "PartialBannerGroup",
    "ReportView",
    "PartialReportView",
    "ResourcesUploadExternal",
    "ResourcesUploadExternalUpdateFields",
    "PartialResourcesUploadExternal",
    "ResourcesUploadInternal",
    "ResourcesUploadInternalUpdateFields",
    "PartialResourcesUploadInternal",
    "NotificationSetting",
    "PartialNotificationSetting",
    "Esign",
    "PartialEsign",
    "EsignFunctionSettings",
    "EsignFunctionSettingsFields",
    "SalesboardCard",
    "PartialSalesboardCard",
    "OnboardingImport",
    "PartialOnboardingImport",
    "Visit",
    "PartialVisit",
    "UserDefinedObject1",
    "PartialUserDefinedObject1",
    "UserDefinedObject2",
    "PartialUserDefinedObject2",
    "UserDefinedObject3",
    "PartialUserDefinedObject3",
    "UserDefinedObject4",
    "UserDefinedObjectCategory",
    "UserDefinedObjectCategoryUpdateFields",
    "PartialUserDefinedObjectCategory",
    "UserDefinedObjectDefinition",
    "UserDefinedObjectDefinitionUpdateFields",
    "PartialUserDefinedObjectDefinition",
    "PartialUserDefinedObject4",
    "BundledProduct",
    "BundledProductUpdateFields",
    "PartialBundledProduct",
    "CustomFields",
    "CustomField",
    "CustomFieldType",
    "PartialCustomField",
    "Agreement",
    "AgreementUpdateFields",
    "PartialAgreement",
    "AgreementGroup",
    "AgreementGroupUpdateFields",
    "PartialAgreementGroup",
    "Activity",
    "ActivityUpdateFields",
    "PartialActivity",
    "ActivityListItem",
    "ActivityType",
    "AdAccount",
    "AdAccountUpdateFields",
    "PartialAdAccount",
    "ActivityTypeUpdateFields",
    "PartialActivityType",
    "AdCampaign",
    "AdCampaignUpdateFields",
    "PartialAdCampaign",
    "NestedAdCampaign",
    "PartialNestedAdCampaign",
    "AdCreative",
    "AdCreativeUpdateFields",
    "PartialAdCreative",
    "Address",
    "AddressList",
    "AddressType",
    "VALID_ADDRESS_TYPES",
    "PartialAddress",
    "ApiKey",
    "ApiKeyUpdateFields",
    "PartialApiKey",
    "Appointment",
    "AppointmentUpdateFields",
    "PartialAppointment",
    "Assignment",
    "PartialAssignment",
    "ClientCategory",
    "ClientCategoryUpdateFields",
    "PartialClientCategory",
    "ClientIpInfo",
    "ClientIp",
    "ClientIpUpdateFields",
    "PartialClientIp",
    "ClientCategoryType",
    "ClientCategoryTypeUpdateFields",
    "PartialClientCategoryType",
    "ClientRelation",
    "ClientRelationUpdateFields",
    "PartialClientRelation",
    "Company",
    "PartialCompany",
    "Contact",
    "ContactRelation",
    "ContactRelationUpdateFields",
    "PartialContactRelation",
    "ContractAccepted",
    "ContractAcceptedUpdateFields",
    "PartialContractAccepted",
    "ContactCreateFields",
    "ContactUpdateFields",
    "PartialContact",
    "Currency",
    "CurrencyUpdateFields",
    "PartialCurrency",
    "CurrencyConfiguration",
    "PartialCurrencyConfiguration",
    "DataSourceRequest",
    "DataSourceResponse",
    "PartialDataSourceResponse",
    "EngageCreditTransaction",
    "PartialEngageCreditTransaction",
    "Event",
    "EventCreateFields",
    "EventUpdateFields",
    "PartialEvent",
    "File",
    "FileUpdateFields",
    "PartialFile",
    "FileUpload",
    "FileUploadUpdateFields",
    "PartialFileUpload",
    "Flow",
    "FlowUpdateFields",
    "PartialFlow",
    "Form",
    "FormUpdateFields",
    "PartialForm",
    "FormAction",
    "FormActionProperty",
    "PartialFormAction",
    "FormElement",
    "FormElementUpdateFields",
    "PartialFormElement",
    "FormField",
    "FormSubmit",
    "FormSubmitUpdateFields",
    "PartialFormSubmit",
    "PartialFormField",
    "GroupMailCategory",
    "GroupMailCategoryUpdateFields",
    "PartialGroupMailCategory",
    "ImportMailCampaignMailRequest",
    "ImportMailCampaignMailResponse",
    "ImportMailEventResponse",
    "MailEvent",
    "MailEventType",
    "SkippedEvent",
    "JourneyStep",
    "JourneyStepUpdateFields",
    "PartialJourneyStep",
    "LeadChannel",
    "PartialLeadChannel",
    "LeadSource",
    "PartialLeadSource",
    "Lead",
    "LeadUpdateFields",
    "PartialLead",
    "ListView",
    "ListViewUpdateFields",
    "PartialListView",
    "Mail",
    "MailUpdateFields",
    "PartialMail",
    "MailMultiItem",
    "MailMultiRequest",
    "MailMultiResponse",
    "MailCampaign",
    "MailCampaignUpdateFields",
    "PartialMailCampaign",
    "MailDomain",
    "PartialMailDomain",
    "MailEditorToken",
    "MailTemplate",
    "MailTemplateUpdateFields",
    "PartialMailTemplate",
    "MailTestResponse",
    "MailTestSendFields",
    "MarketRejectlist",
    "MarketRejectlistUpdateFields",
    "PartialMarketRejectlist",
    "Metadata",
    "Notification",
    "NotifyRequest",
    "MetadataCurrency",
    "MetadataUser",
    "SystemParams",
    "FieldDefinition",
    "PartialNotification",
    "OpportunityAI",
    "PartialOpportunityAI",
    "Order",
    "OrderCreateFields",
    "OrderUpdateFields",
    "PartialOrder",
    "OrderStage",
    "OrderStageUpdateFields",
    "PartialOrderStage",
    "Page",
    "PageUpdateFields",
    "PartialPage",
    "Periodization",
    "PeriodizationCreateFields",
    "PeriodizationUpdateFields",
    "PartialPeriodization",
    "PhoneCall",
    "PhoneCallUpdateFields",
    "PartialPhoneCall",
    "PriceTier",
    "PartialPriceTier",
    "Pricelist",
    "PricelistUpdateFields",
    "PartialPricelist",
    "ProcessedBy",
    "PartialProcessedBy",
    "Product",
    "PartialProduct",
    "ProductCategory",
    "ProductCategoryUpdateFields",
    "PartialProductCategory",
    "ProjectPlanPriority",
    "ProjectPlanPriorityUpdateFields",
    "PartialProjectPlanPriority",
    "ProjectPlanStage",
    "ProjectPlanStageUpdateFields",
    "PartialProjectPlanStage",
    "ProjectPlanStatus",
    "ProjectPlanStatusUpdateFields",
    "PartialProjectPlanStatus",
    "ProjectPlanType",
    "ProjectPlanTypeUpdateFields",
    "PartialProjectPlanType",
    "Project",
    "ProjectUpdateFields",
    "PartialProject",
    "Quota",
    "QuotaUpdateFields",
    "PartialQuota",
    "Role",
    "RoleUpdateFields",
    "PartialRole",
    "SalesCoach",
    "SalesCoachUpdateFields",
    "PartialSalesCoach",
    "Segment",
    "SegmentUpdateFields",
    "PartialSegment",
    "SendBeam",
    "SendBeamCreateFields",
    "StandardCreative",
    "PartialStandardCreative",
    "StandardIntegration",
    "StandardIntegrationUpdateFields",
    "PartialStandardIntegration",
    "StandardIntegrationSettings",
    "StandardIntegrationSettingsUpdateFields",
    "PartialStandardIntegrationSettings",
    "StandardIntegrationUserSettings",
    "StandardIntegrationUserSettingsUpdateFields",
    "PartialStandardIntegrationUserSettings",
    "StandardIntegrationData",
    "StandardIntegrationDataCreateFields",
    "Self",
    "SelfClient",
    "ClientDetail",
    "VersionData",
    "AccountManager",
    "StaticValue",
    "CreditRating",
    "IndustryCode",
    "StaticValues",
    "Suggestion",
    "SuggestionUpdateFields",
    "PartialSuggestion",
    "TicketStatus",
    "TicketStatusUpdateFields",
    "PartialTicketStatus",
    "TicketType",
    "TicketTypeUpdateFields",
    "PartialTicketType",
    "Ticket",
    "TicketUpdateFields",
    "PartialTicket",
    "TodoView",
    "TriggerAttribute",
    "TriggerAttributes",
    "Trigger",
    "TriggerUpdateFields",
    "PartialTrigger",
    "Unsub",
    "UnsubUpdateFields",
    "PartialUnsub",
    "User",
    "UserUpdateFields",
    "PartialUser",
    "UserInvite",
    "UserInviteUpdateFields",
    "PartialUserInvite",
    "PartialCategory",
    "PartialCampaign",
    "ProvisioningRequest",
    "PartialProvisioningRequest",
    "ImageComposeCreateFields",
    "ImageComposeResponse",
    "SoliditetClient",
    "SoliditetClientUpdateFields",
    "PartialSoliditetClient",
    "VoiceCallData",
    "VoiceOperation",
    "VoiceRecording",
    "PartialVoiceOperation",
    "SystemMailRequest",
    "SystemMailResponse",
    "SystemMailCreateFields",
    "ValidatePageRequest",
    "ValidatePageResponse",
]
