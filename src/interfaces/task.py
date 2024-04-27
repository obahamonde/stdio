from abc import ABC, abstractmethod
from typing import Coroutine, Generic, TypeAlias, TypeVar

from fastapi import Response
from pydantic import BaseModel
from typing_extensions import Literal

Identifier: TypeAlias = Literal[
    "sentence-transformers/all-mpnet-base-v2",
    "openai/whisper-large-v3",
    "tts_models/multilingual/multi-dataset/xtts_v2",
    "facebook/musicgen-melody",
    "llama-3-quipu",
    "stabilityai/stable-diffusion-xl-base-1.0",
]
T = TypeVar("T")
Res = TypeVar("Res", bound=Response)


class IRequest(BaseModel, Generic[T]):
    input: T


class ITask(BaseModel, Generic[T, Res], ABC):
    identifier: Identifier

    @abstractmethod
    async def handler(
        self, *, request: IRequest[T]
    ) -> Res | Coroutine[None, Res, Res]: ...
