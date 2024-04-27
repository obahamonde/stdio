import os
from typing import cast

from openai import AsyncOpenAI
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
from pydantic import Field
from sse_starlette.sse import EventSourceResponse

from ..interfaces import Identifier, IProxy, IRequest, ITask
from ..schemas import LLMConversation, LLMMessage
from ..schemas.conversation import Thread
from ..utils.handlers import handle


class LanguageModel(ITask[LLMConversation, EventSourceResponse], IProxy[AsyncOpenAI]):
    namespace: str
    identifier: Identifier = Field(default="llama-3-quipu")
    instructions: str

    def __load__(self) -> AsyncOpenAI:
        return AsyncOpenAI(base_url=os.getenv("OPENAI_API_BASE"))

    @handle
    async def handler(
        self, *, request: IRequest[LLMConversation]
    ) -> EventSourceResponse:
        client = self.__load__()
        response = await client.chat.completions.create(
            messages=cast(
                list[ChatCompletionMessageParam],
                [{"role": "system", "content": request.input.instructions}]
                + [r.model_dump() for r in request.input.messages],
            ),
            model=self.identifier,
            max_tokens=4096,
            stream=True,
            stop=["<|eot_id|>"],
        )
        chunks = ""

        async def _generator():
            nonlocal chunks

            async for chunkpart in response:
                content = chunkpart.choices[0].delta.content
                if content:
                    chunks += content
                    yield content
                else:
                    continue
            thread = await Thread.find_many(
                namespace=self.namespace, title=request.input.messages[0].content
            )
            if thread:
                thread[0].conversation.messages.append(
                    LLMMessage(content=chunks, role="assistant")
                )
                await thread[0].save()
            else:
                await Thread(
                    conversation=LLMConversation(
                        instructions=request.input.instructions,
                        messages=[
                            LLMMessage(content=chunks, role="assistant"),
                            *request.input.messages,
                        ],
                    ),
                    namespace=self.namespace,
                    title=request.input.messages[0].content[:10] + "...",
                ).save()

        return EventSourceResponse(_generator())
