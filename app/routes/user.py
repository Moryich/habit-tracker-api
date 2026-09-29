from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.user_repository import UserRepository
from app.services.userService import UserService

user = APIRouter(prefix='/user', tags=['user'])

def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db)

def get_user_service(repo: UserRepository = Depends(get_user_repository)) -> UserService:
    return UserService(repo)

@user.get('/')
async def get_users(service: UserService = Depends(get_user_service)):
    return await service.get_users()
