import asyncio
from typing import AsyncIterator, Dict, Generic, TypeVar

T = TypeVar("T")

class IQueue(Generic[T]):
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