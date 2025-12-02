"""Models for the imageCompose endpoint.

The imageCompose endpoint is used to compose/modify images, such as adding
YouTube play buttons to thumbnails.
"""

from typing import Literal, TypedDict

from pydantic import BaseModel, Field


class ImageComposeCreateFields(TypedDict, total=False):
    """Fields for composing an image.

    Attributes:
        sourcepath: Path to the source image.
        composition: Type of composition to apply.
    """

    sourcepath: str
    composition: Literal["addYouTubePlayButton"]


class ImageComposeResponse(BaseModel):
    """Response from image composition request.

    This model represents the response returned after composing an image.
    The exact structure depends on the API response format.

    Attributes:
        url: URL of the composed image (if returned).
        path: Path of the composed image (if returned).
    """

    url: str | None = Field(None, description="URL of the composed image")
    path: str | None = Field(None, description="Path of the composed image")


# Note: This endpoint doesn't have GET operations, so no PartialModel is needed
