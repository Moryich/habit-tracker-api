from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.redis_client import rate_limiter
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserPublic
from app.services.userService import UserService

user = APIRouter(prefix='/user', tags=['User'])

def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db)

def get_user_service(repo: UserRepository = Depends(get_user_repository)) -> UserService:
    return UserService(repo)

@user.get('/', dependencies=[
    Depends(rate_limiter(120, 60))
])
async def get_users(limit: int = Query(default=20, ge=1, le=100), offset: int = Query(default=0, ge=0), service: UserService = Depends(get_user_service)):
    users = await service.get_users(limit, offset)
    return [UserPublic.model_validate(user) for user in users]
