import os
from typing import Any

import httpx
from fastapi.responses import JSONResponse
from pydantic import Field

from ..interfaces import Identifier, IRequest, ITask
from ..schemas import ImageRequest, ImageResponse
from ..utils.handlers import handle


class ImageGenerationResponse(JSONResponse):
    """
    A response object for the image generation task.
    """

    def __init__(self, data: ImageResponse, **kwargs: Any):
        super().__init__(content=data, **kwargs)


class ImageGeneration(ITask[ImageRequest, ImageGenerationResponse]):
    """
    A generic class for generating images using the `ImageGen` model with a singleton instance.
    """

    identifier: Identifier = Field(default="stabilityai/stable-diffusion-xl-base-1.0")

    async def handler(self, *, request: IRequest[ImageRequest]):
        """
        Handles the image generation task.

        Args:
            request (IRequest[ImageRequest]): The image request.

        Returns:
            ImageResponse: The image response.
        """
        data = await self.gen_image(request=request)
        return ImageGenerationResponse(data=data)  # type: ignore

    @handle
    async def gen_image(self, *, request: IRequest[ImageRequest]) -> ImageResponse:
        """
        Generates an image based on the given data.

        Args:
            data (ImageRequest): The image request data.

        Returns:
            ImageResponse: The image response.
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.runpod.ai/v2/riqj0gj1sg8asw/runsync",
                json=request.model_dump(),
                headers={"Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"},
                timeout=30000,
            )
            return ImageResponse(**response.json())
