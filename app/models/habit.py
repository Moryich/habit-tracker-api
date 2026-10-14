from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ARRAY, ForeignKey, Integer

from app.core.database import Base

class Habit(Base):
    __tablename__ = 'habits'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.user_id', ondelete='CASCADE'))
    name: Mapped[str]
    days: Mapped[list] = mapped_column(ARRAY(Integer))
    checked_days: Mapped[list] = mapped_column(ARRAY(Integer), default=list)

    user = relationship("User", back_populates="habit")
