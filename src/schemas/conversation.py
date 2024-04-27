from functools import cached_property

from pydantic import computed_field
from transformers import AutoTokenizer  # type: ignore

from ..data.database import RocksDBModel
from .llm import LLMConversation


class Thread(RocksDBModel):
    """
    A schema for conversation data.
    """

    conversation: LLMConversation
    namespace: str
    title: str

    @cached_property
    def tokenizer(self) -> AutoTokenizer:
        """
        Returns the tokenizer for the conversation.
        """
        return AutoTokenizer.from_pretrained("meta-llama/Meta-Llama-3-8B-Instruct")  # type: ignore

    @computed_field(return_type=int)
    @property
    def token_count(self) -> int:
        """
        Returns the token count for the conversation.
        """
        chunks = self.tokenizer(
            " ".join(
                [m.content for m in self.conversation.messages]
                + [self.conversation.instructions]
            )
        )
        length = len(chunks["input_ids"])  # type: ignore
        while length > 4096:
            self.conversation.messages.pop(0)
            chunks = self.tokenizer(
                " ".join(
                    [m.content for m in self.conversation.messages]
                    + [self.conversation.instructions]
                )
            )
            length = len(chunks["input_ids"])  # type: ignore
        return length
