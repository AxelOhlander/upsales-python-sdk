"""Unit tests for UserDefinedObjectDefinitionsResource.

This endpoint only supports POST (create) and DELETE operations.
GET and UPDATE operations are not available.
"""

import pytest

from upsales.exceptions import NotFoundError
from upsales.models.user_defined_object_definition import (
    PartialUserDefinedObjectDefinition,
    UserDefinedObjectDefinition,
)
from upsales.resources.user_defined_object_definition import (
    UserDefinedObjectDefinitionsResource,
)


class TestUserDefinedObjectDefinitionsResource:
    """Test suite for UserDefinedObjectDefinitionsResource."""

    @pytest.fixture
    def resource(self, client):
        """Create a UserDefinedObjectDefinitionsResource instance."""
        return UserDefinedObjectDefinitionsResource(client.http)

    @pytest.fixture
    def sample_definition(self):
        """Sample definition data."""
        return {
            "id": 1,
            "name": "Custom Entity",
            "description": "A custom entity type",
            "fields": [
                {"name": "field1", "type": "string"},
                {"name": "field2", "type": "number"},
            ],
        }

    @pytest.mark.asyncio
    async def test_create_definition(self, resource, sample_definition, httpx_mock):
        """Test creating a new user-defined object definition."""
        httpx_mock.add_response(json={"error": None, "data": sample_definition}, status_code=201)

        result = await resource.create(
            name="Custom Entity",
            description="A custom entity type",
            fields=[
                {"name": "field1", "type": "string"},
                {"name": "field2", "type": "number"},
            ],
        )

        assert isinstance(result, UserDefinedObjectDefinition)
        assert result.id == 1
        assert result.name == "Custom Entity"
        assert result.description == "A custom entity type"
        assert len(result.fields) == 2

    @pytest.mark.asyncio
    async def test_delete_definition(self, resource, httpx_mock):
        """Test deleting a user-defined object definition."""
        httpx_mock.add_response(json={"error": None, "data": {}}, status_code=200)

        await resource.delete(1)

        # Verify the request was made
        request = httpx_mock.get_requests()[0]
        assert "/userDefinedDefinition/1" in str(request.url)
        assert request.method == "DELETE"

    @pytest.mark.asyncio
    async def test_delete_nonexistent(self, resource, httpx_mock):
        """Test deleting a non-existent definition raises NotFoundError."""
        httpx_mock.add_response(json={"error": "Not found", "data": None}, status_code=404)

        with pytest.raises(NotFoundError):
            await resource.delete(999)

    @pytest.mark.asyncio
    async def test_model_to_partial(self, sample_definition):
        """Test converting full model to partial."""
        full = UserDefinedObjectDefinition(**sample_definition)
        partial = PartialUserDefinedObjectDefinition(id=full.id, name=full.name)

        assert partial.id == full.id
        assert partial.name == full.name

    @pytest.mark.asyncio
    async def test_model_validates_fields(self, sample_definition):
        """Test model validation of fields."""
        # Valid definition
        definition = UserDefinedObjectDefinition(**sample_definition)
        assert definition.id == 1
        assert definition.name == "Custom Entity"

        # With None fields (all optional except id)
        minimal = UserDefinedObjectDefinition(id=2)
        assert minimal.id == 2
        assert minimal.name is None
        assert minimal.description is None
        assert minimal.fields is None

    @pytest.mark.asyncio
    async def test_edit_not_supported(self, sample_definition):
        """Test that edit() raises NotImplementedError."""
        definition = UserDefinedObjectDefinition(**sample_definition)

        with pytest.raises(NotImplementedError) as exc:
            await definition.edit(name="New Name")

        assert "Update operations are not supported" in str(exc.value)

    @pytest.mark.asyncio
    async def test_partial_fetch_full_not_supported(self):
        """Test that fetch_full() raises NotImplementedError."""
        partial = PartialUserDefinedObjectDefinition(id=1, name="Test")

        with pytest.raises(NotImplementedError) as exc:
            await partial.fetch_full()

        assert "GET operations are not supported" in str(exc.value)

    @pytest.mark.asyncio
    async def test_partial_edit_not_supported(self):
        """Test that partial edit() raises NotImplementedError."""
        partial = PartialUserDefinedObjectDefinition(id=1, name="Test")

        with pytest.raises(NotImplementedError) as exc:
            await partial.edit(name="New Name")

        assert "Update operations are not supported" in str(exc.value)

    @pytest.mark.asyncio
    async def test_create_minimal_definition(self, resource, httpx_mock):
        """Test creating a definition with minimal fields."""
        minimal_def = {"id": 2, "name": "Minimal", "description": None, "fields": None}

        httpx_mock.add_response(json={"error": None, "data": minimal_def}, status_code=201)

        result = await resource.create(name="Minimal")

        assert isinstance(result, UserDefinedObjectDefinition)
        assert result.id == 2
        assert result.name == "Minimal"
        assert result.description is None
        assert result.fields is None

    @pytest.mark.asyncio
    async def test_resource_endpoint_path(self, resource):
        """Test that resource uses correct endpoint path."""
        assert resource._endpoint == "/userDefinedDefinition"

    @pytest.mark.asyncio
    async def test_frozen_id_field(self, sample_definition):
        """Test that id field is frozen and cannot be changed."""
        definition = UserDefinedObjectDefinition(**sample_definition)

        with pytest.raises(Exception):  # Pydantic ValidationError
            definition.id = 999

    @pytest.mark.asyncio
    async def test_model_dict_serialization(self, sample_definition):
        """Test model serialization to dict."""
        definition = UserDefinedObjectDefinition(**sample_definition)
        data = definition.model_dump()

        assert data["id"] == 1
        assert data["name"] == "Custom Entity"
        assert data["description"] == "A custom entity type"
        assert len(data["fields"]) == 2
