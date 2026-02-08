"""Translate tags resource for Upsales API.

Translates tag placeholders in text using entity data.

Example:
    ```python
    async with Upsales(token="...") as upsales:
        result = await upsales.translate_tags.translate(
            entity="client",
            entity_id=100,
            data={"greeting": "Hello {{Client.Name}}"},
        )
        print(result["data"]["greeting"])  # "Hello ACME Corp"
    ```
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from upsales.http import HTTPClient


class TranslateTagsResource:
    """Resource manager for tag translation.

    Function endpoint at /function/translate. Takes template text with
    tag placeholders and returns text with tags replaced by entity values.

    Example:
        ```python
        resource = TranslateTagsResource(http_client)
        result = await resource.translate(
            entity="client", entity_id=100,
            data={"greeting": "Hello {{Client.Name}}"}
        )
        ```
    """

    def __init__(self, http: HTTPClient) -> None:
        """Initialize translate tags resource.

        Args:
            http: HTTP client for API requests.
        """
        self._http = http
        self._endpoint = "/function/translate"

    async def translate(
        self,
        entity: str,
        entity_id: int,
        data: dict[str, str],
    ) -> dict[str, Any]:
        """Translate tag placeholders in text.

        Supported entity types: client, contact, order, activity,
        appointment, project, opportunity, sidebar (user), user.

        Args:
            entity: Entity type to pull values from.
            entity_id: ID of the entity.
            data: Key-value pairs where values contain tag placeholders.

        Returns:
            API response with translated text in data field.

        Example:
            ```python
            result = await upsales.translate_tags.translate(
                entity="client",
                entity_id=100,
                data={
                    "greeting": "Hello {{Client.Name}}",
                    "note": "Manager: {{Client.User.Name}}",
                },
            )
            ```
        """
        return await self._http.post(
            self._endpoint,
            entity=entity,
            entityId=entity_id,
            data=data,
        )
