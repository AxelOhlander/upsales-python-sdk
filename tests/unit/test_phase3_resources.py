"""Unit tests for Phase 3 read-only endpoint resources.

Tests all 45 new GET-only resource managers added in Phase 3.
Each test verifies client registration and basic GET functionality.
"""

import pytest
from pytest_httpx import HTTPXMock

from upsales import Upsales

API = "https://power.upsales.com/api/v2"


def _wrap(data: dict | list | str = "OK") -> dict:
    """Wrap data in standard Upsales response format."""
    return {"error": None, "data": data}


# ── Client Registration Tests ───────────────────────────────────

PHASE3_ATTRS = [
    "quick_search",
    "lookup",
    "find_prospect",
    "email_duplicates",
    "email_suggest",
    "email_suggestion",
    "report",
    "report_widget",
    "report_widget_metadata",
    "report_client_company_type",
    "scoreboard",
    "mail_by_thread",
    "mail_campaign_info",
    "mail_templates_recently_used",
    "mail_templates_used_in",
    "leads2",
    "lead_sources2",
    "looker_sso",
    "looker_explores",
    "looker_looks",
    "docebo_sso",
    "standard_integration_user",
    "unread_notifications",
    "signals_feed",
    "ad_credits",
    "ad_locations",
    "file_download",
    "resources_download_adgear",
    "resources_download_internal",
    "client_form",
    "forms_external_lead_source",
    "landing_page_templates",
    "engage_site_templates",
    "flow_contacts",
    "journey_step_history",
    "soliditet_search",
    "delete_log",
    "events_prior",
    "group_structure",
    "industries",
    "links",
    "placeholder",
    "role_settings",
    "what_is_my_ip",
    "worker_status",
]


class TestPhase3Registration:
    """Test all Phase 3 resources are registered on client."""

    @pytest.mark.parametrize("attr", PHASE3_ATTRS)
    def test_registered(self, attr: str) -> None:
        """Test resource is registered on client."""
        upsales = Upsales(token="test")
        assert hasattr(upsales, attr), f"Missing attribute: {attr}"


# ── Search & Lookup ─────────────────────────────────────────────


