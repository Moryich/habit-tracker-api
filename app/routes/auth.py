from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.redis_client import rate_limiter
from app.repositories.user_repository import UserRepository
from app.schemas.user import AuthResponse, UserCreate, UserLogin, UserResponse
from app.services.authService import AuthService

auth = APIRouter(prefix='/auth', tags=['Auth'])

def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db)

def get_auth_service(repo: UserRepository = Depends(get_user_repository)) -> AuthService:
    return AuthService(repo)

@auth.post('/registration', status_code=201, dependencies=[
    Depends(rate_limiter(10, 600))
])
async def registration(user: UserCreate, service: AuthService = Depends(get_auth_service)):
    new_user, access_token = await service.registrate(user)
    return AuthResponse(access_token=access_token, user=UserResponse.model_validate(new_user))

@auth.post('/login', dependencies=[
    Depends(rate_limiter(10, 60))
])
async def login(user: UserLogin, service: AuthService = Depends(get_auth_service)):
    exists, access_token = await service.login(user)
    return AuthResponse(access_token=access_token, user=UserResponse.model_validate(exists))

