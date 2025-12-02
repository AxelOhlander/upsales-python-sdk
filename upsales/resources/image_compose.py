"""Image composition resource manager for Upsales API.

Provides methods to interact with the /api/v2/image/compose endpoint.
This endpoint is used to compose/modify images (e.g., add YouTube play buttons).

Example:
    >>> async with Upsales(token="...") as upsales:
    ...     result = await upsales.image_compose.compose(
    ...         sourcepath="/path/to/image.jpg",
    ...         composition="addYouTubePlayButton"
    ...     )
"""

from typing import Unpack

from upsales.http import HTTPClient
from upsales.models.image_compose import ImageComposeCreateFields, ImageComposeResponse


class ImageComposeResource:
    """Resource manager for image composition endpoint.

    This endpoint only supports POST operations for composing/modifying images.
    It does not support standard CRUD operations (GET, PUT, DELETE).

    Example:
        >>> resource = ImageComposeResource(http_client)
        >>> result = await resource.compose(
        ...     sourcepath="/images/video_thumbnail.jpg",
        ...     composition="addYouTubePlayButton"
        ... )
    """

    def __init__(self, http: HTTPClient):
        """Initialize image composition resource manager.

        Args:
            http: HTTP client for API requests.
        """
        self.http = http
        self.endpoint = "/image/compose"

    async def compose(self, **data: Unpack[ImageComposeCreateFields]) -> ImageComposeResponse:
        """Compose/modify an image.

        Currently supports adding YouTube play buttons to images.

        Args:
            **data: Image composition parameters.
                sourcepath: Path to the source image.
                composition: Type of composition (currently only "addYouTubePlayButton").

        Returns:
            Response containing the composed image URL or path.

        Raises:
            ValidationError: If required fields are missing or invalid.
            UpsalesError: If the API request fails.

        Example:
            >>> result = await resource.compose(
            ...     sourcepath="/uploads/video_thumb.jpg",
            ...     composition="addYouTubePlayButton"
            ... )
            >>> print(result.url)
        """
        response_data = await self.http.post(self.endpoint, **data)
        return ImageComposeResponse.model_validate(response_data["data"])
