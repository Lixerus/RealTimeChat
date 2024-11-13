import aio_pika
from aio_pika.abc import AbstractConnection, AbstractChannel, AbstractQueue, AbstractExchange, AbstractIncomingMessage
from aio_pika.exceptions import AMQPConnectionError
from storage import DBService
from services import TokenService
from typing import Self
import asyncio

class AuthRpcConsumer:
    _connection: AbstractConnection
    _channel : AbstractChannel
    _exchange : AbstractExchange
    _execution_queue : AbstractQueue

    @classmethod
    async def _connect(cls, uri: str = "amqp://guest:guest@localhost/"):
        cls._connection = await aio_pika.connect(uri)
        cls._channel = await cls._connection.channel()
        cls._exchange = cls._channel.default_exchange
        cls._execution_queue = await cls._channel.declare_queue("auth_queue")
        await cls._execution_queue.consume(cls._verify_ticket)
    
    @classmethod
    async def publish_response(cls, message : aio_pika.message.Message, routing_key : str):
        print(f"routing_key {routing_key}")
        await cls._exchange.publish(message, routing_key=routing_key)

    @classmethod
    async def _verify_ticket(cls, message: AbstractIncomingMessage) -> None:
        try:
            async with message.process(requeue=False):
                assert message.reply_to is not None
                response = "reject"
                ticket = message.body.decode()
                print(f"GOT {ticket}")
                print(f"message.reply_to {message.reply_to}")
                id = TokenService.verify_ticket(ticket)
                if id:
                    result = await DBService.check_ticket_id(id)
                    if result:
                        response = "accept"
                    response = aio_pika.message.Message(body=response.encode(), correlation_id=message.correlation_id,)
                    routing_key=message.reply_to
                    print(f"fff routing_key {routing_key}")
                    asyncio.create_task(cls.publish_response(response, routing_key))
        except AssertionError:
            print(f"Invalid message with body {message.body.decode()}")