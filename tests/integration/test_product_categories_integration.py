"""
Integration tests for ProductCategoriesResource using VCR.py.

Uses VCR.py to record API responses on first run, then replay them.
Validates that our Pydantic v2 models correctly parse real API data.

To record cassettes:
    uv run pytest tests/integration/test_product_categories_integration.py -v

To re-record (delete cassette first):
    rm tests/cassettes/integration/test_product_categories_integration/*.yaml
    uv run pytest tests/integration/test_product_categories_integration.py -v
"""

import pytest
import vcr

from upsales import Upsales
from upsales.models.product_categories import ProductCategory

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
@my_vcr.use_cassette("test_product_categories_integration/test_list_categories_real_response.yaml")
async def test_list_categories_real_response():
    """Test listing product categories with real API response."""
    async with Upsales.from_env() as upsales:
        categories = await upsales.product_categories.list_all()

        assert isinstance(categories, list)

        for category in categories:
            assert isinstance(category, ProductCategory)
            assert isinstance(category.id, int)
            assert isinstance(category.name, str)
            assert hasattr(category, "parentId")
            assert hasattr(category, "sortId")
            assert hasattr(category, "roles")

        print(f"[OK] Listed {len(categories)} product categories")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_product_categories_integration/test_get_category_real_response.yaml")
async def test_get_category_real_response():
    """Test getting a single product category with real API response."""
    async with Upsales.from_env() as upsales:
        # Get categories first to find a valid ID
        categories = await upsales.product_categories.list_all()

        if len(categories) == 0:
            pytest.skip("No product categories available for testing")

        category_id = categories[0].id
        category = await upsales.product_categories.get(category_id)

        assert isinstance(category, ProductCategory)
        assert category.id == category_id
        assert isinstance(category.name, str)

        print(f"[OK] Got category: {category.name} (ID: {category.id})")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_product_categories_integration/test_category_computed_fields.yaml")
async def test_category_computed_fields():
    """Test computed fields on product category model."""
    async with Upsales.from_env() as upsales:
        categories = await upsales.product_categories.list_all()

        if len(categories) == 0:
            pytest.skip("No product categories available for testing")

        found_root = False
        found_child = False
        found_with_roles = False

        for category in categories:
            # Test is_root computed field
            assert isinstance(category.is_root, bool)
            if category.is_root:
                assert category.parentId is None or category.parentId == 0
                found_root = True
            else:
                assert category.parentId is not None and category.parentId != 0
                found_child = True

            # Test has_roles computed field
            assert isinstance(category.has_roles, bool)
            if category.has_roles:
                assert len(category.roles) > 0
                found_with_roles = True

        print("[OK] Computed fields validated:")
        print(f"  - is_root: found_root={found_root}, found_child={found_child}")
        print(f"  - has_roles: {found_with_roles}")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_product_categories_integration/test_get_root_categories.yaml")
async def test_get_root_categories():
    """Test getting root categories (no parent)."""
    async with Upsales.from_env() as upsales:
        root_categories = await upsales.product_categories.get_root_categories()

        assert isinstance(root_categories, list)

        for category in root_categories:
            assert category.is_root
            assert category.parentId is None or category.parentId == 0

        print(f"[OK] Got {len(root_categories)} root categories")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_product_categories_integration/test_get_children.yaml")
async def test_get_children():
    """Test getting child categories of a parent."""
    async with Upsales.from_env() as upsales:
        # Get all categories first
        all_categories = await upsales.product_categories.list_all()

        if len(all_categories) == 0:
            pytest.skip("No product categories available for testing")

        # Find a category that might have children (try root categories first)
        root_categories = [c for c in all_categories if c.is_root]

        if root_categories:
            parent_id = root_categories[0].id
            children = await upsales.product_categories.get_children(parent_id)

            assert isinstance(children, list)
            for child in children:
                assert child.parentId == parent_id

            print(f"[OK] Got {len(children)} children for category ID {parent_id}")
        else:
            print("[SKIP] No root categories to test children")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_product_categories_integration/test_get_by_name.yaml")
async def test_get_by_name():
    """Test getting category by name."""
    async with Upsales.from_env() as upsales:
        # Get categories first to find a valid name
        categories = await upsales.product_categories.list_all()

        if len(categories) == 0:
            pytest.skip("No product categories available for testing")

        target_name = categories[0].name
        category = await upsales.product_categories.get_by_name(target_name)

        assert category is not None
        assert category.name.lower() == target_name.lower()

        # Test non-existent name
        not_found = await upsales.product_categories.get_by_name("NonExistentCategory12345")
        assert not_found is None

        print(f"[OK] Got category by name: {target_name}")
