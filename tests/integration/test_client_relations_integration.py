"""
Integration tests for ClientRelation model with real API responses.

Uses VCR.py to record API responses on first run, then replay.
Validates that ClientRelation model correctly parses real Upsales API data.

To record cassettes:
    uv run pytest tests/integration/test_client_relations_integration.py -v
"""

import pytest
import vcr

from upsales import Upsales
from upsales.exceptions import ServerError
from upsales.models.client_relations import ClientRelation

# Configure VCR for this test module
my_vcr = vcr.VCR(
    cassette_library_dir="tests/cassettes/integration",
    record_mode="once",  # Record once, then always replay
    match_on=["method", "scheme", "host", "port", "path", "query"],
    filter_headers=[("cookie", "REDACTED")],
    filter_post_data_parameters=[("password", "REDACTED")],
)


@pytest.mark.asyncio
@my_vcr.use_cassette("test_client_relations_integration/test_list_client_relations.yaml")
async def test_list_client_relations_real_response():
    """Test listing client relations with real API response structure."""
    async with Upsales.from_env() as upsales:
        try:
            relations = await upsales.client_relations.list(limit=10)
        except ServerError:
            pytest.skip("Client relations endpoint not available in test environment (500 error)")

        assert isinstance(relations, list)
        assert len(relations) <= 10

        if len(relations) == 0:
            pytest.skip("No client relations available in test environment")

        for relation in relations:
            assert isinstance(relation, ClientRelation)
            assert isinstance(relation.id, int)
            assert relation.id > 0
            # Required fields
            assert isinstance(relation.clientId, int)
            assert relation.clientId > 0
            assert isinstance(relation.relatedToClientId, int)
            assert relation.relatedToClientId > 0
            # Optional fields
            assert isinstance(relation.description, str)
            assert isinstance(relation.descriptionChildParent, str)

        print(f"[OK] Listed {len(relations)} client relations successfully")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_client_relations_integration/test_get_client_relation.yaml")
async def test_get_client_relation_real_response():
    """
    Test getting a single client relation with real API response structure.

    This test records the actual API response on first run, then
    replays it from cassette on future runs. Ensures our ClientRelation
    model correctly parses real Upsales API data.
    """
    async with Upsales.from_env() as upsales:
        # Get relations to find a valid ID
        try:
            relations = await upsales.client_relations.list(limit=1)
        except ServerError:
            pytest.skip("Client relations endpoint not available in test environment (500 error)")

        if len(relations) == 0:
            pytest.skip("No client relations available in test environment")

        relation_id = relations[0].id

        # Get single relation
        relation = await upsales.client_relations.get(relation_id)

        # Validate ClientRelation model
        assert isinstance(relation, ClientRelation)
        assert isinstance(relation.id, int)
        assert relation.id > 0

        # Validate frozen fields (read-only)
        assert hasattr(relation, "id")

        # Validate required fields
        assert isinstance(relation.clientId, int)
        assert relation.clientId > 0
        assert isinstance(relation.relatedToClientId, int)
        assert relation.relatedToClientId > 0

        # Validate optional fields
        assert isinstance(relation.description, str)
        assert isinstance(relation.descriptionChildParent, str)

        print(
            f"[OK] ClientRelation parsed successfully: "
            f"ID {relation.id}, {relation.clientId} -> {relation.relatedToClientId}"
        )


@pytest.mark.asyncio
@my_vcr.use_cassette("test_client_relations_integration/test_serialization.yaml")
async def test_client_relation_serialization_real_data():
    """
    Test to_api_dict() serialization with real client relation data.

    Validates that serialization excludes frozen fields using
    Pydantic v2 optimized serialization.
    """
    async with Upsales.from_env() as upsales:
        try:
            relations = await upsales.client_relations.list(limit=1)
        except ServerError:
            pytest.skip("Client relations endpoint not available in test environment (500 error)")

        if len(relations) == 0:
            pytest.skip("No client relations available in test environment")

        relation = relations[0]

        # Get API dict (should exclude frozen fields)
        api_dict = relation.to_api_dict()

        # Validate frozen fields excluded
        assert "id" not in api_dict or api_dict.get("id") is None

        # Should include updatable fields
        assert "clientId" in api_dict
        assert "relatedToClientId" in api_dict
        assert "description" in api_dict
        assert "descriptionChildParent" in api_dict

        # With overrides, should include changed fields
        api_dict_with_changes = relation.to_api_dict(
            description="Test description", descriptionChildParent="Test child to parent"
        )
        assert api_dict_with_changes["description"] == "Test description"
        assert api_dict_with_changes["descriptionChildParent"] == "Test child to parent"

        # Validate it's JSON serializable
        import json

        json_str = json.dumps(api_dict)  # Should not raise
        assert json_str

        print(f"[OK] Serialization validated for relation ID {relation.id}")
        print(f"[OK] API payload has {len(api_dict)} fields")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_client_relations_integration/test_get_by_client.yaml")
async def test_get_by_client_custom_method():
    """
    Test get_by_client() custom method with real data.

    Validates that custom methods work correctly with the client relations endpoint.
    """
    async with Upsales.from_env() as upsales:
        try:
            relations = await upsales.client_relations.list(limit=1)
        except ServerError:
            pytest.skip("Client relations endpoint not available in test environment (500 error)")

        if len(relations) == 0:
            pytest.skip("No client relations available in test environment")

        # Use the first relation's clientId to test
        test_client_id = relations[0].clientId

        # Get all relations for this client
        client_relations = await upsales.client_relations.get_by_client(test_client_id)

        assert isinstance(client_relations, list)
        # All should involve the test client as either clientId or relatedToClientId
        for relation in client_relations:
            assert (
                relation.clientId == test_client_id or relation.relatedToClientId == test_client_id
            )

        print(f"[OK] Found {len(client_relations)} relations for client {test_client_id}")


@pytest.mark.asyncio
@my_vcr.use_cassette("test_client_relations_integration/test_get_children.yaml")
async def test_get_children_custom_method():
    """
    Test get_children() custom method with real data.

    Validates that child relations can be filtered correctly.
    """
    async with Upsales.from_env() as upsales:
        try:
            relations = await upsales.client_relations.list(limit=1)
        except ServerError:
            pytest.skip("Client relations endpoint not available in test environment (500 error)")

        if len(relations) == 0:
            pytest.skip("No client relations available in test environment")

        # Use the first relation's clientId as parent
        parent_client_id = relations[0].clientId

        # Get child relations for this parent
        children = await upsales.client_relations.get_children(parent_client_id)

        assert isinstance(children, list)
        # All should have the parent as clientId
        for relation in children:
            assert relation.clientId == parent_client_id

        print(f"[OK] Found {len(children)} child relations for parent {parent_client_id}")
