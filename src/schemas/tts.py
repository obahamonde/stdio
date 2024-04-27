from pydantic import BaseModel, Field


class YoutubeVideoRequest(BaseModel):
    url: str = Field(..., description="The URL of the YouTube video.")
