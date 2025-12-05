"""
Integration tests for FormSubmit model with real API responses.

Uses VCR.py to record API responses on first run, then replay them.
Validates that our Pydantic v2 models correctly parse real API data.

To record cassettes:
    uv run pytest tests/integration/test_form_submits_integration.py -v

To re-record (delete cassette first):
    rm -r tests/cassettes/integration/test_form_submits_integration/
    uv run pytest tests/integration/test_form_submits_integration.py -v
"""

import pytest
import vcr

from upsales import Upsales
from upsales.models.form_submits import FormSubmit

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
@my_vcr.use_cassette("test_form_submits_integration/test_list_form_submits_real_response.yaml")
async def test_list_form_submits_real_response():
    """
    Test listing form submissions with real API response structure.

    Validates that FormSubmit model correctly parses real API data including
    nested objects like PartialForm, PartialContact, PartialCompany.

    Cassette: tests/cassettes/integration/test_form_submits_integration/test_list_form_submits_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        submissions = await upsales.form_submits.list(limit=5)

        assert isinstance(submissions, list)

        if len(submissions) == 0:
            pytest.skip("No form submissions found in the system")

        for submission in submissions:
            assert isinstance(submission, FormSubmit)
            assert isinstance(submission.id, int)
            assert submission.id > 0
            assert isinstance(submission.formId, int)

            # Validate read-only fields are present
            assert isinstance(submission.userRemovable, bool)
            assert isinstance(submission.userEditable, bool)
            assert isinstance(submission.brandId, int)
            assert isinstance(submission.regDate, str)

            # Validate updatable fields
            assert isinstance(submission.score, int)
            assert isinstance(submission.processedDate, str)
            assert isinstance(submission.fieldValues, list)

        print(f"[OK] Listed {len(submissions)} form submissions successfully")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_form_submits_integration/test_get_form_submit_real_response.yaml")
async def test_get_form_submit_real_response():
    """
    Test getting a single form submission with real API response structure.

    Validates full FormSubmit model including all nested objects.

    Cassette: tests/cassettes/integration/test_form_submits_integration/test_get_form_submit_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        # First list to get a valid submission ID
        submissions = await upsales.form_submits.list(limit=1)

        if len(submissions) == 0:
            pytest.skip("No form submissions found in the system")

        submission_id = submissions[0].id

        # Now get the specific submission
        submission = await upsales.form_submits.get(submission_id)

        assert isinstance(submission, FormSubmit)
        assert submission.id == submission_id
        assert isinstance(submission.formId, int)
        assert isinstance(submission.score, int)

        print(f"[OK] Got form submission {submission.id} for form {submission.formId}")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_form_submits_integration/test_form_submit_computed_fields.yaml")
async def test_form_submit_computed_fields():
    """
    Test computed fields work correctly with real API data.

    Validates is_removable and is_editable computed properties.

    Cassette: tests/cassettes/integration/test_form_submits_integration/test_form_submit_computed_fields.yaml
    """
    async with Upsales.from_env() as upsales:
        submissions = await upsales.form_submits.list(limit=5)

        if len(submissions) == 0:
            pytest.skip("No form submissions found in the system")

        submission = submissions[0]

        # Test computed fields exist and return correct types
        assert isinstance(submission.is_removable, bool)
        assert submission.is_removable == submission.userRemovable

        assert isinstance(submission.is_editable, bool)
        assert submission.is_editable == submission.userEditable

        print(
            f"[OK] Computed fields: is_removable={submission.is_removable}, "
            f"is_editable={submission.is_editable}"
        )


