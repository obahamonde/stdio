import asyncio
from typing import AsyncIterator, Dict, Generic, TypeVar

import torch
from fastapi import APIRouter
from typing_extensions import NamedTuple

T = TypeVar("T")


class Progress(NamedTuple):
    progress: int
    total: int


class Stream(Generic[T]):
    subscribers: Dict[str, asyncio.Queue[T]] = {}

    async def sub(self, *, key: str) -> AsyncIterator[T]:
        if key not in self.subscribers:
            self.subscribers[key] = asyncio.Queue()
        queue = self.subscribers[key]
        while True:
            yield await queue.get()

    async def pub(self, *, key: str, data: T) -> None:
        if key not in self.subscribers:
            self.subscribers[key] = asyncio.Queue()
        queue = self.subscribers[key]
        await queue.put(data)


class TensorStream(APIRouter, Stream[torch.Tensor]):
    async def pub(self, *, key: str, data: torch.Tensor) -> None:
        await super().pub(key=key, data=data)

    async def sub(self, *, key: str) -> AsyncIterator[torch.Tensor]:
        async for data in super().sub(key=key):
            yield data
