"""
Integration tests for MailCampaign model with real API responses.

Uses VCR.py to record API responses on first run, then replay them.
Validates that our Pydantic v2 models correctly parse real API data.

To record cassettes:
    uv run pytest tests/integration/test_mail_campaigns_integration.py -v

To re-record (delete cassette first):
    rm -r tests/cassettes/integration/test_mail_campaigns_integration/
    uv run pytest tests/integration/test_mail_campaigns_integration.py -v
"""

import pytest
import vcr

from upsales import Upsales
from upsales.models.mail_campaigns import MailCampaign
from upsales.models.projects import PartialProject
from upsales.models.user import PartialUser

# Configure VCR for these tests
my_vcr = vcr.VCR(
    cassette_library_dir="tests/cassettes/integration",
    record_mode="once",  # Record once, then always replay
    match_on=["method", "scheme", "host", "port", "path"],
    filter_headers=[
        ("cookie", "REDACTED"),
        ("authorization", "REDACTED"),
    ],
    filter_post_data_parameters=[
        ("password", "REDACTED"),
    ],
)


@pytest.mark.asyncio
@my_vcr.use_cassette("test_mail_campaigns_integration/test_list_mail_campaigns_real_response.yaml")
async def test_list_mail_campaigns_real_response():
    """
    Test listing mail campaigns with real API response structure.

    Validates that MailCampaign model correctly parses list responses.

    Cassette: tests/cassettes/integration/test_mail_campaigns_integration/test_list_mail_campaigns_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        campaigns = await upsales.mail_campaigns.list(limit=5)

        assert isinstance(campaigns, list)

        if len(campaigns) == 0:
            pytest.skip("No mail campaigns found in the system")

        for campaign in campaigns:
            assert isinstance(campaign, MailCampaign)
            assert isinstance(campaign.id, int)
            assert campaign.id > 0
            assert isinstance(campaign.name, str)
            assert isinstance(campaign.subject, str)

            # Validate read-only fields
            assert isinstance(campaign.status, str)
            assert campaign.status in ("DRAFT", "SCHEDULED", "PROCESSING", "SENT")
            assert isinstance(campaign.mailSent, int)
            assert isinstance(campaign.mailRead, int)
            assert isinstance(campaign.mailClicked, int)
            assert isinstance(campaign.mailError, int)
            assert isinstance(campaign.mailPending, int)
            assert isinstance(campaign.mailUnsub, int)

            # Validate BinaryFlag field
            assert campaign.isArchived in (0, 1)

            # Validate required fields
            assert isinstance(campaign.body, str)
            assert isinstance(campaign.bodyJson, str)
            assert isinstance(campaign.fromName, str)
            assert isinstance(campaign.from_email, str)

        print(f"[OK] Listed {len(campaigns)} mail campaigns successfully")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_mail_campaigns_integration/test_get_mail_campaign_real_response.yaml")
async def test_get_mail_campaign_real_response():
    """
    Test getting a single mail campaign with real API response structure.

    This test records the actual API response on first run, then
    replays it from cassette on future runs.

    Cassette: tests/cassettes/integration/test_mail_campaigns_integration/test_get_mail_campaign_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        # First list to get a valid campaign ID
        campaigns = await upsales.mail_campaigns.list(limit=1)

        if len(campaigns) == 0:
            pytest.skip("No mail campaigns found in the system")

        campaign_id = campaigns[0].id

        # Now get the specific campaign
        campaign = await upsales.mail_campaigns.get(campaign_id)

        assert isinstance(campaign, MailCampaign)
        assert campaign.id == campaign_id
        assert isinstance(campaign.name, str)
        assert isinstance(campaign.subject, str)

        # Validate status
        assert isinstance(campaign.status, str)
        assert campaign.status in ("DRAFT", "SCHEDULED", "PROCESSING", "SENT")

        # Validate statistics
        assert isinstance(campaign.mailSent, int)
        assert isinstance(campaign.mailRead, int)
        assert isinstance(campaign.mailClicked, int)
        assert isinstance(campaign.mailError, int)
        assert isinstance(campaign.mailPending, int)
        assert isinstance(campaign.mailUnsub, int)

        # Validate required fields
        assert isinstance(campaign.body, str)
        assert isinstance(campaign.bodyJson, str)
        assert isinstance(campaign.fromName, str)
        assert isinstance(campaign.from_email, str)

        # Validate version and jobId
        assert isinstance(campaign.version, int)
        assert isinstance(campaign.jobId, int)

        # Validate lists
        assert isinstance(campaign.attachments, list)
        assert isinstance(campaign.labels, list)
        assert isinstance(campaign.segments, list)

        print(f"[OK] Got campaign {campaign.id}: {campaign.name}")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_mail_campaigns_integration/test_mail_campaign_nested_objects.yaml")
async def test_mail_campaign_nested_objects():
    """
    Test that nested objects (PartialUser, PartialProject) parse correctly.

    These nested objects often have fewer fields than their full counterparts,
    so this validates our Partial models handle the actual API responses.

    Cassette: tests/cassettes/integration/test_mail_campaigns_integration/test_mail_campaign_nested_objects.yaml
    """
    async with Upsales.from_env() as upsales:
        campaigns = await upsales.mail_campaigns.list(limit=20)

        if len(campaigns) == 0:
            pytest.skip("No mail campaigns found in the system")

        # Check various nested objects across campaigns
        found_user = False
        found_project = False
        found_template = False
        found_category = False

        for campaign in campaigns:
            # Test user if present
            if campaign.user is not None:
                found_user = True
                assert isinstance(campaign.user, PartialUser)
                assert hasattr(campaign.user, "id")
                assert hasattr(campaign.user, "name")
                assert isinstance(campaign.user.id, int)
                print(f"  [OK] user: id={campaign.user.id}, name={campaign.user.name}")

            # Test project if present
            if campaign.project is not None:
                found_project = True
                assert isinstance(campaign.project, PartialProject)
                assert hasattr(campaign.project, "id")
                assert isinstance(campaign.project.id, int)
                print(f"  [OK] project: id={campaign.project.id}")

            # Test template if present
            if campaign.template is not None:
                found_template = True
                assert isinstance(campaign.template, dict)
                print(f"  [OK] template: {type(campaign.template)}")

            # Test category if present
            if campaign.category is not None:
                found_category = True
                assert isinstance(campaign.category, dict)
                print(f"  [OK] category: {type(campaign.category)}")

        print(
            f"\n[OK] Nested objects found - user:{found_user}, project:{found_project}, "
            f"template:{found_template}, category:{found_category}"
        )


