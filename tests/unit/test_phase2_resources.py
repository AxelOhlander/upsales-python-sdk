"""Unit tests for Phase 2 CRUD endpoint resources.

Tests all 13 new resource managers added in Phase 2:
- AssignResource
- AccountManagerHistoryResource
- CancelEsignResource
- SendEsignReminderResource
- ContractsResource
- CustomfieldsAccountsResource
- ExportResource
- ImportMailCampaignResource
- IntegrationLogResource
- SoliditetMatcherResource
- SoliditetSearchBuyResource
- StandardFieldsResource
- TranslateTagsResource
"""

import httpx
import pytest
from pytest_httpx import HTTPXMock

from upsales import Upsales

API = "https://power.upsales.com/api/v2"


def _wrap(data: dict | list | str = "OK") -> dict:
    """Wrap data in standard Upsales response format."""
    return {"error": None, "data": data}


# ── AssignResource ──────────────────────────────────────────────


class TestAssignResource:
    """Tests for AssignResource."""

    @pytest.mark.anyio
    async def test_get(self, httpx_mock: HTTPXMock) -> None:
        """Test getting assigned user for a client."""
        httpx_mock.add_response(
            url=f"{API}/function/assign/100",
            json=_wrap({"id": 42, "name": "John"}),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.assign.get(client_id=100)
        assert result["data"]["id"] == 42

    @pytest.mark.anyio
    async def test_assign_user(self, httpx_mock: HTTPXMock) -> None:
        """Test assigning a user to a client."""
        httpx_mock.add_response(
            url=f"{API}/function/assign/100",
            method="PUT",
            json=_wrap({"id": 100, "userId": 42}),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.assign.assign_user(client_id=100, user_id=42)
        assert result["data"]["userId"] == 42

    @pytest.mark.anyio
    async def test_remove(self, httpx_mock: HTTPXMock) -> None:
        """Test removing assignment."""
        httpx_mock.add_response(
            url=f"{API}/function/assign/100",
            method="DELETE",
            json=_wrap({}),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.assign.remove(client_id=100)
        assert result["error"] is None

    def test_registered_on_client(self) -> None:
        """Test assign is registered on client."""
        upsales = Upsales(token="test")
        assert hasattr(upsales, "assign")


# ── AccountManagerHistoryResource ───────────────────────────────


class TestAccountManagerHistoryResource:
    """Tests for AccountManagerHistoryResource."""

    @pytest.mark.anyio
    async def test_set_history(self, httpx_mock: HTTPXMock) -> None:
        """Test setting account manager history."""
        httpx_mock.add_response(
            url=f"{API}/function/accountManagerHistory",
            method="PUT",
            json=_wrap("OK"),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.account_manager_history.set_history(
                client_id=100, date="2025-01-15", user_ids=[42]
            )
        assert result["data"] == "OK"

    @pytest.mark.anyio
    async def test_set_specific(self, httpx_mock: HTTPXMock) -> None:
        """Test setting specific agreement AM."""
        httpx_mock.add_response(
            url=f"{API}/function/accountManagerHistory/specific",
            method="PUT",
            json=_wrap("OK"),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.account_manager_history.set_specific(
                agreement_id=500, client_id=100, user_id=42
            )
        assert result["data"] == "OK"

    def test_registered_on_client(self) -> None:
        """Test account_manager_history is registered on client."""
        upsales = Upsales(token="test")
        assert hasattr(upsales, "account_manager_history")


# ── CancelEsignResource ────────────────────────────────────────


class TestCancelEsignResource:
    """Tests for CancelEsignResource."""

    @pytest.mark.anyio
    async def test_cancel(self, httpx_mock: HTTPXMock) -> None:
        """Test cancelling an e-sign document."""
        httpx_mock.add_response(
            url=f"{API}/function/cancelEsign/123",
            method="PUT",
            json=_wrap({"id": 123, "status": "cancelled"}),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.cancel_esign.cancel(esign_id=123)
        assert result["data"]["status"] == "cancelled"

    def test_registered_on_client(self) -> None:
        """Test cancel_esign is registered on client."""
        upsales = Upsales(token="test")
        assert hasattr(upsales, "cancel_esign")


# ── SendEsignReminderResource ──────────────────────────────────


class TestSendEsignReminderResource:
    """Tests for SendEsignReminderResource."""

    @pytest.mark.anyio
    async def test_send(self, httpx_mock: HTTPXMock) -> None:
        """Test sending an e-sign reminder."""
        httpx_mock.add_response(
            url=f"{API}/function/sendEsignReminder/123",
            method="PUT",
            json=_wrap({"id": 123}),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.send_esign_reminder.send(esign_id=123)
        assert result["data"]["id"] == 123

    def test_registered_on_client(self) -> None:
        """Test send_esign_reminder is registered on client."""
        upsales = Upsales(token="test")
        assert hasattr(upsales, "send_esign_reminder")


# ── ContractsResource ──────────────────────────────────────────


class TestContractsResource:
    """Tests for ContractsResource."""

    @pytest.mark.anyio
    async def test_list(self, httpx_mock: HTTPXMock) -> None:
        """Test listing contracts."""
        httpx_mock.add_response(
            url=f"{API}/contract",
            json=_wrap([{"id": 1, "terms": "..."}]),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.contracts.list()
        assert len(result["data"]) == 1

    @pytest.mark.anyio
    async def test_get(self, httpx_mock: HTTPXMock) -> None:
        """Test getting a contract."""
        httpx_mock.add_response(
            url=f"{API}/contract/5",
            json=_wrap({"id": 5, "terms": "Some terms"}),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.contracts.get(5)
        assert result["data"]["id"] == 5

    @pytest.mark.anyio
    async def test_update(self, httpx_mock: HTTPXMock) -> None:
        """Test updating contract terms."""
        httpx_mock.add_response(
            url=f"{API}/contract/5",
            method="PUT",
            json=_wrap({"id": 5, "terms": "New terms"}),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.contracts.update(5, terms="New terms")
        assert result["data"]["terms"] == "New terms"

    def test_registered_on_client(self) -> None:
        """Test contracts is registered on client."""
        upsales = Upsales(token="test")
        assert hasattr(upsales, "contracts")


# ── CustomfieldsAccountsResource ───────────────────────────────


class TestCustomfieldsAccountsResource:
    """Tests for CustomfieldsAccountsResource."""

    @pytest.mark.anyio
    async def test_list(self, httpx_mock: HTTPXMock) -> None:
        """Test listing custom field definitions."""
        httpx_mock.add_response(
            url=f"{API}/customfields/account",
            json=_wrap([{"id": 11, "name": "Industry"}]),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.customfields_accounts.list()
        assert len(result["data"]) == 1

    @pytest.mark.anyio
    async def test_get(self, httpx_mock: HTTPXMock) -> None:
        """Test getting a custom field definition."""
        httpx_mock.add_response(
            url=f"{API}/customfields/account/11",
            json=_wrap({"id": 11, "name": "Industry"}),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.customfields_accounts.get(11)
        assert result["data"]["name"] == "Industry"

    @pytest.mark.anyio
    async def test_create(self, httpx_mock: HTTPXMock) -> None:
        """Test creating a custom field definition."""
        httpx_mock.add_response(
            url=f"{API}/customfields/account",
            method="POST",
            json=_wrap({"id": 99, "name": "New Field"}),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.customfields_accounts.create(name="New Field")
        assert result["data"]["id"] == 99

    @pytest.mark.anyio
    async def test_update(self, httpx_mock: HTTPXMock) -> None:
        """Test updating a custom field definition."""
        httpx_mock.add_response(
            url=f"{API}/customfields/account/11",
            method="PUT",
            json=_wrap({"id": 11, "visible": False}),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.customfields_accounts.update(11, visible=False)
        assert result["data"]["visible"] is False

    @pytest.mark.anyio
    async def test_delete(self, httpx_mock: HTTPXMock) -> None:
        """Test deleting a custom field definition."""
        httpx_mock.add_response(
            url=f"{API}/customfields/account/11",
            method="DELETE",
            json=_wrap({}),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.customfields_accounts.delete(11)
        assert result["error"] is None

    def test_registered_on_client(self) -> None:
        """Test customfields_accounts is registered on client."""
        upsales = Upsales(token="test")
        assert hasattr(upsales, "customfields_accounts")


# ── ExportResource ─────────────────────────────────────────────


class TestExportResource:
    """Tests for ExportResource."""

    @pytest.mark.anyio
    async def test_trigger(self, httpx_mock: HTTPXMock) -> None:
        """Test triggering an export."""
        httpx_mock.add_response(
            url=f"{API}/function/export",
            method="POST",
            json=_wrap("OK"),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.export.trigger(
                entity="Client",
                columns=[{"key": "Client_name", "title": "Name"}],
                filters={},
                name="test-export",
            )
        assert result["data"] == "OK"

    def test_registered_on_client(self) -> None:
        """Test export is registered on client."""
        upsales = Upsales(token="test")
        assert hasattr(upsales, "export")


# ── ImportMailCampaignResource ─────────────────────────────────


class TestImportMailCampaignResource:
    """Tests for ImportMailCampaignResource."""

    @pytest.mark.anyio
    async def test_create(self, httpx_mock: HTTPXMock) -> None:
        """Test importing a mail campaign."""
        httpx_mock.add_response(
            url=f"{API}/import/mailcampaign",
            method="POST",
            json=_wrap({"id": 1, "name": "Newsletter"}),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.import_mail_campaign.create(
                name="Newsletter",
                subject="Update",
                from_address="news@example.com",
                fromName="News",
                body="<h1>Hi</h1>",
                sendDate="2025-01-15",
            )
        assert result["data"]["name"] == "Newsletter"

    def test_registered_on_client(self) -> None:
        """Test import_mail_campaign is registered on client."""
        upsales = Upsales(token="test")
        assert hasattr(upsales, "import_mail_campaign")


# ── IntegrationLogResource ─────────────────────────────────────


class TestIntegrationLogResource:
    """Tests for IntegrationLogResource."""

    @pytest.mark.anyio
    async def test_list(self, httpx_mock: HTTPXMock) -> None:
        """Test listing integration logs."""
        httpx_mock.add_response(
            url=f"{API}/integrationLog",
            json=_wrap([{"id": 1}]),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.integration_log.list()
        assert len(result["data"]) == 1

    @pytest.mark.anyio
    async def test_get(self, httpx_mock: HTTPXMock) -> None:
        """Test getting an integration log entry."""
        httpx_mock.add_response(
            url=f"{API}/integrationLog/456",
            json=_wrap({"id": 456}),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.integration_log.get(456)
        assert result["data"]["id"] == 456

    @pytest.mark.anyio
    async def test_create(self, httpx_mock: HTTPXMock) -> None:
        """Test creating an integration log entry."""
        httpx_mock.add_response(
            url=f"{API}/integrationLog",
            method="POST",
            json=_wrap({"id": 789}),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.integration_log.create(integrationId=1)
        assert result["data"]["id"] == 789

    @pytest.mark.anyio
    async def test_update(self, httpx_mock: HTTPXMock) -> None:
        """Test updating an integration log entry."""
        httpx_mock.add_response(
            url=f"{API}/integrationLog/456",
            method="PUT",
            json=_wrap({"id": 456, "status": 200}),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.integration_log.update(456, status=200)
        assert result["data"]["status"] == 200

    @pytest.mark.anyio
    async def test_delete(self, httpx_mock: HTTPXMock) -> None:
        """Test deleting an integration log entry."""
        httpx_mock.add_response(
            url=f"{API}/integrationLog/456",
            method="DELETE",
            json=_wrap({}),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.integration_log.delete(456)
        assert result["error"] is None

    def test_registered_on_client(self) -> None:
        """Test integration_log is registered on client."""
        upsales = Upsales(token="test")
        assert hasattr(upsales, "integration_log")


# ── SoliditetMatcherResource ──────────────────────────────────


class TestSoliditetMatcherResource:
    """Tests for SoliditetMatcherResource."""

    @pytest.mark.anyio
    async def test_list(self, httpx_mock: HTTPXMock) -> None:
        """Test listing matches."""
        httpx_mock.add_response(
            url=f"{API}/soliditet/matcher",
            json=_wrap([{"id": 1}]),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.soliditet_matcher.list()
        assert len(result["data"]) == 1

    @pytest.mark.anyio
    async def test_search(self, httpx_mock: HTTPXMock) -> None:
        """Test searching for matches."""
        httpx_mock.add_response(
            url=httpx.URL(
                f"{API}/soliditet/matcher/search",
                params={"id": "100", "searchString": "ACME", "countries": "SE"},
            ),
            json=_wrap([{"dunsNo": "123456789"}]),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.soliditet_matcher.search(
                client_id=100, search_string="ACME", countries="SE"
            )
        assert len(result["data"]) == 1

    @pytest.mark.anyio
    async def test_action(self, httpx_mock: HTTPXMock) -> None:
        """Test performing a match action."""
        httpx_mock.add_response(
            url=f"{API}/soliditet/matcher",
            method="PUT",
            json=_wrap({"bought": 1}),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.soliditet_matcher.action(
                buy=[{"id": 100, "dunsNo": "123456789"}]
            )
        assert result["data"]["bought"] == 1

    def test_registered_on_client(self) -> None:
        """Test soliditet_matcher is registered on client."""
        upsales = Upsales(token="test")
        assert hasattr(upsales, "soliditet_matcher")


# ── SoliditetSearchBuyResource ─────────────────────────────────


class TestSoliditetSearchBuyResource:
    """Tests for SoliditetSearchBuyResource."""

    @pytest.mark.anyio
    async def test_buy(self, httpx_mock: HTTPXMock) -> None:
        """Test purchasing a company from Soliditet."""
        httpx_mock.add_response(
            url=f"{API}/soliditet/search/buy",
            method="POST",
            json=_wrap({"id": 100, "name": "ACME Corp"}),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.soliditet_search_buy.buy(duns="123456789")
        assert result["data"]["name"] == "ACME Corp"

    @pytest.mark.anyio
    async def test_buy_with_properties(self, httpx_mock: HTTPXMock) -> None:
        """Test buy with properties."""
        httpx_mock.add_response(
            url=f"{API}/soliditet/search/buy",
            method="POST",
            json=_wrap({"id": 100}),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.soliditet_search_buy.buy(
                duns="123456789",
                properties=[{"name": "User", "value": 42}],
            )
        assert result["data"]["id"] == 100

    def test_registered_on_client(self) -> None:
        """Test soliditet_search_buy is registered on client."""
        upsales = Upsales(token="test")
        assert hasattr(upsales, "soliditet_search_buy")


# ── StandardFieldsResource ─────────────────────────────────────


class TestStandardFieldsResource:
    """Tests for StandardFieldsResource."""

    @pytest.mark.anyio
    async def test_list(self, httpx_mock: HTTPXMock) -> None:
        """Test listing all standard fields."""
        httpx_mock.add_response(
            url=f"{API}/standardField",
            json=_wrap([{"id": 1, "entity": "Contact"}]),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.standard_fields.list()
        assert len(result["data"]) == 1

    @pytest.mark.anyio
    async def test_get_for_entity(self, httpx_mock: HTTPXMock) -> None:
        """Test getting fields for an entity type."""
        httpx_mock.add_response(
            url=f"{API}/standardField/Contact",
            json=_wrap([{"id": 1, "name": "Phone"}]),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.standard_fields.get_for_entity("Contact")
        assert result["data"][0]["name"] == "Phone"

    @pytest.mark.anyio
    async def test_update(self, httpx_mock: HTTPXMock) -> None:
        """Test updating a standard field."""
        httpx_mock.add_response(
            url=f"{API}/standardField/42",
            method="PUT",
            json=_wrap({"id": 42, "required": True}),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.standard_fields.update(42, required=True)
        assert result["data"]["required"] is True

    def test_registered_on_client(self) -> None:
        """Test standard_fields is registered on client."""
        upsales = Upsales(token="test")
        assert hasattr(upsales, "standard_fields")


# ── TranslateTagsResource ─────────────────────────────────────


class TestTranslateTagsResource:
    """Tests for TranslateTagsResource."""

    @pytest.mark.anyio
    async def test_translate(self, httpx_mock: HTTPXMock) -> None:
        """Test translating tag placeholders."""
        httpx_mock.add_response(
            url=f"{API}/function/translate",
            method="POST",
            json=_wrap({"greeting": "Hello ACME Corp"}),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.translate_tags.translate(
                entity="client",
                entity_id=100,
                data={"greeting": "Hello {{Client.Name}}"},
            )
        assert result["data"]["greeting"] == "Hello ACME Corp"

    def test_registered_on_client(self) -> None:
        """Test translate_tags is registered on client."""
        upsales = Upsales(token="test")
        assert hasattr(upsales, "translate_tags")
