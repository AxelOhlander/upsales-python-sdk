"""
Integration tests for MailTemplate model with real API responses.

Uses VCR.py to record API responses on first run, then replay them.
Validates that our Pydantic v2 models correctly parse real API data.

To record cassettes:
    uv run pytest tests/integration/test_mail_templates_integration.py -v

To re-record (delete cassette first):
    rm -r tests/cassettes/integration/test_mail_templates_integration/
    uv run pytest tests/integration/test_mail_templates_integration.py -v
"""

import pytest
import vcr

from upsales import Upsales
from upsales.models.mail_templates import MailTemplate

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
@my_vcr.use_cassette("test_mail_templates_integration/test_list_mail_templates_real_response.yaml")
async def test_list_mail_templates_real_response():
    """
    Test listing mail templates with real API response structure.

    Validates that MailTemplate model correctly parses real API data including
    field aliases (from, fromName, regDate, modDate, bodyJson, userEditable, userRemovable, usedCounter).

    Cassette: tests/cassettes/integration/test_mail_templates_integration/test_list_mail_templates_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        templates = await upsales.mail_templates.list(limit=5)

        assert isinstance(templates, list)

        if len(templates) == 0:
            pytest.skip("No mail templates found in the system")

        for template in templates:
            assert isinstance(template, MailTemplate)
            assert isinstance(template.id, int)
            assert template.id > 0
            assert isinstance(template.name, str)
            assert isinstance(template.subject, str)
            assert isinstance(template.body, str)

            # Validate read-only fields are present
            assert isinstance(template.reg_date, str)
            assert isinstance(template.mod_date, str)
            assert isinstance(template.version, int)

            # Validate required fields with aliases
            assert isinstance(template.from_address, str)
            assert isinstance(template.from_name, str)
            assert isinstance(template.user_editable, bool)
            assert isinstance(template.user_removable, bool)

            # Validate optional fields with aliases (can be None)
            assert template.body_json is None or isinstance(template.body_json, str)

            # Validate binary flags (0 or 1)
            assert template.active in (0, 1)
            assert template.private in (0, 1)

        print(f"[OK] Listed {len(templates)} mail templates successfully")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_mail_templates_integration/test_get_mail_template_real_response.yaml")
async def test_get_mail_template_real_response():
    """
    Test getting a single mail template with real API response structure.

    Validates full MailTemplate model including all fields and aliases.

    Cassette: tests/cassettes/integration/test_mail_templates_integration/test_get_mail_template_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        # First list to get a valid template ID
        templates = await upsales.mail_templates.list(limit=1)

        if len(templates) == 0:
            pytest.skip("No mail templates found in the system")

        template_id = templates[0].id

        # Now get the specific template
        template = await upsales.mail_templates.get(template_id)

        assert isinstance(template, MailTemplate)
        assert template.id == template_id
        assert isinstance(template.name, str)
        assert isinstance(template.subject, str)
        assert isinstance(template.body, str)

        # Validate field aliases work correctly
        assert hasattr(template, "from_address")
        assert hasattr(template, "from_name")
        assert hasattr(template, "body_json")
        assert hasattr(template, "user_editable")
        assert hasattr(template, "user_removable")
        assert hasattr(template, "reg_date")
        assert hasattr(template, "mod_date")

        print(f"[OK] Got mail template {template.id}: {template.name}")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_mail_templates_integration/test_mail_template_nested_user.yaml")
