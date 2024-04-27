from pydantic import BaseModel, Field
from typing_extensions import TypedDict


class ImageRequest(BaseModel):
    """
    A class for representing an image request.
    """

    prompt: str = Field(
        ...,
        title="Prompt",
        description="The prompt for generating an image.",
    )
    num_inference_steps: int = Field(
        default=25,
        title="Number of Inference Steps",
        description="The number of inference steps for generating an image.",
    )
    refiner_inference_steps: int = Field(
        default=50,
        title="Refiner Inference Steps",
        description="The number of inference steps for refining an image.",
    )
    width: int = Field(
        default=1024,
        title="Width",
        description="The width of the generated image.",
    )
    height: int = Field(
        default=1024,
        title="Height",
        description="The height of the generated image.",
    )
    guidance_scale: float = Field(
        default=7.5,
        title="Guidance Scale",
        description="The guidance scale for generating an image.",
    )
    strength: float = Field(
        default=0.3,
        title="Strength",
        description="The strength for generating an image.",
    )
    seed: int = Field(
        default=42,
        title="Seed",
        description="The seed for generating an image.",
    )
    num_images: int = Field(
        default=1,
        title="Number of Images",
        description="The number of images to generate.",
    )


class OutputImage(TypedDict):
    """
    A class for representing an output image.
    """

    image_url: str
    images: list[str]
    seed: int


class ImageResponse(TypedDict):
    """
    A class for representing an image response.
    """

    delayTime: int
    executionTime: int
    id: str
    output: OutputImage
    status: str
