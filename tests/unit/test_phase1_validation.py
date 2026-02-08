"""Validation tests for Phase 1 detective findings.

Tests that the SDK correctly implements the endpoints and behavior
documented by the upsales-api-detective for Phase 1:
1. /notify/* endpoints (users, admins, all)
2. File upload resource (/file/upload)
3. UDO 1-4 resources (/userDefinedObjects/:nr)
4. Custom field search syntax (custom=eq:fieldId:value)
"""

import pytest
from pytest_httpx import HTTPXMock

from upsales.http import HTTPClient


# =============================================================================
# 1. Notify endpoints validation
# =============================================================================


class TestNotifyResource:
    """Validate /notify/* endpoints match detective findings.

    Detective found:
    - POST /notify/users (requires message, from, userIds)
    - POST /notify/admins (requires message, from)
    - POST /notify/all (requires message, from)
    - type: "info" (default) or "error"
    - from is mapped to action internally
    """

    @pytest.mark.asyncio
    async def test_send_to_users(self, httpx_mock: HTTPXMock):
        """Test sending notification to specific users."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/notify/users",
            method="POST",
            json={"error": None, "data": {"success": True}},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            from upsales.resources.notify import NotifyResource

            resource = NotifyResource(http)
            result = await resource.send_to_users(
                message="Your export is ready",
                from_name="Export Service",
                user_ids=[123, 456],
            )

            assert result["data"]["success"] is True

            # Verify the request body
            request = httpx_mock.get_requests()[0]
            import json

            body = json.loads(request.content)
            assert body["message"] == "Your export is ready"
            assert body["from"] == "Export Service"
            assert body["type"] == "info"
            assert body["userIds"] == [123, 456]

    @pytest.mark.asyncio
    async def test_send_to_users_error_type(self, httpx_mock: HTTPXMock):
        """Test sending error-type notification."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/notify/users",
            method="POST",
            json={"error": None, "data": {"success": True}},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            from upsales.resources.notify import NotifyResource

            resource = NotifyResource(http)
            await resource.send_to_users(
                message="Critical failure",
                from_name="Monitor",
                user_ids=[1],
                notification_type="error",
            )

            import json

            body = json.loads(httpx_mock.get_requests()[0].content)
            assert body["type"] == "error"

    @pytest.mark.asyncio
    async def test_send_to_admins(self, httpx_mock: HTTPXMock):
        """Test sending notification to all admins."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/notify/admins",
            method="POST",
            json={"error": None, "data": {"success": True}},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            from upsales.resources.notify import NotifyResource

            resource = NotifyResource(http)
            result = await resource.send_to_admins(
                message="System alert",
                from_name="Monitor",
                notification_type="error",
            )

            assert result["data"]["success"] is True

            import json

            body = json.loads(httpx_mock.get_requests()[0].content)
            assert body["message"] == "System alert"
            assert body["from"] == "Monitor"
            assert "userIds" not in body

    @pytest.mark.asyncio
    async def test_send_to_all(self, httpx_mock: HTTPXMock):
        """Test sending notification to all users."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/notify/all",
            method="POST",
            json={"error": None, "data": {"success": True}},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            from upsales.resources.notify import NotifyResource

            resource = NotifyResource(http)
            result = await resource.send_to_all(
                message="Maintenance in 1 hour",
                from_name="IT Department",
            )

            assert result["data"]["success"] is True

    @pytest.mark.asyncio
    async def test_send_with_entity_id(self, httpx_mock: HTTPXMock):
        """Test notification with entity linkage."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/notify/users",
            method="POST",
            json={"error": None, "data": {"success": True}},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            from upsales.resources.notify import NotifyResource

            resource = NotifyResource(http)
            await resource.send_to_users(
                message="Deal updated",
                from_name="CRM",
                user_ids=[1],
                entity_id="order_123",
            )

            import json

            body = json.loads(httpx_mock.get_requests()[0].content)
            assert body["entityId"] == "order_123"

    def test_notify_registered_on_client(self):
        """Test that notify resource is accessible on the Upsales client."""
        from upsales import Upsales

        upsales = Upsales(token="test_token")
        assert hasattr(upsales, "notify")
        assert hasattr(upsales.notify, "send_to_users")
        assert hasattr(upsales.notify, "send_to_admins")
        assert hasattr(upsales.notify, "send_to_all")


# =============================================================================
# 2. File upload resource validation
# =============================================================================


class TestFileUploadValidation:
    """Validate file upload resource matches detective findings.

    Detective found:
    - POST /file/upload (multipart/form-data)
    - private field sent as string "true"/"false"
    - Max 25MB file size
    - Response fields: id, userId, extension, type, filename, mimetype, private, size, entity, entityId, uploadDate
    """

    def test_file_upload_model_fields(self):
        """Verify FileUpload model has all fields from detective findings."""
        from upsales.models.file_upload import FileUpload

        fields = FileUpload.model_fields
        expected = [
            "id",
            "userId",
            "extension",
            "type",
            "filename",
            "mimetype",
            "private",
            "size",
            "entity",
            "entityId",
            "uploadDate",
        ]
        for field in expected:
            assert field in fields, f"Missing field: {field}"

    def test_file_upload_model_parses_response(self):
        """Verify FileUpload model can parse a typical API response."""
        from upsales.models.file_upload import FileUpload

        data = {
            "id": 12345,
            "userId": 1,
            "extension": "pdf",
            "type": "application/pdf",
            "filename": "document.pdf",
            "mimetype": "application/pdf",
            "private": 0,
            "size": 2500000,
            "entity": "Appointment",
            "entityId": 789,
            "uploadDate": "2024-01-15T10:30:00",
        }
        upload = FileUpload(**data)
        assert upload.id == 12345
        assert upload.filename == "document.pdf"
        assert upload.size_mb == 2.5
        assert upload.is_private is False

    def test_file_upload_resource_endpoint(self):
        """Verify endpoint path matches detective finding: /file/upload."""
        from unittest.mock import AsyncMock

        from upsales.resources.file_upload import FileUploadsResource

        mock_http = AsyncMock()
        resource = FileUploadsResource(mock_http)
        assert resource._endpoint == "/file/upload"

    @pytest.mark.asyncio
    async def test_file_upload_sends_private_as_string(self, httpx_mock: HTTPXMock):
        """Verify private field is sent as string 'true'/'false' per detective finding."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/file/upload",
            method="POST",
            json={
                "error": None,
                "data": {
                    "id": 1,
                    "userId": 1,
                    "extension": "pdf",
                    "type": "application/pdf",
                    "filename": "test.pdf",
                    "mimetype": "application/pdf",
                    "private": 1,
                    "size": 1000,
                    "entity": None,
                    "entityId": None,
                    "uploadDate": "2024-01-15",
                },
            },
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            from io import BytesIO

            from upsales.resources.file_upload import FileUploadsResource

            resource = FileUploadsResource(http)
            result = await resource.upload(
                file=BytesIO(b"test content"),
                filename="test.pdf",
                private=True,
            )

            assert result.id == 1
            # Verify the request sent private as string
            request = httpx_mock.get_requests()[0]
            # multipart form data - check that private is "true" string
            content = request.content.decode("utf-8", errors="replace")
            assert "true" in content  # private="true" in form data


