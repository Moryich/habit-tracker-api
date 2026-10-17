from redis.asyncio import Redis

from app.core.redis_client import check_failure, clear_failure, count_failure
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserLogin
from app.core.exceptions import InvalidCredentialsException, SomethingAlreadyExistsException
from app.core.security import create_access_token, hash_password, verify_password, dummy_hash

class AuthService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def registrate(self, user: UserCreate):
        user_exists = await self.repo.get_by_email_or_username(user.email, user.username)
        if user_exists:
            if user_exists.email == user.email:
                raise SomethingAlreadyExistsException("User with this email already exists")
            if user_exists.username == user.username:
                raise SomethingAlreadyExistsException("User with this username already exists")
 
        hashed_password = hash_password(user.password)

        new_user = await self.repo.create(user.username, user.email, hashed_password)
        access_token = create_access_token(new_user.user_id)
        return new_user, access_token

    async def login(self, user: UserLogin, client: Redis):
        await check_failure(client, user.email, 5)
        exists = await self.repo.get_by_email(user.email) 
        if exists:
            verified = verify_password(user.password, exists.hashed_password)
        else:
            verified = verify_password(user.password, dummy_hash)
        if not exists or not verified:
            await count_failure(client, user.email, 300)
            raise InvalidCredentialsException("Invalid email or password")

        await clear_failure(client, user.email)
        access_token = create_access_token(exists.user_id)
        return exists, access_token