async def test_mail_template_nested_user():
    """
    Test that nested PartialUser parses correctly.

    The user field contains minimal user data (id, name) and should parse
    as PartialUser, not full User.

    Cassette: tests/cassettes/integration/test_mail_templates_integration/test_mail_template_nested_user.yaml
    """
    async with Upsales.from_env() as upsales:
        templates = await upsales.mail_templates.list(limit=10)

        if len(templates) == 0:
            pytest.skip("No mail templates found in the system")

        # Check for nested user object
        found_user = False

        for template in templates:
            if template.user is not None:
                found_user = True
                assert hasattr(template.user, "id")
                assert hasattr(template.user, "name")
                assert isinstance(template.user.id, int)
                assert isinstance(template.user.name, str)
                print(f"  [OK] user: id={template.user.id}, name={template.user.name}")

        if found_user:
            print("[OK] Nested PartialUser validated")
        else:
            print("[SKIP] No templates with user field found")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_mail_templates_integration/test_mail_template_computed_fields.yaml")
async def test_mail_template_computed_fields():
    """
    Test computed fields work correctly with real API data.

    Validates is_active, is_private, is_editable, is_removable, has_attachments,
    and attachment_count computed properties.

    Cassette: tests/cassettes/integration/test_mail_templates_integration/test_mail_template_computed_fields.yaml
    """
    async with Upsales.from_env() as upsales:
        templates = await upsales.mail_templates.list(limit=5)

        if len(templates) == 0:
            pytest.skip("No mail templates found in the system")

        template = templates[0]

        # Test computed fields exist and return correct types
        assert isinstance(template.is_active, bool)
        assert template.is_active == (template.active == 1)

        assert isinstance(template.is_private, bool)
        assert template.is_private == (template.private == 1)

        assert isinstance(template.is_editable, bool)
        assert template.is_editable == template.user_editable

        assert isinstance(template.is_removable, bool)
        assert template.is_removable == template.user_removable

        assert isinstance(template.has_attachments, bool)
        assert template.has_attachments == (len(template.attachments) > 0)

        assert isinstance(template.attachment_count, int)
        assert template.attachment_count == len(template.attachments)

        print(
            f"[OK] Computed fields: is_active={template.is_active}, "
            f"is_private={template.is_private}, is_editable={template.is_editable}, "
            f"is_removable={template.is_removable}, has_attachments={template.has_attachments}, "
            f"attachment_count={template.attachment_count}"
        )


@pytest.mark.asyncio
@my_vcr.use_cassette("test_mail_templates_integration/test_get_active_custom_method.yaml")
async def test_get_active_custom_method():
    """
    Test get_active() custom resource method.

    Validates that the custom method filters templates correctly.

    Cassette: tests/cassettes/integration/test_mail_templates_integration/test_get_active_custom_method.yaml
    """
    async with Upsales.from_env() as upsales:
        active_templates = await upsales.mail_templates.get_active()

        assert isinstance(active_templates, list)

        # Verify all returned templates are active
        for template in active_templates:
            assert isinstance(template, MailTemplate)
            assert template.is_active is True
            assert template.active == 1

        print(f"[OK] Found {len(active_templates)} active templates")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_mail_templates_integration/test_get_inactive_custom_method.yaml")
async def test_get_inactive_custom_method():
    """
    Test get_inactive() custom resource method.

    Validates that the custom method filters templates correctly.

    Cassette: tests/cassettes/integration/test_mail_templates_integration/test_get_inactive_custom_method.yaml
    """
    async with Upsales.from_env() as upsales:
        inactive_templates = await upsales.mail_templates.get_inactive()

        assert isinstance(inactive_templates, list)

        # Verify all returned templates are inactive
        for template in inactive_templates:
            assert isinstance(template, MailTemplate)
            assert template.is_active is False
            assert template.active == 0

        print(f"[OK] Found {len(inactive_templates)} inactive templates")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_mail_templates_integration/test_get_private_custom_method.yaml")
async def test_get_private_custom_method():
    """
    Test get_private() custom resource method.

    Validates that the custom method filters templates correctly.

    Cassette: tests/cassettes/integration/test_mail_templates_integration/test_get_private_custom_method.yaml
    """
    async with Upsales.from_env() as upsales:
        private_templates = await upsales.mail_templates.get_private()

        assert isinstance(private_templates, list)

        # Verify all returned templates are private
        for template in private_templates:
            assert isinstance(template, MailTemplate)
            assert template.is_private is True
            assert template.private == 1

        print(f"[OK] Found {len(private_templates)} private templates")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_mail_templates_integration/test_get_public_custom_method.yaml")
