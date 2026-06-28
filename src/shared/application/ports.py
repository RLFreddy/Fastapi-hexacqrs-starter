from abc import ABC, abstractmethod
from typing import Awaitable, Callable


class EventBus(ABC):
    @abstractmethod
    async def publish(self, exchange: str, routing_key: str, message: dict):
        ...

    @abstractmethod
    async def consume(
        self, queue: str, callback: Callable[[dict], Awaitable[None]], exchange: str = None, routing_key: str = None
    ):
        ...
