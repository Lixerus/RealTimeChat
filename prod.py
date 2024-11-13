import aio_pika
import asyncio
from random import choice
from string import ascii_lowercase

async def connection():
    conn = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
    return conn

async def prod(prod_ex : aio_pika.abc.AbstractExchange, p):
    while True:
        # salt = ''.join(choice(ascii_lowercase) for _ in range(20))
        salt = ';flsdjkla;jfl;asdjfkas;dljfk lksadjflk;jjsdkaf;lasdjfl;kasdf'
        msg = aio_pika.message.Message(body=salt.encode(), content_type="text/plain")
        # print(p)
        await prod_ex.publish(msg, routing_key='cons_queue')


async def main():
    tasks = []
    conn = await connection()
    conn2 = await connection()
    channel3 = await conn2.channel(channel_number=14, publisher_confirms=True)
    channel1 = await conn.channel(channel_number=12, publisher_confirms=True)
    prod_ex = await channel1.declare_exchange(name='prod_ex')
    channel2 =  await conn.channel(channel_number=13, publisher_confirms=True)
    prod_ex2 = await channel2.declare_exchange(name = "prod_ex1")
    prod_ex3 = channel3.get_exchange(name='prod_ex', ensure=True)
    task1 = asyncio.create_task(prod(prod_ex, p = 1))
    task2 = asyncio.create_task(prod(prod_ex, p = 2))
    task3 = asyncio.create_task(prod(prod_ex3, p = 3))
    rtsks = [task1,task2,task3]
    await task1
    # await task2


# asyncio.run(main=main())