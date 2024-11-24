import aio_pika
from aio_pika.abc import AbstractConnection, AbstractQueue, AbstractChannel, AbstractIncomingMessage
from typing import Protocol
from enum import Enum
import asyncio
import uuid

class IConsumer(Protocol):
    connection : AbstractConnection
    def consume_handler(): ...

class IProducer(Protocol):
    connection : AbstractConnection
    def publish_handler(): ...

class RpcStatuses(Enum):
    ACCEPT = "accept"
    REJECT = "reject"
    FAILED = "failed"
    TIMEDOUT = "timedout"
    CANCELLED = "cancelled"
    UNEXPECTED = "unexpected"

class AuthRpcClient:
    _connection: AbstractConnection
    _channel : AbstractChannel
    _callback_queue : AbstractQueue
    _futures : dict[str, asyncio.Future] = {}

    @classmethod
    async def _connect(cls, uri: str = "amqp://guest:guest@localhost/") -> None:
        cls._connection = await aio_pika.connect(uri)
        cls._channel = await cls._connection.channel()
        cls._callback_queue = await cls._channel.declare_queue(exclusive=True)
        await cls._callback_queue.consume(cls._on_response, no_ack=True)

    @classmethod
    async def _on_response(cls, message: AbstractIncomingMessage) -> None:
        future: asyncio.Future = cls._futures.pop(message.correlation_id)
        if message.correlation_id is None:
            future.set_result(RpcStatuses.FAILED)
        future.set_result(message.body.decode())

    @classmethod
    async def verify_ticket(cls, message: str) -> int:
        correlation_id = str(uuid.uuid4())
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        cls._futures[correlation_id] = future
        await cls._channel.default_exchange.publish(
            aio_pika.message.Message(
                message.encode(),
                content_type="text/plain",
                correlation_id=correlation_id,
                reply_to=cls._callback_queue.name,
                ),
            routing_key="auth_queue",)
        try:
            async with asyncio.timeout(10):
                result = str(await future)
        except asyncio.TimeoutError:
            cls._futures.pop(correlation_id)
            return RpcStatuses.TIMEDOUT
        except asyncio.CancelledError:
            cls._futures.pop(correlation_id)
            return RpcStatuses.CANCELLED
        if result not in RpcStatuses:
            return RpcStatuses.UNEXPECTED
        return result