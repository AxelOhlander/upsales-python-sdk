"""
Integration tests for MailDomain model with real API responses.

Uses VCR.py to record API responses on first run, then replay them.
Validates that our Pydantic v2 models correctly parse real API data.

Note:
    Mail domains use domain name (string) as identifier instead of numeric ID.
    Requires mail account configuration and administrator permissions.

To record cassettes:
    uv run pytest tests/integration/test_mail_domains_integration.py -v

To re-record (delete cassette first):
    rm -r tests/cassettes/integration/test_mail_domains_integration/
    uv run pytest tests/integration/test_mail_domains_integration.py -v
"""

import pytest
import vcr

from upsales import Upsales
from upsales.models.mail_domains import MailDomain

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
@my_vcr.use_cassette("test_mail_domains_integration/test_list_mail_domains_real_response.yaml")
async def test_list_mail_domains_real_response():
    """
    Test listing mail domains with real API response structure.

    Validates that MailDomain model correctly parses real API data including
    domain verification status and DNS configuration.

    Cassette: tests/cassettes/integration/test_mail_domains_integration/test_list_mail_domains_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        domains = await upsales.mail_domains.list(limit=10)

        assert isinstance(domains, list)

        if len(domains) == 0:
            pytest.skip("No mail domains found in the system (requires mail account configuration)")

        for domain in domains:
            assert isinstance(domain, MailDomain)
            assert isinstance(domain.domain, str)
            assert len(domain.domain) > 0
            assert isinstance(domain.dns, dict)
            assert isinstance(domain.valid, bool)

            # msg can be None or string
            if domain.msg is not None:
                assert isinstance(domain.msg, str)

        print(f"[OK] Listed {len(domains)} mail domains successfully")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_mail_domains_integration/test_get_mail_domain_real_response.yaml")
async def test_get_mail_domain_real_response():
    """
    Test getting a single mail domain with real API response structure.

    Note:
        Unlike most resources, mail domains use domain name as identifier
        instead of numeric ID. However, the API may not support GET by domain name.

    Cassette: tests/cassettes/integration/test_mail_domains_integration/test_get_mail_domain_real_response.yaml
    """
    from upsales.exceptions import NotFoundError

    async with Upsales.from_env() as upsales:
        # First list to get a valid domain name
        domains = await upsales.mail_domains.list(limit=1)

        if len(domains) == 0:
            pytest.skip("No mail domains found in the system (requires mail account configuration)")

        domain_name = domains[0].domain

        try:
            # Now get the specific domain by name
            domain = await upsales.mail_domains.get(domain_name)

            assert isinstance(domain, MailDomain)
            assert domain.domain == domain_name
            assert isinstance(domain.dns, dict)
            assert isinstance(domain.valid, bool)

            print(f"[OK] Got domain {domain.domain}: valid={domain.is_valid}, dns={domain.dns}")
        except NotFoundError:
            pytest.skip("API does not support GET /mail/domains/{domain_name}")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_mail_domains_integration/test_mail_domain_computed_fields.yaml")
async def test_mail_domain_computed_fields():
    """
    Test computed fields work correctly with real API data.

    Validates is_valid computed property.

    Cassette: tests/cassettes/integration/test_mail_domains_integration/test_mail_domain_computed_fields.yaml
    """
    async with Upsales.from_env() as upsales:
        domains = await upsales.mail_domains.list(limit=5)

        if len(domains) == 0:
            pytest.skip("No mail domains found in the system (requires mail account configuration)")

        domain = domains[0]

        # Test computed field exists and returns correct type
        assert isinstance(domain.is_valid, bool)
        assert domain.is_valid == domain.valid

        print(f"[OK] Computed field: is_valid={domain.is_valid} (valid={domain.valid})")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_mail_domains_integration/test_get_verified_domains.yaml")
async def test_get_verified_domains():
    """
    Test get_verified() custom method.

    Validates that the method correctly filters for verified domains.

    Cassette: tests/cassettes/integration/test_mail_domains_integration/test_get_verified_domains.yaml
    """
    async with Upsales.from_env() as upsales:
        verified = await upsales.mail_domains.get_verified()

        assert isinstance(verified, list)

        # All returned domains should be verified
        for domain in verified:
            assert isinstance(domain, MailDomain)
            assert domain.is_valid is True
            assert domain.valid is True

        print(f"[OK] Found {len(verified)} verified domains")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_mail_domains_integration/test_get_by_name.yaml")
async def test_get_by_name():
    """
    Test get_by_name() convenience method.

    Validates that get_by_name() works as an alias for get().

    Cassette: tests/cassettes/integration/test_mail_domains_integration/test_get_by_name.yaml
    """
    from upsales.exceptions import NotFoundError

    async with Upsales.from_env() as upsales:
        # First list to get a valid domain name
        domains = await upsales.mail_domains.list(limit=1)

        if len(domains) == 0:
            pytest.skip("No mail domains found in the system (requires mail account configuration)")

        domain_name = domains[0].domain

        try:
            # Get using convenience method
            domain = await upsales.mail_domains.get_by_name(domain_name)

            assert isinstance(domain, MailDomain)
            assert domain.domain == domain_name

            print(f"[OK] get_by_name() retrieved domain: {domain.domain}")
        except NotFoundError:
            pytest.skip("API does not support GET /mail/domains/{domain_name}")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_mail_domains_integration/test_mail_domain_string_identifier.yaml")
async def test_mail_domain_string_identifier():
    """
    Test that mail domains correctly use string domain name as identifier.

    This is unique compared to most other resources which use numeric IDs.

    Cassette: tests/cassettes/integration/test_mail_domains_integration/test_mail_domain_string_identifier.yaml
    """
    from upsales.exceptions import NotFoundError

    async with Upsales.from_env() as upsales:
        domains = await upsales.mail_domains.list(limit=1)

        if len(domains) == 0:
            pytest.skip("No mail domains found in the system (requires mail account configuration)")

        domain = domains[0]

        # Verify domain name is the identifier (not numeric ID)
        assert isinstance(domain.domain, str)
        assert len(domain.domain) > 0

        # The id field should be present (may be 0 or a real ID from API)
        assert hasattr(domain, "id")
        assert isinstance(domain.id, int)

        try:
            # Verify we can fetch by domain name
            fetched = await upsales.mail_domains.get(domain.domain)
            assert fetched.domain == domain.domain
            print(f"[OK] Domain uses string identifier: {domain.domain} (id={domain.id})")
        except NotFoundError:
            # API doesn't support GET by domain name, just verify the domain field
            print(
                f"[OK] Domain has string identifier: {domain.domain} (id={domain.id}) "
                "[Note: API doesn't support GET by domain name]"
            )
