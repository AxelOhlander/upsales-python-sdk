"""
Integration tests for NotificationSetting model with real API responses.

Uses VCR.py to record API responses on first run, then replay them.
Validates that our Pydantic v2 models correctly parse real API data.

To record cassettes:
    uv run pytest tests/integration/test_notification_settings_integration.py -v

To re-record (delete cassette first):
    rm -r tests/cassettes/integration/test_notification_settings_integration/
    uv run pytest tests/integration/test_notification_settings_integration.py -v
"""

import pytest
import vcr

from upsales import Upsales
from upsales.models.notification_settings import NotificationSetting

# Configure VCR for these tests
my_vcr = vcr.VCR(
    cassette_library_dir="tests/cassettes/integration",
    record_mode="once",
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
    "test_notification_settings_integration/test_list_notification_settings_real_response.yaml"
)
async def test_list_notification_settings_real_response():
    """
    Test listing notification_settings with real API response structure.

    Validates that NotificationSetting model correctly parses list responses.

    Cassette: tests/cassettes/integration/test_notification_settings_integration/test_list_notification_settings_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        items = await upsales.notification_settings.list(limit=10)

        assert isinstance(items, list)

        if len(items) == 0:
            pytest.skip("No notification_settings found in the system")

        for item in items:
            assert isinstance(item, NotificationSetting)
            assert isinstance(item.id, int)
            assert item.id > 0

        print(f"[OK] Listed {len(items)} notification_settings successfully")


@pytest.mark.asyncio
@my_vcr.use_cassette(
    "test_notification_settings_integration/test_get_notification_settings_real_response.yaml"
)
async def test_get_notification_settings_real_response():
    """
    Test getting a single notification_settings with real API response.

    Cassette: tests/cassettes/integration/test_notification_settings_integration/test_get_notification_settings_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        items = await upsales.notification_settings.list(limit=1)

        if len(items) == 0:
            pytest.skip("No notification_settings found in the system")

        item = await upsales.notification_settings.get(items[0].id)
        assert isinstance(item, NotificationSetting)
        assert item.id == items[0].id

        print(f"[OK] Got notification_settings ID={item.id} successfully")