class TestQuickSearchResource:
    """Tests for QuickSearchResource."""

    @pytest.mark.anyio
    async def test_search(self, httpx_mock: HTTPXMock) -> None:
        """Test cross-entity search."""
        httpx_mock.add_response(
            url=f"{API}/quicksearch?q=ACME",
            json=_wrap([{"type": "client", "name": "ACME"}]),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.quick_search.search(query="ACME")
        assert len(result["data"]) == 1


class TestLookupResource:
    """Tests for LookupResource."""

    @pytest.mark.anyio
    async def test_lookup(self, httpx_mock: HTTPXMock) -> None:
        """Test entity lookup."""
        httpx_mock.add_response(
            url=f"{API}/lookup",
            json=_wrap([]),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.lookup.lookup()
        assert result["error"] is None


class TestFindProspectResource:
    """Tests for FindProspectResource."""

    @pytest.mark.anyio
    async def test_find(self, httpx_mock: HTTPXMock) -> None:
        """Test prospect finder."""
        httpx_mock.add_response(
            url=f"{API}/findProspect",
            json=_wrap([]),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.find_prospect.find()
        assert result["error"] is None


class TestEmailDuplicatesResource:
    """Tests for EmailDuplicatesResource."""

    @pytest.mark.anyio
    async def test_check(self, httpx_mock: HTTPXMock) -> None:
        """Test duplicate email check."""
        httpx_mock.add_response(
            url=f"{API}/function/email-duplicates",
            json=_wrap([]),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.email_duplicates.check()
        assert result["error"] is None


class TestEmailSuggestResource:
    """Tests for EmailSuggestResource."""

    @pytest.mark.anyio
    async def test_suggest(self, httpx_mock: HTTPXMock) -> None:
        """Test email suggestion."""
        httpx_mock.add_response(
            url=f"{API}/function/email-suggest",
            json=_wrap([]),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.email_suggest.suggest()
        assert result["error"] is None


class TestEmailSuggestionResource:
    """Tests for EmailSuggestionResource."""

    @pytest.mark.anyio
    async def test_get(self, httpx_mock: HTTPXMock) -> None:
        """Test email suggestion alternate."""
        httpx_mock.add_response(
            url=f"{API}/emailSuggestion",
            json=_wrap([]),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.email_suggestion.get()
        assert result["error"] is None


# ── Reporting ────────────────────────────────────────────────────


class TestReportResource:
    """Tests for ReportResource."""

    @pytest.mark.anyio
    async def test_get(self, httpx_mock: HTTPXMock) -> None:
        """Test report data retrieval."""
        httpx_mock.add_response(
            url=f"{API}/report/api/Client",
            json=_wrap({"rows": []}),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.report.get(entity="Client")
        assert "rows" in result["data"]


class TestReportWidgetResource:
    """Tests for ReportWidgetResource."""

    @pytest.mark.anyio
    async def test_get(self, httpx_mock: HTTPXMock) -> None:
        """Test report widget data."""
        httpx_mock.add_response(
            url=f"{API}/report/widget",
            json=_wrap({}),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.report_widget.get()
        assert result["error"] is None


class TestReportWidgetMetadataResource:
    """Tests for ReportWidgetMetadataResource."""

    @pytest.mark.anyio
    async def test_get(self, httpx_mock: HTTPXMock) -> None:
        """Test report widget metadata."""
        httpx_mock.add_response(
            url=f"{API}/report/metadata/widget",
            json=_wrap({}),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.report_widget_metadata.get()
        assert result["error"] is None


class TestReportClientCompanyTypeResource:
    """Tests for ReportClientCompanyTypeResource."""

    @pytest.mark.anyio
    async def test_get(self, httpx_mock: HTTPXMock) -> None:
        """Test company type report."""
        httpx_mock.add_response(
            url=f"{API}/report/clientCompanyType",
            json=_wrap({}),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.report_client_company_type.get()
        assert result["error"] is None


class TestScoreboardResource:
    """Tests for ScoreboardResource."""

    @pytest.mark.anyio
    async def test_get(self, httpx_mock: HTTPXMock) -> None:
        """Test scoreboard data."""
        httpx_mock.add_response(
            url=f"{API}/scoreboard",
            json=_wrap([]),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.scoreboard.get()
        assert result["error"] is None


# ── Mail ──────────────────────────────────────────────────────


class TestMailByThreadResource:
    """Tests for MailByThreadResource."""

    @pytest.mark.anyio
    async def test_list(self, httpx_mock: HTTPXMock) -> None:
        """Test mail by thread listing."""
        httpx_mock.add_response(
            url=f"{API}/mail/byThread",
            json=_wrap([]),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.mail_by_thread.list()
        assert result["error"] is None


class TestMailCampaignInfoResource:
    """Tests for MailCampaignInfoResource."""

    @pytest.mark.anyio
    async def test_get(self, httpx_mock: HTTPXMock) -> None:
        """Test campaign info."""
        httpx_mock.add_response(
            url=f"{API}/mailCampaignInfo",
            json=_wrap({}),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.mail_campaign_info.get()
        assert result["error"] is None

    @pytest.mark.anyio
    async def test_preview(self, httpx_mock: HTTPXMock) -> None:
        """Test campaign preview."""
        httpx_mock.add_response(
            url=f"{API}/mailCampaignInfo/preview",
            json=_wrap({}),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.mail_campaign_info.preview()
        assert result["error"] is None


class TestMailTemplatesRecentlyUsedResource:
    """Tests for MailTemplatesRecentlyUsedResource."""

    @pytest.mark.anyio
    async def test_list(self, httpx_mock: HTTPXMock) -> None:
        """Test recently used templates."""
        httpx_mock.add_response(
            url=f"{API}/mail/templates/recentlyUsed",
            json=_wrap([]),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.mail_templates_recently_used.list()
        assert result["error"] is None


class TestMailTemplatesUsedInResource:
    """Tests for MailTemplatesUsedInResource."""

    @pytest.mark.anyio
    async def test_get(self, httpx_mock: HTTPXMock) -> None:
        """Test template usage info."""
        httpx_mock.add_response(
            url=f"{API}/mail/templates/usedIn",
            json=_wrap({}),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.mail_templates_used_in.get()
        assert result["error"] is None


# ── Leads ─────────────────────────────────────────────────────


class TestLeads2Resource:
    """Tests for Leads2Resource."""

    @pytest.mark.anyio
    async def test_list(self, httpx_mock: HTTPXMock) -> None:
        """Test leads v2 listing."""
        httpx_mock.add_response(
            url=f"{API}/leads2",
            json=_wrap([]),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.leads2.list()
        assert result["error"] is None


class TestLeadSources2Resource:
    """Tests for LeadSources2Resource."""

    @pytest.mark.anyio
    async def test_list(self, httpx_mock: HTTPXMock) -> None:
        """Test lead sources v2."""
        httpx_mock.add_response(
            url=f"{API}/leadsources2",
            json=_wrap([]),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.lead_sources2.list()
        assert result["error"] is None


# ── Integrations & SSO ────────────────────────────────────────


class TestLookerSSOResource:
    """Tests for LookerSSOResource."""

    @pytest.mark.anyio
    async def test_get_url(self, httpx_mock: HTTPXMock) -> None:
        """Test Looker SSO URL."""
        httpx_mock.add_response(
            url=f"{API}/function/externalSSO/looker/explore/123",
            json=_wrap({"url": "https://looker.example.com/sso"}),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.looker_sso.get_url(type="explore", id="123")
        assert "url" in result["data"]


class TestLookerExploresResource:
    """Tests for LookerExploresResource."""

    @pytest.mark.anyio
    async def test_list(self, httpx_mock: HTTPXMock) -> None:
        """Test Looker explores listing."""
        httpx_mock.add_response(
            url=f"{API}/looker/explores",
            json=_wrap([]),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.looker_explores.list()
        assert result["error"] is None


class TestLookerLooksResource:
    """Tests for LookerLooksResource."""

    @pytest.mark.anyio
    async def test_list(self, httpx_mock: HTTPXMock) -> None:
        """Test Looker looks listing."""
        httpx_mock.add_response(
            url=f"{API}/looker/looks",
            json=_wrap([]),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.looker_looks.list()
        assert result["error"] is None


class TestDoceboSSOResource:
    """Tests for DoceboSSOResource."""

    @pytest.mark.anyio
    async def test_get_url(self, httpx_mock: HTTPXMock) -> None:
        """Test Docebo SSO URL."""
        httpx_mock.add_response(
            url=f"{API}/function/externalSSO/docebo",
            json=_wrap({"url": "https://docebo.example.com"}),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.docebo_sso.get_url()
        assert result["error"] is None


class TestStandardIntegrationUserResource:
    """Tests for StandardIntegrationUserResource."""

    @pytest.mark.anyio
    async def test_list(self, httpx_mock: HTTPXMock) -> None:
        """Test standard integration user listing."""
        httpx_mock.add_response(
            url=f"{API}/standardIntegrationUser",
            json=_wrap([]),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.standard_integration_user.list()
        assert result["error"] is None


# ── Notifications & Signals ───────────────────────────────────


class TestUnreadNotificationsResource:
    """Tests for UnreadNotificationsResource."""

    @pytest.mark.anyio
    async def test_get(self, httpx_mock: HTTPXMock) -> None:
        """Test unread notification count."""
        httpx_mock.add_response(
            url=f"{API}/notificationsUnread/42",
            json=_wrap({"count": 5}),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.unread_notifications.get(user_id=42)
        assert result["data"]["count"] == 5


class TestSignalsFeedResource:
    """Tests for SignalsFeedResource."""

    @pytest.mark.anyio
    async def test_list(self, httpx_mock: HTTPXMock) -> None:
        """Test signals feed."""
        httpx_mock.add_response(
            url=f"{API}/prospecting/signals",
            json=_wrap([]),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.signals_feed.list()
        assert result["error"] is None


# ── Ads ───────────────────────────────────────────────────────


class TestAdCreditsResource:
    """Tests for AdCreditsResource."""

    @pytest.mark.anyio
    async def test_get(self, httpx_mock: HTTPXMock) -> None:
        """Test ad credits."""
        httpx_mock.add_response(
            url=f"{API}/engage/credit",
            json=_wrap({"balance": 100}),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.ad_credits.get()
        assert result["data"]["balance"] == 100


class TestAdLocationsResource:
    """Tests for AdLocationsResource."""

    @pytest.mark.anyio
    async def test_list(self, httpx_mock: HTTPXMock) -> None:
        """Test ad locations."""
        httpx_mock.add_response(
            url=f"{API}/engage/location",
            json=_wrap([]),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.ad_locations.list()
        assert result["error"] is None


# ── Files & Resources ─────────────────────────────────────────


class TestFileDownloadResource:
    """Tests for FileDownloadResource."""

    @pytest.mark.anyio
    async def test_get(self, httpx_mock: HTTPXMock) -> None:
        """Test file download."""
        httpx_mock.add_response(
            url=f"{API}/file/download",
            json=_wrap({}),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.file_download.get()
        assert result["error"] is None


class TestResourcesDownloadAdgearResource:
    """Tests for ResourcesDownloadAdgearResource."""

    @pytest.mark.anyio
    async def test_get(self, httpx_mock: HTTPXMock) -> None:
        """Test adgear download."""
        httpx_mock.add_response(
            url=f"{API}/resources/download/adgear",
            json=_wrap({}),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.resources_download_adgear.get()
        assert result["error"] is None


class TestResourcesDownloadInternalResource:
    """Tests for ResourcesDownloadInternalResource."""

    @pytest.mark.anyio
    async def test_get(self, httpx_mock: HTTPXMock) -> None:
        """Test internal download."""
        httpx_mock.add_response(
            url=f"{API}/resources/download/internal",
            json=_wrap({}),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.resources_download_internal.get()
        assert result["error"] is None


# ── Forms & Pages ─────────────────────────────────────────────


class TestClientFormResource:
    """Tests for ClientFormResource."""

    @pytest.mark.anyio
    async def test_list(self, httpx_mock: HTTPXMock) -> None:
        """Test client forms."""
        httpx_mock.add_response(
            url=f"{API}/clientform",
            json=_wrap([]),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.client_form.list()
        assert result["error"] is None


class TestFormsExternalLeadSourceResource:
    """Tests for FormsExternalLeadSourceResource."""

    @pytest.mark.anyio
    async def test_list(self, httpx_mock: HTTPXMock) -> None:
        """Test external lead source forms."""
        httpx_mock.add_response(
            url=f"{API}/forms/external-lead-source",
            json=_wrap([]),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.forms_external_lead_source.list()
        assert result["error"] is None


class TestLandingPageTemplateResource:
    """Tests for LandingPageTemplateResource."""

    @pytest.mark.anyio
    async def test_list(self, httpx_mock: HTTPXMock) -> None:
        """Test landing page templates."""
        httpx_mock.add_response(
            url=f"{API}/landingPageTemplate",
            json=_wrap([]),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.landing_page_templates.list()
        assert result["error"] is None


class TestEngageSiteTemplateResource:
    """Tests for EngageSiteTemplateResource."""

    @pytest.mark.anyio
    async def test_list(self, httpx_mock: HTTPXMock) -> None:
        """Test engage site templates."""
        httpx_mock.add_response(
            url=f"{API}/engage/siteTemplate",
            json=_wrap([]),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.engage_site_templates.list()
        assert result["error"] is None


# ── Flows & Journeys ──────────────────────────────────────────


class TestFlowContactsResource:
    """Tests for FlowContactsResource."""

    @pytest.mark.anyio
    async def test_list(self, httpx_mock: HTTPXMock) -> None:
        """Test flow contacts listing."""
        httpx_mock.add_response(
            url=f"{API}/flows/1/2/contacts/waiting",
            json=_wrap([]),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.flow_contacts.list(flow_id=1, step_id=2, stats_type="waiting")
        assert result["error"] is None


class TestJourneyStepHistoryResource:
    """Tests for JourneyStepHistoryResource."""

    @pytest.mark.anyio
    async def test_list(self, httpx_mock: HTTPXMock) -> None:
        """Test journey step history."""
        httpx_mock.add_response(
            url=f"{API}/journeyStepHistory",
            json=_wrap([]),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.journey_step_history.list()
        assert result["error"] is None


# ── Soliditet ─────────────────────────────────────────────────


class TestSoliditetSearchResource:
    """Tests for SoliditetSearchResource."""

    @pytest.mark.anyio
    async def test_search(self, httpx_mock: HTTPXMock) -> None:
        """Test Soliditet search."""
        httpx_mock.add_response(
            url=f"{API}/soliditet/search",
            json=_wrap([]),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.soliditet_search.search()
        assert result["error"] is None


# ── Other ─────────────────────────────────────────────────────


class TestDeleteLogResource:
    """Tests for DeleteLogResource."""

    @pytest.mark.anyio
    async def test_list(self, httpx_mock: HTTPXMock) -> None:
        """Test deletion log."""
        httpx_mock.add_response(
            url=f"{API}/deleteLog",
            json=_wrap([]),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.delete_log.list()
        assert result["error"] is None


class TestEventsPriorResource:
    """Tests for EventsPriorResource."""

    @pytest.mark.anyio
    async def test_list(self, httpx_mock: HTTPXMock) -> None:
        """Test prior events."""
        httpx_mock.add_response(
            url=f"{API}/events/prior",
            json=_wrap([]),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.events_prior.list()
        assert result["error"] is None


class TestGroupStructureResource:
    """Tests for GroupStructureResource."""

    @pytest.mark.anyio
    async def test_list(self, httpx_mock: HTTPXMock) -> None:
        """Test group structure."""
        httpx_mock.add_response(
            url=f"{API}/prospectinggroupstructure",
            json=_wrap([]),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.group_structure.list()
        assert result["error"] is None


class TestIndustriesResource:
    """Tests for IndustriesResource."""

    @pytest.mark.anyio
    async def test_list(self, httpx_mock: HTTPXMock) -> None:
        """Test industries list."""
        httpx_mock.add_response(
            url=f"{API}/industries",
            json=_wrap([]),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.industries.list()
        assert result["error"] is None


class TestLinksResource:
    """Tests for LinksResource."""

    @pytest.mark.anyio
    async def test_list(self, httpx_mock: HTTPXMock) -> None:
        """Test links tracking."""
        httpx_mock.add_response(
            url=f"{API}/links",
            json=_wrap([]),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.links.list()
        assert result["error"] is None


class TestPlaceholderResource:
    """Tests for PlaceholderResource."""

    @pytest.mark.anyio
    async def test_get(self, httpx_mock: HTTPXMock) -> None:
        """Test placeholder data."""
        httpx_mock.add_response(
            url=f"{API}/placeholder/dashboard",
            json=_wrap({}),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.placeholder.get(feature="dashboard")
        assert result["error"] is None


class TestRoleSettingsResource:
    """Tests for RoleSettingsResource."""

    @pytest.mark.anyio
    async def test_list(self, httpx_mock: HTTPXMock) -> None:
        """Test role settings."""
        httpx_mock.add_response(
            url=f"{API}/roleSettings",
            json=_wrap([]),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.role_settings.list()
        assert result["error"] is None


class TestWhatIsMyIpResource:
    """Tests for WhatIsMyIpResource."""

    @pytest.mark.anyio
    async def test_get(self, httpx_mock: HTTPXMock) -> None:
        """Test IP lookup."""
        httpx_mock.add_response(
            url=f"{API}/function/whatismyip",
            json=_wrap({"ip": "1.2.3.4"}),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.what_is_my_ip.get()
        assert result["data"]["ip"] == "1.2.3.4"


class TestWorkerStatusResource:
    """Tests for WorkerStatusResource."""

    @pytest.mark.anyio
    async def test_get(self, httpx_mock: HTTPXMock) -> None:
        """Test worker status."""
        httpx_mock.add_response(
            url=f"{API}/worker/status",
            json=_wrap({"running": True}),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.worker_status.get()
        assert result["data"]["running"] is True