async def test_get_public_custom_method():
    """
    Test get_public() custom resource method.

    Validates that the custom method filters templates correctly.

    Cassette: tests/cassettes/integration/test_mail_templates_integration/test_get_public_custom_method.yaml
    """
    async with Upsales.from_env() as upsales:
        public_templates = await upsales.mail_templates.get_public()

        assert isinstance(public_templates, list)

        # Verify all returned templates are public
        for template in public_templates:
            assert isinstance(template, MailTemplate)
            assert template.is_private is False
            assert template.private == 0

        print(f"[OK] Found {len(public_templates)} public templates")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_mail_templates_integration/test_get_editable_custom_method.yaml")
async def test_get_editable_custom_method():
    """
    Test get_editable() custom resource method.

    Validates that the custom method filters templates correctly.

    Cassette: tests/cassettes/integration/test_mail_templates_integration/test_get_editable_custom_method.yaml
    """
    async with Upsales.from_env() as upsales:
        editable_templates = await upsales.mail_templates.get_editable()

        assert isinstance(editable_templates, list)

        # Verify all returned templates are editable
        for template in editable_templates:
            assert isinstance(template, MailTemplate)
            assert template.is_editable is True
            assert template.user_editable is True

        print(f"[OK] Found {len(editable_templates)} editable templates")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_mail_templates_integration/test_get_removable_custom_method.yaml")
async def test_get_removable_custom_method():
    """
    Test get_removable() custom resource method.

    Validates that the custom method filters templates correctly.

    Cassette: tests/cassettes/integration/test_mail_templates_integration/test_get_removable_custom_method.yaml
    """
    async with Upsales.from_env() as upsales:
        removable_templates = await upsales.mail_templates.get_removable()

        assert isinstance(removable_templates, list)

        # Verify all returned templates are removable
        for template in removable_templates:
            assert isinstance(template, MailTemplate)
            assert template.is_removable is True
            assert template.user_removable is True

        print(f"[OK] Found {len(removable_templates)} removable templates")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_mail_templates_integration/test_get_with_attachments_custom_method.yaml")
async def test_get_with_attachments_custom_method():
    """
    Test get_with_attachments() custom resource method.

    Validates that the custom method filters templates correctly.

    Cassette: tests/cassettes/integration/test_mail_templates_integration/test_get_with_attachments_custom_method.yaml
    """
    async with Upsales.from_env() as upsales:
        templates_with_attachments = await upsales.mail_templates.get_with_attachments()

        assert isinstance(templates_with_attachments, list)

        # Verify all returned templates have attachments
        for template in templates_with_attachments:
            assert isinstance(template, MailTemplate)
            assert template.has_attachments is True
            assert len(template.attachments) > 0

        print(f"[OK] Found {len(templates_with_attachments)} templates with attachments")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_mail_templates_integration/test_get_by_name_custom_method.yaml")
async def test_get_by_name_custom_method():
    """
    Test get_by_name() custom resource method.

    Validates that the custom method finds templates by name.

    Cassette: tests/cassettes/integration/test_mail_templates_integration/test_get_by_name_custom_method.yaml
    """
    async with Upsales.from_env() as upsales:
        # First get a template to know a valid name
        templates = await upsales.mail_templates.list(limit=1)

        if len(templates) == 0:
            pytest.skip("No mail templates found in the system")

        template_name = templates[0].name

        # Now search by name
        found_template = await upsales.mail_templates.get_by_name(template_name)

        if found_template:
            assert isinstance(found_template, MailTemplate)
            assert found_template.name.lower() == template_name.lower()
            print(f"[OK] Found template by name: {found_template.name}")
        else:
            print(f"[SKIP] Template '{template_name}' not found")
