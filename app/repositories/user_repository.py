from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User

class UserRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_email_or_username(self, email: str, username: str) -> User | None:
        return (await self.db.execute(select(User).where((User.email == email) | (User.username == username)))).scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        return (await self.db.execute(select(User).where(User.email == email))).scalar_one_or_none()

    async def create(self, username: str, email: str, hashed_password: str) -> User:
        new_user = User(
            username = username,
            email = email,
            hashed_password = hashed_password
        )
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user

    async def get_all(self):
        return (await self.db.execute(select(User))).scalars().all()
