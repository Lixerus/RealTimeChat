from schemas import UserInDB
from redis import asyncio as aioredis
import asyncio

class DBService:
    redis = aioredis.from_url("redis://redis", decode_responses=True)

    @classmethod
    async def get_user(cls, username: str, hashset_name : str = 'users'):
        password = await cls.redis.hget(name=hashset_name, key=username)
        if password == None:
            return None
        return UserInDB(username=username, hashed_password=password)
    
    @classmethod
    async def save_user(cls, username: str, hashed_password : str, hashset_name : str = 'users'):
        res = await cls.redis.hset(name=hashset_name, key=username, value=hashed_password)
        return res

    @classmethod
    async def add_to_logged(cls, username: str, token: str, name = 'logged_in'):
        res = await cls.redis.hset(name=name, key=username, value=token)
        return res

    @classmethod
    async def logout(cls, username: str, name = 'logged_in'):
        res = await cls.redis.hdel(name=name, keys = [f'{username}'])
        return res

    @classmethod
    async def add_ticket_id(cls, id:str, set_name="tickets"):
        res = await cls.redis.sadd(set_name,id)
        return res

    @classmethod
    async def check_ticket_id(cls, id: str, hset_name="tickets"):
        ismember = await cls.redis.sismember(name=hset_name, value=id)
        if ismember :
            task = asyncio.create_task(cls.redis.srem(hset_name,id))
        return ismember == 1