import asyncio
import json
from typing import Awaitable, Callable

import aio_pika


class RabbitMQEventBus:
    def __init__(self, connection_url: str):
        self.connection_url = connection_url
        self.connection = None
        self.channel = None

    async def connect(self):
        if not self.connection or self.connection.is_closed:
            self.connection = await aio_pika.connect_robust(self.connection_url)
            self.channel = await self.connection.channel()

    async def publish(self, exchange: str, routing_key: str, message: dict):
        await self.connect()

        exchange_obj = await self.channel.declare_exchange(exchange, aio_pika.ExchangeType.DIRECT, durable=True)

        await exchange_obj.publish(aio_pika.Message(body=json.dumps(message).encode()), routing_key=routing_key)

    async def consume(
        self, queue: str, callback: Callable[[dict], Awaitable[None]], exchange: str = None, routing_key: str = None
    ):
        await self.connect()

        queue_obj = await self.channel.declare_queue(queue, durable=True)

        if exchange and routing_key:
            exchange_obj = await self.channel.declare_exchange(exchange, aio_pika.ExchangeType.DIRECT, durable=True)
            await queue_obj.bind(exchange_obj, routing_key)

        while True:
            try:
                async with queue_obj.iterator() as queue_iter:
                    async for message in queue_iter:
                        async with message.process():
                            await callback(json.loads(message.body.decode()))
            except Exception as e:
                logger = __import__("logging").getLogger(__name__)
                logger.error("Consumer error, reconnecting in 5s: %s", e)
                await asyncio.sleep(5)
