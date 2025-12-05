"""
Integration tests for ListView model with real API responses.

Uses VCR.py to record API responses on first run, then replay them.
Validates that our Pydantic v2 models correctly parse real API data.

To record cassettes:
    uv run pytest tests/integration/test_list_views_integration.py -v

To re-record (delete cassette first):
    rm -r tests/cassettes/integration/test_list_views_integration/
    uv run pytest tests/integration/test_list_views_integration.py -v
"""

import pytest
import vcr

from upsales import Upsales
from upsales.models.list_views import ListView

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
@my_vcr.use_cassette("test_list_views_integration/test_list_account_views.yaml")
async def test_list_account_views():
    """
    Test listing account list views with real API response structure.

    Validates that ListView model correctly parses real API data for account views.

    Cassette: tests/cassettes/integration/test_list_views_integration/test_list_account_views.yaml
    """
    async with Upsales.from_env() as upsales:
        views = await upsales.list_views.list("account", limit=5)

        assert isinstance(views, list)

        if len(views) == 0:
            pytest.skip("No account list views found in the system")

        for view in views:
            assert isinstance(view, ListView)
            assert isinstance(view.id, (int, str))
            if isinstance(view.id, int):
                assert view.id > 0
            assert isinstance(view.title, str)
            assert view.listType == "account"

            # Validate read-only fields are present
            if view.regDate is not None:
                assert isinstance(view.regDate, str)
            if view.modDate is not None:
                assert isinstance(view.modDate, str)

        print(f"[OK] Listed {len(views)} account list views successfully")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_list_views_integration/test_list_contact_views.yaml")
async def test_list_contact_views():
    """
    Test listing contact list views with real API response structure.

    Validates that ListView model correctly parses real API data for contact views.

    Cassette: tests/cassettes/integration/test_list_views_integration/test_list_contact_views.yaml
    """
    async with Upsales.from_env() as upsales:
        views = await upsales.list_views.list("contact", limit=5)

        assert isinstance(views, list)

        if len(views) == 0:
            pytest.skip("No contact list views found in the system")

        for view in views:
            assert isinstance(view, ListView)
            assert isinstance(view.id, (int, str))
            if isinstance(view.id, int):
                assert view.id > 0
            assert isinstance(view.title, str)
            assert view.listType == "contact"

        print(f"[OK] Listed {len(views)} contact list views successfully")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_list_views_integration/test_list_order_views.yaml")
async def test_list_order_views():
    """
    Test listing order list views with real API response structure.

    Validates that ListView model correctly parses real API data for order views.

    Cassette: tests/cassettes/integration/test_list_views_integration/test_list_order_views.yaml
    """
    async with Upsales.from_env() as upsales:
        views = await upsales.list_views.list("order", limit=5)

        assert isinstance(views, list)

        if len(views) == 0:
            pytest.skip("No order list views found in the system")

        for view in views:
            assert isinstance(view, ListView)
            assert isinstance(view.id, (int, str))
            if isinstance(view.id, int):
                assert view.id > 0
            assert isinstance(view.title, str)
            assert view.listType == "order"

        print(f"[OK] Listed {len(views)} order list views successfully")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_list_views_integration/test_get_list_view.yaml")
async def test_get_list_view():
    """
    Test getting a single list view with real API response structure.

    Validates full ListView model including all fields.

    Cassette: tests/cassettes/integration/test_list_views_integration/test_get_list_view.yaml
    """
    async with Upsales.from_env() as upsales:
        # First list to get a valid view ID
        views = await upsales.list_views.list("account", limit=10)

        if len(views) == 0:
            pytest.skip("No account list views found in the system")

        # Find a custom view (with int ID) to test GET endpoint
        custom_view = None
        for v in views:
            if isinstance(v.id, int):
                custom_view = v
                break

        if custom_view is None:
            pytest.skip("No custom list views with int ID found (only standard views exist)")

        view_id = custom_view.id
        entity = custom_view.listType

        # Now get the specific view
        view = await upsales.list_views.get(entity, view_id)

        assert isinstance(view, ListView)
        assert view.id == view_id
        assert isinstance(view.title, str)
        assert view.listType == entity

        print(f"[OK] Got list view {view.id}: {view.title} (entity: {view.listType})")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_list_views_integration/test_list_view_computed_fields.yaml")
async def test_list_view_computed_fields():
    """
    Test computed fields work correctly with real API data.

    Validates is_default computed property.

    Cassette: tests/cassettes/integration/test_list_views_integration/test_list_view_computed_fields.yaml
    """
    async with Upsales.from_env() as upsales:
        views = await upsales.list_views.list("account", limit=10)

        if len(views) == 0:
            pytest.skip("No account list views found in the system")

        # Find views with different default status
        found_default = False
        found_non_default = False

        for view in views:
            # Test computed field exists and returns correct type
            assert isinstance(view.is_default, bool)
            assert view.is_default == (view.default is True)

            if view.is_default:
                found_default = True
                print(f"  [OK] Default view: {view.title} (id={view.id})")
            else:
                found_non_default = True

        print(
            f"\n[OK] Computed field is_default validated - "
            f"found default:{found_default}, non-default:{found_non_default}"
        )


@pytest.mark.asyncio
@my_vcr.use_cassette("test_list_views_integration/test_list_view_configuration_fields.yaml")
async def test_list_view_configuration_fields():
    """
    Test that configuration fields (columns, sorting, filters, etc.) parse correctly.

    Validates that complex nested structures in view configuration work properly.

    Cassette: tests/cassettes/integration/test_list_views_integration/test_list_view_configuration_fields.yaml
    """
    async with Upsales.from_env() as upsales:
        views = await upsales.list_views.list("account", limit=10)

        if len(views) == 0:
            pytest.skip("No account list views found in the system")

        # Check various configuration fields across views
        found_columns = False
        found_sorting = False
        found_filters = False
        found_grouping = False

        for view in views:
            if view.columns is not None and len(view.columns) > 0:
                found_columns = True
                assert isinstance(view.columns, list)
                print(f"  [OK] columns: {len(view.columns)} columns configured")

            if view.sorting is not None and len(view.sorting) > 0:
                found_sorting = True
                assert isinstance(view.sorting, list)
                print(f"  [OK] sorting: {len(view.sorting)} sort rules configured")

            if view.filters is not None and len(view.filters) > 0:
                found_filters = True
                assert isinstance(view.filters, list)
                print(f"  [OK] filters: {len(view.filters)} filters configured")

            if view.grouping is not None:
                found_grouping = True
                assert isinstance(view.grouping, str)
                print(f"  [OK] grouping: {view.grouping}")

        print(
            f"\n[OK] Configuration fields found - columns:{found_columns}, "
            f"sorting:{found_sorting}, filters:{found_filters}, grouping:{found_grouping}"
        )


@pytest.mark.asyncio
@my_vcr.use_cassette("test_list_views_integration/test_list_all_views.yaml")
async def test_list_all_views():
    """
    Test listing all list views with automatic pagination.

    Validates list_all method correctly handles pagination.

    Cassette: tests/cassettes/integration/test_list_views_integration/test_list_all_views.yaml
    """
    async with Upsales.from_env() as upsales:
        all_views = await upsales.list_views.list_all("account")

        assert isinstance(all_views, list)

        if len(all_views) == 0:
            pytest.skip("No account list views found in the system")

        for view in all_views:
            assert isinstance(view, ListView)
            assert view.listType == "account"

        print(f"[OK] Listed all {len(all_views)} account list views with automatic pagination")