# =============================================================================
# 3. UDO 1-4 resource validation
# =============================================================================


class TestUDOValidation:
    """Validate UDO resources match detective findings.

    Detective found:
    - Endpoint: /userDefinedObjects/:nr (nr=1-4)
    - Full CRUD: GET, POST, PUT, DELETE
    - Fields: notes, notes1-4, clientId, contactId, projectId, userId, roleId, custom, categories
    - Read-only: id, regDate, regTime, modDate, modTime
    - Custom fields via standard custom array format
    """

    @pytest.fixture
    def sample_udo_data(self):
        """Sample UDO data matching detective findings."""
        return {
            "id": 1,
            "notes": "Main notes",
            "notes1": "Extra notes 1",
            "notes2": None,
            "notes3": None,
            "notes4": None,
            "clientId": 100,
            "contactId": 200,
            "projectId": None,
            "userId": 5,
            "roleId": 2,
            "regDate": "2024-01-15",
            "regTime": "2024-01-15T10:00:00",
            "modDate": "2024-01-20",
            "modTime": "2024-01-20T14:30:00",
            "custom": [{"fieldId": 12345, "value": "test_value"}],
            "categories": [{"id": 1, "name": "Category A"}],
        }

    def test_udo_model_has_all_fields(self):
        """Verify UDO model has all fields from detective findings."""
        from upsales.models.user_defined_object_1 import UserDefinedObject1

        fields = UserDefinedObject1.model_fields
        expected_writable = [
            "notes",
            "notes1",
            "notes2",
            "notes3",
            "notes4",
            "clientId",
            "contactId",
            "projectId",
            "userId",
            "roleId",
            "custom",
            "categories",
        ]
        expected_readonly = ["id", "regDate", "regTime", "modDate", "modTime"]
        for field in expected_writable + expected_readonly:
            assert field in fields, f"Missing field: {field}"

    def test_udo_readonly_fields_are_frozen(self):
        """Verify read-only fields are marked frozen per detective findings."""
        from upsales.models.user_defined_object_1 import UserDefinedObject1

        frozen_fields = ["id", "regDate", "regTime", "modDate", "modTime"]
        for field_name in frozen_fields:
            field_info = UserDefinedObject1.model_fields[field_name]
            assert field_info.frozen is True, f"Field {field_name} should be frozen"

    def test_udo_parses_api_response(self, sample_udo_data):
        """Verify UDO model can parse a typical API response."""
        from upsales.models.user_defined_object_1 import UserDefinedObject1

        udo = UserDefinedObject1(**sample_udo_data)
        assert udo.id == 1
        assert udo.notes == "Main notes"
        assert udo.clientId == 100
        assert udo.contactId == 200
        assert udo.custom_fields[12345] == "test_value"

    def test_udo_resource_endpoint_paths(self):
        """Verify UDO resource endpoint paths match detective finding: /userDefinedObjects/:nr."""
        from unittest.mock import AsyncMock

        from upsales.resources.user_defined_object_1 import UserDefinedObject1Resource
        from upsales.resources.user_defined_object_2 import UserDefinedObject2Resource
        from upsales.resources.user_defined_object_3 import UserDefinedObject3Resource
        from upsales.resources.user_defined_object_4 import UserDefinedObject4Resource

        mock_http = AsyncMock()
        assert UserDefinedObject1Resource(mock_http)._endpoint == "/userDefinedObjects/1"
        assert UserDefinedObject2Resource(mock_http)._endpoint == "/userDefinedObjects/2"
        assert UserDefinedObject3Resource(mock_http)._endpoint == "/userDefinedObjects/3"
        assert UserDefinedObject4Resource(mock_http)._endpoint == "/userDefinedObjects/4"

    @pytest.mark.asyncio
    async def test_udo_create(self, httpx_mock: HTTPXMock, sample_udo_data):
        """Test creating a UDO object."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/userDefinedObjects/1",
            method="POST",
            json={"error": None, "data": sample_udo_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            from upsales.resources.user_defined_object_1 import UserDefinedObject1Resource

            resource = UserDefinedObject1Resource(http)
            result = await resource.create(notes="Main notes", clientId=100)

            assert result.id == 1
            assert result.notes == "Main notes"

    @pytest.mark.asyncio
    async def test_udo_get(self, httpx_mock: HTTPXMock, sample_udo_data):
        """Test getting a UDO object."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/userDefinedObjects/1/1",
            json={"error": None, "data": sample_udo_data},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            from upsales.resources.user_defined_object_1 import UserDefinedObject1Resource

            resource = UserDefinedObject1Resource(http)
            result = await resource.get(1)

            assert result.id == 1
            assert result.notes == "Main notes"
            assert result.custom_fields[12345] == "test_value"

    @pytest.mark.asyncio
    async def test_udo_update(self, httpx_mock: HTTPXMock, sample_udo_data):
        """Test updating a UDO object."""
        updated = {**sample_udo_data, "notes": "Updated notes"}
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/userDefinedObjects/1/1",
            method="PUT",
            json={"error": None, "data": updated},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            from upsales.resources.user_defined_object_1 import UserDefinedObject1Resource

            resource = UserDefinedObject1Resource(http)
            result = await resource.update(1, notes="Updated notes")

            assert result.notes == "Updated notes"

    @pytest.mark.asyncio
    async def test_udo_delete(self, httpx_mock: HTTPXMock):
        """Test deleting a UDO object."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/userDefinedObjects/1/1",
            method="DELETE",
            json={"error": None, "data": {"id": 1}},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            from upsales.resources.user_defined_object_1 import UserDefinedObject1Resource

            resource = UserDefinedObject1Resource(http)
            result = await resource.delete(1)

            assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_udo_custom_field_search(self, httpx_mock: HTTPXMock, sample_udo_data):
        """Test searching UDO objects by custom field per detective finding."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/userDefinedObjects/1?custom=eq%3A12345%3Atest_value&limit=100&offset=0",
            json={"error": None, "data": [sample_udo_data]},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            from upsales.resources.user_defined_object_1 import UserDefinedObject1Resource

            resource = UserDefinedObject1Resource(http)
            results = await resource.search(custom="eq:12345:test_value")

            assert len(results) == 1
            assert results[0].custom_fields[12345] == "test_value"


