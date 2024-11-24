from redis import asyncio as aioredis
from asyncio import create_task
from redis.exceptions import RedisError
from .ws_manager import WsChatManager


class CacheService:
    _redis = aioredis.from_url("redis://localhost", decode_responses=True)
    _groups_cache_full = {group : False for group in WsChatManager.get_all_groups()}
    MAX_CACHE_LENGTH = 100

    @classmethod
    async def retreve_group_cahce(cls, group_name:str) -> list | None:
        res = await cls._redis.lrange(group_name, 0 ,-1)
        if len(res) > cls.MAX_CACHE_LENGTH:
            cls._groups_cache_full[group_name] = True
            create_task(cls._redis.ltrim(group_name, 0, cls.MAX_CACHE_LENGTH))
        return res

    @classmethod
    async def update_group_cache(cls, group_name: str, text:str):
        try:
            if not cls._groups_cache_full[group_name]:
                res = await cls._redis.rpush(group_name, text)
            else:
                async with cls._redis.pipeline(transaction=False) as pipe:
                    pipe.rpush(group_name, text)
                    pipe.lpop(group_name)
                    await pipe.execute(raise_on_error=True)
        except RedisError as e:
            print(f"Redis error with group {group_name} and error {e}")