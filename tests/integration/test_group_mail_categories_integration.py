"""
Integration tests for GroupMailCategory model with real API responses.

Uses VCR.py to record API responses on first run, then replay them.
Validates that our Pydantic v2 models correctly parse real API data.

To record cassettes:
    uv run pytest tests/integration/test_group_mail_categories_integration.py -v

To re-record (delete cassette first):
    rm -r tests/cassettes/integration/test_group_mail_categories_integration/
    uv run pytest tests/integration/test_group_mail_categories_integration.py -v
"""

import pytest
import vcr

from upsales import Upsales
from upsales.models.group_mail_categories import GroupMailCategory

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
@my_vcr.use_cassette(
    "test_group_mail_categories_integration/test_list_group_mail_categories_real_response.yaml"
)
async def test_list_group_mail_categories_real_response():
    """
    Test listing group mail categories with real API response structure.

    Validates that GroupMailCategory model correctly parses real API data.

    Cassette: tests/cassettes/integration/test_group_mail_categories_integration/test_list_group_mail_categories_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        categories = await upsales.group_mail_categories.list(limit=10)

        assert isinstance(categories, list)

        if len(categories) == 0:
            pytest.skip("No group mail categories found in the system")

        for category in categories:
            assert isinstance(category, GroupMailCategory)
            assert isinstance(category.id, int)
            assert category.id > 0
            assert isinstance(category.title, str)
            assert category.description is None or isinstance(category.description, str)
            assert category.active in (0, 1)
            assert isinstance(category.languages, list)
            assert isinstance(category.relatedMailCampaigns, list)

            # Validate structure if present
            for lang in category.languages:
                assert isinstance(lang, dict)
            for campaign in category.relatedMailCampaigns:
                assert isinstance(campaign, dict)

        print(f"[OK] Listed {len(categories)} group mail categories successfully")


@pytest.mark.asyncio
@my_vcr.use_cassette(
    "test_group_mail_categories_integration/test_get_group_mail_category_real_response.yaml"
)
async def test_get_group_mail_category_real_response():
    """
    Test getting a single group mail category with real API response structure.

    Validates full GroupMailCategory model.

    Cassette: tests/cassettes/integration/test_group_mail_categories_integration/test_get_group_mail_category_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        # First list to get a valid category ID
        categories = await upsales.group_mail_categories.list(limit=1)

        if len(categories) == 0:
            pytest.skip("No group mail categories found in the system")

        category_id = categories[0].id

        # Now get the specific category
        category = await upsales.group_mail_categories.get(category_id)

        assert isinstance(category, GroupMailCategory)
        assert category.id == category_id
        assert isinstance(category.title, str)
        assert category.description is None or isinstance(category.description, str)
        assert category.active in (0, 1)
        assert isinstance(category.languages, list)
        assert isinstance(category.relatedMailCampaigns, list)

        # Validate structure if present
        for lang in category.languages:
            assert isinstance(lang, dict)
            if "language" in lang:
                assert isinstance(lang["language"], str)
        for campaign in category.relatedMailCampaigns:
            assert isinstance(campaign, dict)
            if "entity" in campaign:
                assert isinstance(campaign["entity"], str)

        print(f"[OK] Got category {category.id}: {category.title}")


@pytest.mark.asyncio
@my_vcr.use_cassette(
    "test_group_mail_categories_integration/test_group_mail_category_computed_field.yaml"
)
async def test_group_mail_category_computed_field():
    """
    Test computed field is_active works correctly with real API data.

    Validates is_active computed property.

    Cassette: tests/cassettes/integration/test_group_mail_categories_integration/test_group_mail_category_computed_field.yaml
    """
    async with Upsales.from_env() as upsales:
        categories = await upsales.group_mail_categories.list(limit=5)

        if len(categories) == 0:
            pytest.skip("No group mail categories found in the system")

        category = categories[0]

        # Test computed field exists and returns correct type
        assert isinstance(category.is_active, bool)
        assert category.is_active == (category.active == 1)

        print(f"[OK] Computed field: is_active={category.is_active} (active={category.active})")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_group_mail_categories_integration/test_get_active_categories.yaml")
async def test_get_active_categories():
    """
    Test get_active() custom method with real API data.

    Validates custom resource method that filters active categories.

    Cassette: tests/cassettes/integration/test_group_mail_categories_integration/test_get_active_categories.yaml
    """
    async with Upsales.from_env() as upsales:
        active_categories = await upsales.group_mail_categories.get_active()

        assert isinstance(active_categories, list)

        if len(active_categories) == 0:
            pytest.skip("No active group mail categories found in the system")

        # Verify all returned categories are active
        for category in active_categories:
            assert isinstance(category, GroupMailCategory)
            assert category.active == 1
            assert category.is_active is True

        print(f"[OK] Found {len(active_categories)} active categories")


@pytest.mark.asyncio
@my_vcr.use_cassette(
    "test_group_mail_categories_integration/test_group_mail_category_languages.yaml"
)
async def test_group_mail_category_languages():
    """
    Test languages field parsing with real API data.

    Validates that languages list is properly parsed.

    Cassette: tests/cassettes/integration/test_group_mail_categories_integration/test_group_mail_category_languages.yaml
    """
    async with Upsales.from_env() as upsales:
        categories = await upsales.group_mail_categories.list(limit=20)

        if len(categories) == 0:
            pytest.skip("No group mail categories found in the system")

        # Find a category with languages
        category_with_languages = None
        for category in categories:
            if category.languages:
                category_with_languages = category
                break

        if category_with_languages:
            assert isinstance(category_with_languages.languages, list)
            for lang in category_with_languages.languages:
                assert isinstance(lang, dict)
                # Validate expected structure
                if "language" in lang:
                    assert isinstance(lang["language"], str)
                if "title" in lang:
                    assert isinstance(lang["title"], str)
                if "description" in lang:
                    assert isinstance(lang["description"], str)

            print(
                f"[OK] Languages validated: {len(category_with_languages.languages)} language configs found"
            )
        else:
            print("[SKIP] No categories with languages found")


@pytest.mark.asyncio
@my_vcr.use_cassette(
    "test_group_mail_categories_integration/test_group_mail_category_related_campaigns.yaml"
)
async def test_group_mail_category_related_campaigns():
    """
    Test relatedMailCampaigns field parsing with real API data.

    Validates that related campaign IDs are properly parsed.

    Cassette: tests/cassettes/integration/test_group_mail_categories_integration/test_group_mail_category_related_campaigns.yaml
    """
    async with Upsales.from_env() as upsales:
        categories = await upsales.group_mail_categories.list(limit=20)

        if len(categories) == 0:
            pytest.skip("No group mail categories found in the system")

        # Find a category with related campaigns
        category_with_campaigns = None
        for category in categories:
            if category.relatedMailCampaigns:
                category_with_campaigns = category
                break

        if category_with_campaigns:
            assert isinstance(category_with_campaigns.relatedMailCampaigns, list)
            for campaign in category_with_campaigns.relatedMailCampaigns:
                assert isinstance(campaign, dict)
                # Validate expected structure (entity + value)
                if "entity" in campaign:
                    assert isinstance(campaign["entity"], str)
                    assert campaign["entity"] in ("MailCampaign", "Flow")
                if "value" in campaign:
                    assert isinstance(campaign["value"], dict)
                    assert "id" in campaign["value"]

            print(
                f"[OK] Related campaigns validated: {len(category_with_campaigns.relatedMailCampaigns)} campaigns found"
            )
        else:
            print("[SKIP] No categories with related campaigns found")
