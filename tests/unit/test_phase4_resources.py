"""Unit tests for Phase 4 action/hybrid endpoint resources.

Tests: MailBounceResource, SocialEventsDefaultTemplatesResource,
UserDefinedObjectCategoryTypesResource.
"""

import pytest
from pytest_httpx import HTTPXMock

from upsales import Upsales

API = "https://power.upsales.com/api/v2"


def _wrap(data: dict | list | str = "OK") -> dict:
    return {"error": None, "data": data}


class TestMailBounceResource:
    """Tests for MailBounceResource."""

    @pytest.mark.anyio
    async def test_delete(self, httpx_mock: HTTPXMock) -> None:
        """Test removing a bounce record."""
        httpx_mock.add_response(
            url=f"{API}/bounce/dGVzdEBleGFtcGxlLmNvbQ==",
            method="DELETE",
            json=_wrap({}),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.mail_bounce.delete(
                mail_base64="dGVzdEBleGFtcGxlLmNvbQ=="
            )
        assert result["error"] is None

    def test_registered(self) -> None:
        """Test mail_bounce is registered."""
        assert hasattr(Upsales(token="test"), "mail_bounce")


class TestSocialEventsDefaultTemplatesResource:
    """Tests for SocialEventsDefaultTemplatesResource."""

    @pytest.mark.anyio
    async def test_get(self, httpx_mock: HTTPXMock) -> None:
        """Test getting templates by type."""
        httpx_mock.add_response(
            url=f"{API}/socialEvents/defaultTemplates/invitation",
            json=_wrap([{"id": 1, "name": "Default Invitation"}]),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.social_events_default_templates.get(type="invitation")
        assert len(result["data"]) == 1

    @pytest.mark.anyio
    async def test_delete(self, httpx_mock: HTTPXMock) -> None:
        """Test deleting a template."""
        httpx_mock.add_response(
            url=f"{API}/socialEvents/defaultTemplates/invitation/1",
            method="DELETE",
            json=_wrap({}),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.social_events_default_templates.delete(
                type="invitation", template_id=1
            )
        assert result["error"] is None

    def test_registered(self) -> None:
        """Test social_events_default_templates is registered."""
        assert hasattr(Upsales(token="test"), "social_events_default_templates")


class TestUserDefinedObjectCategoryTypesResource:
    """Tests for UserDefinedObjectCategoryTypesResource."""

    @pytest.mark.anyio
    async def test_list(self, httpx_mock: HTTPXMock) -> None:
        """Test listing category types for UDO 1."""
        httpx_mock.add_response(
            url=f"{API}/userDefinedObjectCategoryTypes/1",
            json=_wrap([{"id": 1, "name": "Category A"}]),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.user_defined_object_category_types.list(nr=1)
        assert len(result["data"]) == 1

    @pytest.mark.anyio
    async def test_delete(self, httpx_mock: HTTPXMock) -> None:
        """Test deleting a category type."""
        httpx_mock.add_response(
            url=f"{API}/userDefinedObjectCategoryTypes/5",
            method="DELETE",
            json=_wrap({}),
        )
        async with Upsales(token="test") as upsales:
            result = await upsales.user_defined_object_category_types.delete(
                category_type_id=5
            )
        assert result["error"] is None

    def test_registered(self) -> None:
        """Test user_defined_object_category_types is registered."""
        assert hasattr(Upsales(token="test"), "user_defined_object_category_types")
