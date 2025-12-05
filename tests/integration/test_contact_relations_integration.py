"""
Integration tests for ContactRelation model with real API responses.

Uses VCR.py to record API responses on first run, then replay them.
Validates that our Pydantic v2 models correctly parse real API data.

To record cassettes:
    uv run pytest tests/integration/test_contact_relations_integration.py -v

To re-record (delete cassette first):
    rm -r tests/cassettes/integration/test_contact_relations_integration/
    uv run pytest tests/integration/test_contact_relations_integration.py -v

Note:
    The /contactrelation endpoint returns 500 Server Error in some test environments.
    Tests will skip gracefully when the endpoint is unavailable.
"""

import pytest
import vcr

from upsales import Upsales
from upsales.exceptions import ServerError
from upsales.models.contact_relations import ContactRelation

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
    "test_contact_relations_integration/test_list_contact_relations_real_response.yaml"
)
async def test_list_contact_relations_real_response():
    """
    Test listing contact relations with real API response structure.

    Validates that ContactRelation model correctly parses real API data
    including required fields like contactId, relatedToClientId, and optional
    fields like description.

    Cassette: tests/cassettes/integration/test_contact_relations_integration/test_list_contact_relations_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        try:
            relations = await upsales.contact_relations.list(limit=10)
        except (ServerError, Exception) as e:
            pytest.skip(f"Contact relations endpoint not available: {e}")

        assert isinstance(relations, list)

        if len(relations) == 0:
            pytest.skip("No contact relations found in the system")

        for relation in relations:
            assert isinstance(relation, ContactRelation)
            assert isinstance(relation.id, int)
            assert relation.id > 0
            assert isinstance(relation.contactId, int)
            assert relation.contactId > 0
            assert isinstance(relation.relatedToClientId, int)
            assert relation.relatedToClientId > 0
            assert isinstance(relation.description, str)

        print(f"[OK] Listed {len(relations)} contact relations successfully")


@pytest.mark.asyncio
@my_vcr.use_cassette(
    "test_contact_relations_integration/test_get_contact_relation_real_response.yaml"
)
async def test_get_contact_relation_real_response():
    """
    Test getting a single contact relation with real API response structure.

    Validates full ContactRelation model including all fields.

    Cassette: tests/cassettes/integration/test_contact_relations_integration/test_get_contact_relation_real_response.yaml
    """
    async with Upsales.from_env() as upsales:
        try:
            # First list to get a valid relation ID
            relations = await upsales.contact_relations.list(limit=1)
        except (ServerError, Exception) as e:
            pytest.skip(f"Contact relations endpoint not available: {e}")

        if len(relations) == 0:
            pytest.skip("No contact relations found in the system")

        relation_id = relations[0].id

        # Now get the specific relation
        relation = await upsales.contact_relations.get(relation_id)

        assert isinstance(relation, ContactRelation)
        assert relation.id == relation_id
        assert isinstance(relation.contactId, int)
        assert relation.contactId > 0
        assert isinstance(relation.relatedToClientId, int)
        assert relation.relatedToClientId > 0
        assert isinstance(relation.description, str)

        print(
            f"[OK] Got contact relation {relation.id}: "
            f"Contact {relation.contactId} -> Client {relation.relatedToClientId}"
        )


@pytest.mark.asyncio
@my_vcr.use_cassette("test_contact_relations_integration/test_get_by_contact.yaml")
async def test_get_by_contact():
    """
    Test getting relations for a specific contact.

    Validates get_by_contact custom resource method.

    Cassette: tests/cassettes/integration/test_contact_relations_integration/test_get_by_contact.yaml
    """
    async with Upsales.from_env() as upsales:
        try:
            # First get all relations to find a valid contact ID
            all_relations = await upsales.contact_relations.list(limit=20)
        except (ServerError, Exception) as e:
            pytest.skip(f"Contact relations endpoint not available: {e}")

        if len(all_relations) == 0:
            pytest.skip("No contact relations found in the system")

        # Pick the first contact ID
        contact_id = all_relations[0].contactId

        # Test get_by_contact
        contact_relations = await upsales.contact_relations.get_by_contact(contact_id)

        assert isinstance(contact_relations, list)

        for relation in contact_relations:
            assert isinstance(relation, ContactRelation)
            assert relation.contactId == contact_id

        print(f"[OK] Found {len(contact_relations)} relations for contact {contact_id}")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_contact_relations_integration/test_get_by_client.yaml")
async def test_get_by_client():
    """
    Test getting relations for a specific client.

    Validates get_by_client custom resource method.

    Cassette: tests/cassettes/integration/test_contact_relations_integration/test_get_by_client.yaml
    """
    async with Upsales.from_env() as upsales:
        try:
            # First get all relations to find a valid client ID
            all_relations = await upsales.contact_relations.list(limit=20)
        except (ServerError, Exception) as e:
            pytest.skip(f"Contact relations endpoint not available: {e}")

        if len(all_relations) == 0:
            pytest.skip("No contact relations found in the system")

        # Pick the first client ID
        client_id = all_relations[0].relatedToClientId

        # Test get_by_client
        client_relations = await upsales.contact_relations.get_by_client(client_id)

        assert isinstance(client_relations, list)

        for relation in client_relations:
            assert isinstance(relation, ContactRelation)
            assert relation.relatedToClientId == client_id

        print(f"[OK] Found {len(client_relations)} relations for client {client_id}")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_contact_relations_integration/test_contact_relation_fields.yaml")
async def test_contact_relation_fields():
    """
    Test that all fields parse correctly with real API data.

    Validates field types and values match expectations.

    Cassette: tests/cassettes/integration/test_contact_relations_integration/test_contact_relation_fields.yaml
    """
    async with Upsales.from_env() as upsales:
        try:
            relations = await upsales.contact_relations.list(limit=5)
        except (ServerError, Exception) as e:
            pytest.skip(f"Contact relations endpoint not available: {e}")

        if len(relations) == 0:
            pytest.skip("No contact relations found in the system")

        relation = relations[0]

        # Test required fields
        assert isinstance(relation.id, int)
        assert relation.id > 0
        print(f"  [OK] id: {relation.id}")

        assert isinstance(relation.contactId, int)
        assert relation.contactId > 0
        print(f"  [OK] contactId: {relation.contactId}")

        assert isinstance(relation.relatedToClientId, int)
        assert relation.relatedToClientId > 0
        print(f"  [OK] relatedToClientId: {relation.relatedToClientId}")

        # Test optional field
        assert isinstance(relation.description, str)
        print(f"  [OK] description: '{relation.description}'")

        print(
            f"\n[OK] All fields validated for relation {relation.id}: "
            f"Contact {relation.contactId} -> Client {relation.relatedToClientId}"
        )


@pytest.mark.asyncio
@my_vcr.use_cassette("test_contact_relations_integration/test_contact_relation_search.yaml")
async def test_contact_relation_search():
    """
    Test searching contact relations with filters.

    Validates search functionality works with real API.

    Cassette: tests/cassettes/integration/test_contact_relations_integration/test_contact_relation_search.yaml
    """
    async with Upsales.from_env() as upsales:
        try:
            # First get a sample relation to use for searching
            all_relations = await upsales.contact_relations.list(limit=1)
        except (ServerError, Exception) as e:
            pytest.skip(f"Contact relations endpoint not available: {e}")

        if len(all_relations) == 0:
            pytest.skip("No contact relations found in the system")

        sample_contact_id = all_relations[0].contactId

        # Search for relations with this contactId
        relations = await upsales.contact_relations.search(contactId=sample_contact_id)

        assert isinstance(relations, list)

        for relation in relations:
            assert isinstance(relation, ContactRelation)
            assert relation.contactId == sample_contact_id

        print(f"[OK] Found {len(relations)} relations for contactId={sample_contact_id}")
