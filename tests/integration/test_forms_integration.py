"""
Integration tests for Form model with real API responses.

Uses VCR.py to record API responses on first run, then replay them.
Validates that our Pydantic v2 models correctly parse real API data.

To record cassettes:
    uv run pytest tests/integration/test_forms_integration.py -v

To re-record (delete cassette first):
    rm tests/cassettes/integration/test_forms_integration/*.yaml
    uv run pytest tests/integration/test_forms_integration.py -v
"""

import pytest
import vcr

from upsales import Upsales
from upsales.models.forms import Form

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
@my_vcr.use_cassette("test_forms_integration/test_get_form_real_response.yaml")
async def test_get_form_real_response():
    """
    Test getting a form with real API response structure.

    This test records the actual API response on first run, then
    replays it from cassette on future runs. This ensures our Form
    model correctly parses real Upsales API data.

    Cassette: tests/cassettes/integration/test_forms_integration/test_get_form_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        # Get a real form (or replay from cassette)
        forms = await upsales.forms.list(limit=1)

        assert len(forms) > 0, "Should have at least one form"
        form = forms[0]

        # Validate Form model with Pydantic v2 features
        assert isinstance(form, Form)
        assert isinstance(form.id, int)
        assert isinstance(form.title, str)
        assert isinstance(form.name, str)
        assert form.name  # Name should not be empty (NonEmptyStr validator)

        # Validate BinaryFlag fields (0 or 1)
        assert form.redirect in (0, 1)
        assert form.showTitle in (0, 1)
        assert form.isArchived in (0, 1)

        # Validate read-only fields
        assert isinstance(form.uuid, str)
        assert isinstance(form.submits, int)
        assert form.submits >= 0
        assert isinstance(form.views, int)
        assert form.views >= 0
        assert isinstance(form.userEditable, bool)
        assert isinstance(form.userRemovable, bool)

        # Validate computed fields
        assert isinstance(form.is_archived, bool)
        assert isinstance(form.has_submissions, bool)
        assert isinstance(form.submission_count, int)
        assert isinstance(form.view_count, int)

        # Validate fields structure
        assert isinstance(form.fields, list)
        assert isinstance(form.actions, list)

        print(
            f"[OK] Form parsed successfully: {form.title} (ID: {form.id}, Submissions: {form.submission_count})"
        )


@pytest.mark.asyncio
@my_vcr.use_cassette("test_forms_integration/test_list_forms_real_response.yaml")
async def test_list_forms_real_response():
    """
    Test listing forms with real API response.

    Validates that list responses correctly parse and return multiple Form objects.

    Cassette: tests/cassettes/integration/test_forms_integration/test_list_forms_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        # List forms (or replay from cassette)
        forms = await upsales.forms.list(limit=10)

        assert isinstance(forms, list)
        assert all(isinstance(f, Form) for f in forms)

        if len(forms) > 0:
            # Validate first form
            form = forms[0]
            assert form.id > 0
            assert form.title
            assert form.name
            assert form.isArchived in (0, 1)

            print(f"[OK] Listed {len(forms)} forms successfully")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_forms_integration/test_form_computed_fields.yaml")
async def test_form_computed_fields():
    """
    Test computed fields work with real data.

    Validates that computed properties (is_archived, has_submissions, etc.)
    return correct values based on actual API data.

    Cassette: tests/cassettes/integration/test_forms_integration/test_form_computed_fields.yaml
    """
    async with Upsales.from_env() as upsales:
        forms = await upsales.forms.list(limit=5)

        for form in forms:
            # Test computed field: is_archived
            if form.isArchived == 1:
                assert form.is_archived is True
            else:
                assert form.is_archived is False

            # Test computed field: has_submissions
            if form.submits > 0:
                assert form.has_submissions is True
            else:
                assert form.has_submissions is False

            # Test computed field: submission_count
            assert form.submission_count == form.submits

            # Test computed field: view_count
            assert form.view_count == form.views

        print(f"[OK] Computed fields validated for {len(forms)} forms")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_forms_integration/test_form_custom_methods.yaml")
async def test_form_custom_methods():
    """
    Test custom resource methods with real data.

    Validates get_active(), get_archived(), get_with_submissions(), get_by_name(),
    and get_by_title() methods work correctly with actual API responses.

    Cassette: tests/cassettes/integration/test_forms_integration/test_form_custom_methods.yaml
    """
    async with Upsales.from_env() as upsales:
        # Test get_active()
        active_forms = await upsales.forms.get_active()
        assert isinstance(active_forms, list)
        assert all(not f.is_archived for f in active_forms)

        # Test get_archived()
        archived_forms = await upsales.forms.get_archived()
        assert isinstance(archived_forms, list)
        assert all(f.is_archived for f in archived_forms)

        # Test get_with_submissions()
        forms_with_submissions = await upsales.forms.get_with_submissions()
        assert isinstance(forms_with_submissions, list)
        assert all(f.has_submissions for f in forms_with_submissions)
        assert all(f.submits > 0 for f in forms_with_submissions)

        # Test get_by_name() with first active form
        if len(active_forms) > 0:
            first_form = active_forms[0]
            found_form = await upsales.forms.get_by_name(first_form.name)
            assert found_form is not None
            assert found_form.id == first_form.id
            assert found_form.name == first_form.name

        # Test get_by_title() with first active form
        if len(active_forms) > 0:
            first_form = active_forms[0]
            found_form = await upsales.forms.get_by_title(first_form.title)
            assert found_form is not None
            assert found_form.id == first_form.id
            assert found_form.title == first_form.title

        print(
            f"[OK] Custom methods validated: {len(active_forms)} active, {len(archived_forms)} archived, {len(forms_with_submissions)} with submissions"
        )
