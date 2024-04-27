from pydantic import BaseModel, Field
from typing_extensions import Literal, Required, TypedDict


class LLMMessage(BaseModel):
    role: Literal["assistant", "user", "system"] = Field(
        ...,
        title="Role",
        description="The role of the speaker.",
    )
    content: str = Field(
        ...,
        title="Content",
        description="The content for generating language model continuation.",
    )


class LLMConversation(BaseModel):
    messages: list[LLMMessage] = Field(
        ...,
        title="Messages",
        description="The conversation messages.",
    )
    instructions: str = Field(
        ...,
        title="Instructions",
        description="The system instructions.",
    )


class LLMResponseEvent(TypedDict):
    role: Required[Literal["assistant", "user", "system"]]
    content: Required[str]
