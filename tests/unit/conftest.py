import pytest
from unittest.mock import AsyncMock

from app.repositories.user_repository import UserRepository
from app.services.authService import AuthService

@pytest.fixture()
def mock_user_repo():
    return AsyncMock(spec=UserRepository)

@pytest.fixture()
def auth_service(mock_user_repo):
    return AuthService(mock_user_repo)