@pytest.mark.asyncio
@my_vcr.use_cassette("test_mail_campaigns_integration/test_mail_campaign_computed_fields.yaml")
async def test_mail_campaign_computed_fields():
    """
    Test computed fields work correctly with real API data.

    Validates is_archived, is_draft, is_sent, open_rate, click_rate computed properties.

    Cassette: tests/cassettes/integration/test_mail_campaigns_integration/test_mail_campaign_computed_fields.yaml
    """
    async with Upsales.from_env() as upsales:
        campaigns = await upsales.mail_campaigns.list(limit=10)

        if len(campaigns) == 0:
            pytest.skip("No mail campaigns found in the system")

        campaign = campaigns[0]

        # Test is_archived computed field
        assert isinstance(campaign.is_archived, bool)
        assert campaign.is_archived == (campaign.isArchived == 1)
        print(f"[OK] is_archived: {campaign.is_archived} (isArchived={campaign.isArchived})")

        # Test is_draft computed field
        assert isinstance(campaign.is_draft, bool)
        assert campaign.is_draft == (campaign.status == "DRAFT")
        print(f"[OK] is_draft: {campaign.is_draft} (status={campaign.status})")

        # Test is_sent computed field
        assert isinstance(campaign.is_sent, bool)
        assert campaign.is_sent == (campaign.status == "SENT")
        print(f"[OK] is_sent: {campaign.is_sent} (status={campaign.status})")

        # Test open_rate computed field
        assert isinstance(campaign.open_rate, float)
        if campaign.mailSent > 0:
            expected_rate = (campaign.mailRead / campaign.mailSent) * 100
            assert abs(campaign.open_rate - expected_rate) < 0.01
        else:
            assert campaign.open_rate == 0.0
        print(
            f"[OK] open_rate: {campaign.open_rate:.2f}% "
            f"(mailRead={campaign.mailRead}, mailSent={campaign.mailSent})"
        )

        # Test click_rate computed field
        assert isinstance(campaign.click_rate, float)
        if campaign.mailSent > 0:
            expected_rate = (campaign.mailClicked / campaign.mailSent) * 100
            assert abs(campaign.click_rate - expected_rate) < 0.01
        else:
            assert campaign.click_rate == 0.0
        print(
            f"[OK] click_rate: {campaign.click_rate:.2f}% "
            f"(mailClicked={campaign.mailClicked}, mailSent={campaign.mailSent})"
        )


@pytest.mark.asyncio
@my_vcr.use_cassette("test_mail_campaigns_integration/test_mail_campaign_drafts.yaml")
async def test_mail_campaign_drafts():
    """
    Test getting draft campaigns with real API data.

    Validates the get_drafts() resource method.

    Cassette: tests/cassettes/integration/test_mail_campaigns_integration/test_mail_campaign_drafts.yaml
    """
    async with Upsales.from_env() as upsales:
        drafts = await upsales.mail_campaigns.get_drafts()

        assert isinstance(drafts, list)

        for draft in drafts:
            assert isinstance(draft, MailCampaign)
            assert draft.status == "DRAFT"
            assert draft.is_draft is True

        print(f"[OK] Found {len(drafts)} draft campaigns")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_mail_campaigns_integration/test_mail_campaign_sent.yaml")
async def test_mail_campaign_sent():
    """
    Test getting sent campaigns with real API data.

    Validates the get_sent() resource method and statistics.

    Cassette: tests/cassettes/integration/test_mail_campaigns_integration/test_mail_campaign_sent.yaml
    """
    async with Upsales.from_env() as upsales:
        sent = await upsales.mail_campaigns.get_sent()

        assert isinstance(sent, list)

        if len(sent) == 0:
            pytest.skip("No sent campaigns found in the system")

        for campaign in sent:
            assert isinstance(campaign, MailCampaign)
            assert campaign.status == "SENT"
            assert campaign.is_sent is True

            # Sent campaigns should have statistics
            assert campaign.mailSent >= 0
            assert campaign.mailRead >= 0
            assert campaign.mailClicked >= 0

            # Rates should be calculable
            assert isinstance(campaign.open_rate, float)
            assert isinstance(campaign.click_rate, float)

        print(f"[OK] Found {len(sent)} sent campaigns with statistics")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_mail_campaigns_integration/test_mail_campaign_archived.yaml")
async def test_mail_campaign_archived():
    """
    Test getting archived campaigns with real API data.

    Validates the get_archived() resource method.

    Cassette: tests/cassettes/integration/test_mail_campaigns_integration/test_mail_campaign_archived.yaml
    """
    async with Upsales.from_env() as upsales:
        archived = await upsales.mail_campaigns.get_archived()

        assert isinstance(archived, list)

        for campaign in archived:
            assert isinstance(campaign, MailCampaign)
            assert campaign.isArchived == 1
            assert campaign.is_archived is True

        print(f"[OK] Found {len(archived)} archived campaigns")
