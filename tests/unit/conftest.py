from fastapi import Request
import pytest
from unittest.mock import AsyncMock, Mock
from redis.client import Redis

from app.core.redis_client import rate_limit
from app.repositories.user_repository import UserRepository
from app.services.authService import AuthService

# test_auth_service block
@pytest.fixture()
def mock_user_repo():
    return AsyncMock(spec=UserRepository)

@pytest.fixture()
def auth_service(mock_user_repo):
    return AuthService(mock_user_repo)

# test_rate_limiter and brute-force protection block
@pytest.fixture()
def mock_redis():
    return Mock(spec=Redis)

@pytest.fixture()
def mock_request():
    return Mock(spec=Request)
