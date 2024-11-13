import aio_pika
from aio_pika.message import Message
from aio_pika.abc import AbstractExchange, AbstractConnection, AbstractQueue, AbstractChannel, AbstractIncomingMessage
from fastapi import WebSocket
from aio_pika.exchange import ExchangeType
from ws_manager import WsChatManager
import asyncio

class ChatMessagesClient:
    _connection: AbstractConnection
    _channel : AbstractChannel
    _exchange : AbstractExchange
    _msg_queue : AbstractQueue

    @classmethod
    async def _connect(cls, uri: str = "amqp://guest:guest@localhost/") -> None:
        cls._connection = await aio_pika.connect(uri)
        cls._channel = await cls._connection.channel(publisher_confirms=True)
        cls._exchange = await cls._channel.declare_exchange(name='chat_messages', type=ExchangeType.FANOUT, durable=True)
        cls._msg_queue = await cls._channel.declare_queue(exclusive=True, durable=True)
        await cls._msg_queue.consume(cls._recieve_msg, no_ack=False)

    @classmethod
    async def _recieve_msg(cls, message: AbstractIncomingMessage) -> None:
        with message.process():
            tokens = message.body.decode().split(' ')
            websockets : set[WebSocket] = WsChatManager.get_ws_in_group(tokens[0])
            ws_send_tasks = [asyncio.create_task(ws.send_text(f'{tokens[1]} {tokens[2]}')) for ws in websockets]
        results = await asyncio.gather(ws_send_tasks,return_exceptions=True)
        for result in results:
            if result != None:
                print(f"GOT an error while sending the message. {result}")

    @classmethod
    async def broadcast_msg(cls, channel: str, username: str, message: str) -> int:
        message = f'{channel} {username} {message}'
        await cls._exchange.publish(
            Message(
                message.encode(),
                content_type="text/plain",
                delivery_mode='persistent'
                ))
        return True