@pytest.mark.asyncio
@my_vcr.use_cassette("test_form_submits_integration/test_form_submit_nested_objects.yaml")
async def test_form_submit_nested_objects():
    """
    Test that nested objects (PartialForm, PartialContact, PartialCompany) parse correctly.

    These nested objects often have fewer fields than their full counterparts,
    so this validates our Partial models handle the actual API responses.

    Cassette: tests/cassettes/integration/test_form_submits_integration/test_form_submit_nested_objects.yaml
    """
    async with Upsales.from_env() as upsales:
        submissions = await upsales.form_submits.list(limit=10)

        if len(submissions) == 0:
            pytest.skip("No form submissions found in the system")

        # Check various nested objects across submissions
        found_form = False
        found_contact = False
        found_client = False
        found_visit = False

        for submission in submissions:
            if submission.form is not None:
                found_form = True
                # Can be PartialForm or dict
                if isinstance(submission.form, dict):
                    assert "id" in submission.form
                    print(f"  [OK] form (dict): id={submission.form.get('id')}")
                else:
                    assert hasattr(submission.form, "id")
                    print(f"  [OK] form: id={submission.form.id}")

            if submission.contact is not None:
                found_contact = True
                # Can be PartialContact or dict
                if isinstance(submission.contact, dict):
                    assert "id" in submission.contact
                    print(f"  [OK] contact (dict): id={submission.contact.get('id')}")
                else:
                    assert hasattr(submission.contact, "id")
                    print(f"  [OK] contact: id={submission.contact.id}")

            if submission.client is not None:
                found_client = True
                # Can be PartialCompany or dict
                if isinstance(submission.client, dict):
                    assert "id" in submission.client
                    print(f"  [OK] client (dict): id={submission.client.get('id')}")
                else:
                    assert hasattr(submission.client, "id")
                    print(f"  [OK] client: id={submission.client.id}")

            if submission.visit is not None:
                found_visit = True
                assert isinstance(submission.visit, dict)
                print(f"  [OK] visit: {submission.visit}")

        print(
            f"\n[OK] Nested objects found - form:{found_form}, contact:{found_contact}, "
            f"client:{found_client}, visit:{found_visit}"
        )


@pytest.mark.asyncio
@my_vcr.use_cassette("test_form_submits_integration/test_form_submit_field_values.yaml")
async def test_form_submit_field_values():
    """
    Test fieldValues structure with real API data.

    Validates that fieldValues list contains proper dictionaries with submission data.

    Cassette: tests/cassettes/integration/test_form_submits_integration/test_form_submit_field_values.yaml
    """
    async with Upsales.from_env() as upsales:
        submissions = await upsales.form_submits.list(limit=20)

        if len(submissions) == 0:
            pytest.skip("No form submissions found in the system")

        # Find a submission with field values
        submission_with_fields = None
        for submission in submissions:
            if submission.fieldValues:
                submission_with_fields = submission
                break

        if submission_with_fields:
            # Validate fieldValues structure
            assert isinstance(submission_with_fields.fieldValues, list)
            for field_value in submission_with_fields.fieldValues:
                assert isinstance(field_value, dict)

            print(f"[OK] Field values validated: {len(submission_with_fields.fieldValues)} fields")
        else:
            print("[SKIP] No submissions with field values found")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_form_submits_integration/test_get_by_form_id.yaml")
async def test_get_by_form_id():
    """
    Test getting submissions for a specific form.

    Validates custom resource method get_by_form_id().

    Cassette: tests/cassettes/integration/test_form_submits_integration/test_get_by_form_id.yaml
    """
    async with Upsales.from_env() as upsales:
        # First get any submission to find a valid form ID
        all_submissions = await upsales.form_submits.list(limit=5)

        if len(all_submissions) == 0:
            pytest.skip("No form submissions found in the system")

        form_id = all_submissions[0].formId

        # Now get submissions for that specific form
        form_submissions = await upsales.form_submits.get_by_form_id(form_id)

        assert isinstance(form_submissions, list)

        # All submissions should be for the requested form
        for submission in form_submissions:
            assert isinstance(submission, FormSubmit)
            assert submission.formId == form_id

        print(f"[OK] Found {len(form_submissions)} submissions for form {form_id}")
