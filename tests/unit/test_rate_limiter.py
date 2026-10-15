import pytest
from unittest.mock import patch

from app.core.exceptions import SomethingIsUnavailableException
from app.core.redis_client import rate_limiter

@pytest.mark.asyncio
@patch("app.core.redis_client.rate_limit")
async def test_limiter_without_scope(mock_rate_limit, mock_redis, mock_request):
    mock_request.client.host = "127.0.0.1"
    mock_request.url.path = "/test/"
    limit = rate_limiter(3, 10)
    await limit(mock_request, mock_redis)
    mock_rate_limit.assert_awaited_once_with(mock_redis, "127.0.0.1:/test/", 3, 10)

@pytest.mark.asyncio
@patch("app.core.redis_client.rate_limit")
async def test_limiter_with_scope(mock_rate_limit, mock_redis, mock_request):
    mock_request.client.host = "127.0.0.1"
    mock_request.url.path = "/test/"
    limit = rate_limiter(3, 10, "test_scope")
    await limit(mock_request, mock_redis)
    mock_rate_limit.assert_awaited_once_with(mock_redis, "127.0.0.1:test_scope", 3, 10)

@pytest.mark.asyncio
@patch("app.core.redis_client.rate_limit")
async def test_rate_limiter_without_client(mock_rate_limit, mock_redis, mock_request):
    mock_request.client = None
    limit = rate_limiter(3, 10)
    
    with pytest.raises(SomethingIsUnavailableException):
        await limit(mock_request, mock_redis)

    mock_rate_limit.assert_not_awaited()
