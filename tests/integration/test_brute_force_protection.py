import asyncio
import pytest

from app.core.exceptions import TooManyRequestsException
from app.core.redis_client import check_failure, clear_failure, count_failure

@pytest.mark.asyncio
async def test_limit_excess(redis_client_fixture, brute_force_email_fixture):
    await check_failure(redis_client_fixture, brute_force_email_fixture, 3)

    await count_failure(redis_client_fixture, brute_force_email_fixture, 5)
    await count_failure(redis_client_fixture, brute_force_email_fixture, 5)

    await check_failure(redis_client_fixture, brute_force_email_fixture, 3)

    await count_failure(redis_client_fixture, brute_force_email_fixture, 5)

    with pytest.raises(TooManyRequestsException):
        await check_failure(redis_client_fixture, brute_force_email_fixture, 3)

@pytest.mark.asyncio
async def test_ttl_not_extending(redis_client_fixture, brute_force_email_fixture):
    await count_failure(redis_client_fixture, brute_force_email_fixture, 10)
    ttl_before = await redis_client_fixture.pttl(f"login-failure:{brute_force_email_fixture}")

    await asyncio.sleep(3)

    await count_failure(redis_client_fixture, brute_force_email_fixture, 10)
    ttl_after = await redis_client_fixture.pttl(f"login-failure:{brute_force_email_fixture}")

    assert 0 < ttl_after < ttl_before - 2000

@pytest.mark.asyncio
async def test_clear_restores_check(redis_client_fixture, brute_force_email_fixture):
    await check_failure(redis_client_fixture, brute_force_email_fixture, 3)

    await count_failure(redis_client_fixture, brute_force_email_fixture, 10)
    await count_failure(redis_client_fixture, brute_force_email_fixture, 10)
    await count_failure(redis_client_fixture, brute_force_email_fixture, 10)

    with pytest.raises(TooManyRequestsException):
        await check_failure(redis_client_fixture, brute_force_email_fixture, 3)

    await clear_failure(redis_client_fixture, brute_force_email_fixture)
    
    assert await redis_client_fixture.get(f"login-failure:{brute_force_email_fixture}") is None

    await check_failure(redis_client_fixture, brute_force_email_fixture, 3)

@pytest.mark.asyncio
async def test_window_recovery(redis_client_fixture, brute_force_email_fixture):
    await check_failure(redis_client_fixture, brute_force_email_fixture, 2)

    await count_failure(redis_client_fixture, brute_force_email_fixture, 3)
    await count_failure(redis_client_fixture, brute_force_email_fixture, 3)

    with pytest.raises(TooManyRequestsException):
        await check_failure(redis_client_fixture, brute_force_email_fixture, 2)

    await asyncio.sleep(4)

    await check_failure(redis_client_fixture, brute_force_email_fixture, 2)