# =============================================================================
# 4. Custom field search syntax validation
# =============================================================================


class TestCustomFieldSearchSyntax:
    """Validate custom field search syntax matches detective findings.

    Detective found:
    - custom=<comparator>:<fieldId>:<value> shortcut syntax
    - Supported comparators: eq, ne, gt, gte, lt, lte, wc, wce, wcs, src, etc.
    - Natural operators transform: =11:Technology -> eq:11:Technology
    - The shortcut always targets custom.value (string field)
    """

    @pytest.mark.asyncio
    async def test_custom_field_eq_search(self, httpx_mock: HTTPXMock):
        """Test custom field equals search: custom=eq:fieldId:value."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/contacts?custom=eq%3A11%3ATechnology&limit=100&offset=0",
            json={
                "error": None,
                "data": [
                    {
                        "id": 1,
                        "name": "John Doe",
                        "firstName": "John",
                        "lastName": "Doe",
                        "email": "john@example.com",
                        "active": 1,
                        "regDate": "2024-01-01",
                        "modDate": "2024-01-15",
                        "emailBounceReason": "",
                        "journeyStep": "lead",
                        "hasForm": False,
                        "hasMail": False,
                        "hasVisit": False,
                        "isPriority": False,
                        "userEditable": True,
                        "userRemovable": True,
                        "score": 0,
                        "custom": [{"fieldId": 11, "value": "Technology"}],
                        "categories": [],
                        "connectedClients": [],
                        "mailBounces": [],
                        "optins": [],
                        "projects": [],
                        "segments": [],
                        "socialEvent": [],
                        "client": {"id": 1, "name": "Tech Corp"},
                        "firstTouch": {},
                        "regBy": {},
                        "supportTickets": {},
                    }
                ],
            },
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            from upsales.resources.contacts import ContactsResource

            resource = ContactsResource(http)
            results = await resource.search(custom="eq:11:Technology")

            assert len(results) == 1
            assert results[0].custom_fields[11] == "Technology"

    @pytest.mark.asyncio
    async def test_custom_field_natural_syntax(self, httpx_mock: HTTPXMock):
        """Test natural syntax =11:Technology transforms to eq:11:Technology."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/contacts?custom=eq%3A11%3ATechnology&limit=100&offset=0",
            json={
                "error": None,
                "data": [],
            },
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            from upsales.resources.contacts import ContactsResource

            resource = ContactsResource(http)
            results = await resource.search(custom="=11:Technology")

            assert len(results) == 0
            # The key test: verify the URL was called with eq: prefix
            request = httpx_mock.get_requests()[0]
            assert "custom=eq%3A11%3ATechnology" in str(request.url)

    @pytest.mark.asyncio
    async def test_custom_field_wildcard_search(self, httpx_mock: HTTPXMock):
        """Test wildcard search: custom=wc:fieldId:*value*."""
        httpx_mock.add_response(
            url="https://power.upsales.com/api/v2/contacts?custom=wc%3A11%3A%2ATech%2A&limit=100&offset=0",
            json={"error": None, "data": []},
        )

        async with HTTPClient(token="test_token", auth_manager=None) as http:
            from upsales.resources.contacts import ContactsResource

            resource = ContactsResource(http)
            results = await resource.search(custom="wc:11:*Tech*")

            assert len(results) == 0
            request = httpx_mock.get_requests()[0]
            assert "custom=wc" in str(request.url)
