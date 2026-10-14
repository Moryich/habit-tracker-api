from redis.asyncio import Redis
from fastapi import Depends, Request

from app.core.config import config
from app.core.exceptions import SomethingIsUnavailableException, TooManyRequestsException

redis = Redis.from_url(f"{config.REDIS_URL}/1")

def get_redis():
    return redis

async def rate_limit(client: Redis, key: str, max_requests: int, window_seconds: int):
    pipeline = client.pipeline(transaction=True)
    pipeline.incr(key)
    pipeline.expire(name=key, time=window_seconds, nx=True)
    res = await pipeline.execute()
    if res[0] > max_requests:
        raise TooManyRequestsException(f"Too many requests, try again in {await client.ttl(key)} seconds")

def rate_limiter(max_requests: int, window_seconds: int, scope: str | None = None):
    async def limit(request: Request, redis_client: Redis = Depends(get_redis)):
        if request.client is None:
            raise SomethingIsUnavailableException("Client adress is unavailable")
        if scope is None:
            key = f"{request.client.host}:{request.url.path}"
        else:
            key = f"{request.client.host}:{scope}"
        await rate_limit(redis_client, key, max_requests, window_seconds)
    return limit
