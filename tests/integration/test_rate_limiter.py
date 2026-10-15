import pytest
import asyncio

from app.core.exceptions import TooManyRequestsException
from app.core.redis_client import rate_limit

@pytest.mark.asyncio
async def test_limit_excess(redis_client_fixture, redis_key_fixture):
    await rate_limit(redis_client_fixture, redis_key_fixture, 3, 10)
    await rate_limit(redis_client_fixture, redis_key_fixture, 3, 10)
    await rate_limit(redis_client_fixture, redis_key_fixture, 3, 10)
    
    with pytest.raises(TooManyRequestsException):
        await rate_limit(redis_client_fixture, redis_key_fixture, 3, 10)

@pytest.mark.asyncio
async def test_limit_window_recovery(redis_client_fixture, redis_key_fixture):
    await rate_limit(redis_client_fixture, redis_key_fixture, 2, 3)
    await rate_limit(redis_client_fixture, redis_key_fixture, 2, 3)

    with pytest.raises(TooManyRequestsException):
        await rate_limit(redis_client_fixture, redis_key_fixture, 2, 3)

    await asyncio.sleep(4)
        
    await rate_limit(redis_client_fixture, redis_key_fixture, 2, 3)

@pytest.mark.asyncio
async def test_ttl_not_extending(redis_client_fixture, redis_key_fixture):
    await rate_limit(redis_client_fixture, redis_key_fixture, 3, 10)
    ttl_before = await redis_client_fixture.pttl(redis_key_fixture)

    await asyncio.sleep(3)

    await rate_limit(redis_client_fixture, redis_key_fixture, 3, 10)
    ttl_after = await redis_client_fixture.pttl(redis_key_fixture)

    assert 0 < ttl_after < ttl_before - 2000

@pytest.mark.asyncio
async def test_rate_limiter_exception(redis_http_client_fixture):
    first = await redis_http_client_fixture.get("/test-rate-limiter")
    second = await redis_http_client_fixture.get("/test-rate-limiter")
    third = await redis_http_client_fixture.get("/test-rate-limiter")
    
    assert first.status_code == 200
    assert second.status_code == 200
    assert third.status_code == 429
