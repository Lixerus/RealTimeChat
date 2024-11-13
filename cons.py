import aio_pika
import asyncio
from random import choice
from string import ascii_lowercase

async def connection():
    conn = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
    return conn

async def consume(msg : aio_pika.abc.AbstractIncomingMessage):
    async with msg.process(requeue=True, ignore_processed=True):
        res = msg.body.decode()
        rchoice = choice(range(10))
        if rchoice == 0:
            await msg.nack()
        await asyncio.sleep(1)


async def main():
    conn = await connection()
    channel1 = await conn.channel(channel_number=12, publisher_confirms=True)
    channel2 = await conn.channel(channel_number=13, publisher_confirms=True)
    # await channel1.set_qos(prefetch_count = 1)
    prod_ex = await channel1.declare_exchange(name='prod_ex')
    cons_queue = await channel1.declare_queue(name = "cons_queue", durable=False)
    same_queue = await channel2.declare_queue(name='cons_queue', passive=True)
    await cons_queue.bind(prod_ex, routing_key=cons_queue.name)
    await same_queue.bind(prod_ex, routing_key=cons_queue.name)
    task1 = asyncio.create_task(cons_queue.consume(consume))
    task2 = asyncio.create_task(same_queue.consume(consume))
    await asyncio.Future()
    
asyncio.run(main=main())