from app.core.exceptions import InvalidCredentialsException, SomethingAlreadyExistsException, TooManyRequestsException
import pytest
from types import SimpleNamespace
from unittest.mock import patch

from app.schemas.user import UserCreate, UserLogin
from app.core.security import dummy_hash

#registrate block
@pytest.mark.asyncio
@patch("app.services.authService.create_access_token")
async def test_registrate_success(mock_access_token, mock_user_repo, auth_service):
    mock_user_repo.get_by_email_or_username.return_value = None
    user_data = UserCreate(username="test", email="test@test.com", password="test")
    user_mock = SimpleNamespace(user_id=1, username="test", email="test@test.com", hashed_password="test")
    mock_user_repo.create.return_value = user_mock
    token = mock_access_token.return_value = "test_access_token"

    new_user, access_token = await auth_service.registrate(user_data)

    assert new_user is user_mock
    assert access_token == token

@pytest.mark.asyncio
async def test_registrate_email_exists(mock_user_repo, auth_service):
    user_data = UserCreate(username="test1", email="test@test.com", password="test")
    user_mock = SimpleNamespace(username="test2", email="test@test.com", password="test")
    mock_user_repo.get_by_email_or_username.return_value = user_mock
    
    with pytest.raises(SomethingAlreadyExistsException):
        await auth_service.registrate(user_data)

@pytest.mark.asyncio
async def test_registrate_username_exists(mock_user_repo, auth_service):
    user_data = UserCreate(username="test", email="test1@test.com", password="test")
    user_mock = SimpleNamespace(username="test", email="test2@test.com", password="test")
    mock_user_repo.get_by_email_or_username.return_value = user_mock

    with pytest.raises(SomethingAlreadyExistsException):
        await auth_service.registrate(user_data)

# login block
@patch("app.services.authService.clear_failure")
@patch("app.services.authService.count_failure")
@patch("app.services.authService.check_failure")
@patch("app.services.authService.create_access_token")
@patch("app.services.authService.verify_password")
@pytest.mark.asyncio
async def test_login_success(mock_verify_password, mock_access_token, mock_check_failure, mock_count_failure, mock_clear_failure, mock_user_repo, auth_service, mock_redis):
    user_data = UserLogin(email="test@test.com", password="test")
    user_mock = SimpleNamespace(user_id=1, username="test", email="test@test.com", hashed_password="test")
    mock_user_repo.get_by_email.return_value = user_mock
    mock_verify_password.return_value = True
    token = mock_access_token.return_value = "test_access_token"

    exists, access_token = await auth_service.login(user_data, mock_redis)

    mock_check_failure.assert_awaited_once_with(mock_redis, user_data.email, 5)
    mock_count_failure.assert_not_awaited()
    mock_clear_failure.assert_awaited_once_with(mock_redis, user_data.email)

    assert exists is user_mock
    assert access_token == token

@patch("app.services.authService.clear_failure")
@patch("app.services.authService.count_failure")
@patch("app.services.authService.check_failure")
@patch("app.services.authService.verify_password")
@pytest.mark.asyncio
async def test_login_email_not_exists(mock_verify_password, mock_check_failure, mock_count_failure, mock_clear_failure, mock_user_repo, auth_service, mock_redis):
    user_data = UserLogin(email="test@test.com", password="test")
    mock_user_repo.get_by_email.return_value = None

    with pytest.raises(InvalidCredentialsException):
        await auth_service.login(user_data, mock_redis)

    mock_check_failure.assert_awaited_once_with(mock_redis, user_data.email, 5)
    mock_count_failure.assert_awaited_once_with(mock_redis, user_data.email, 300)
    mock_clear_failure.assert_not_awaited()

    mock_verify_password.assert_called_once_with(user_data.password, dummy_hash)

@patch("app.services.authService.clear_failure")
@patch("app.services.authService.count_failure")
@patch("app.services.authService.check_failure")
@patch("app.services.authService.verify_password")
@pytest.mark.asyncio
async def test_login_wrong_password(mock_verify_password, mock_check_failure, mock_count_failure, mock_clear_failure, mock_user_repo, auth_service, mock_redis):
    user_data = UserLogin(email="test@test.com", password="test")
    user_mock = SimpleNamespace(username="test", email="test@test.com", hashed_password="test")
    mock_user_repo.get_by_email.return_value = user_mock
    mock_verify_password.return_value = False

    with pytest.raises(InvalidCredentialsException):
        await auth_service.login(user_data, mock_redis)

    mock_check_failure.assert_awaited_once_with(mock_redis, user_data.email, 5)
    mock_count_failure.assert_awaited_once_with(mock_redis, user_data.email, 300)
    mock_clear_failure.assert_not_awaited()

    mock_verify_password.assert_called_once_with(user_data.password, user_mock.hashed_password)

# login brute-force additional test
@patch("app.services.authService.check_failure")
@pytest.mark.asyncio
async def test_login_blocked(mock_check_failure, mock_redis, auth_service, mock_user_repo):
    user_data = UserLogin(email="test@test.com", password="1234")
    mock_check_failure.side_effect = TooManyRequestsException("Too many attempts")

    with pytest.raises(TooManyRequestsException):
        await auth_service.login(user_data, mock_redis)

    mock_check_failure.assert_awaited_once_with(mock_redis, user_data.email, 5)
    mock_user_repo.get_by_email.assert_not_awaited()
