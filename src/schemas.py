from typing import Optional

from pydantic import BaseModel, Field
from typing_extensions import TypedDict


class AudioPrompt(BaseModel):
	text: str = Field(
		...,
		title="Text",
		description="The text description for generating music.",
	)
	audio: Optional[list[float]] = Field(default=None, title="Audio", description="The audio tensor for generating music continuation.")
 
class Message(TypedDict):
	message: str
	role:str