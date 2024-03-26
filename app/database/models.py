from sqlalchemy import ForeignKey, BigInteger, Column, Boolean
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String
from datetime import datetime


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Users(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str]
    tg_id = mapped_column(BigInteger)
    chat_id = mapped_column(BigInteger)
    is_subscribed = Column(Boolean, default=False)


class RequestHistory(Base):
    __tablename__ = 'request_history'

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    request_time: Mapped[datetime]
    article_number: Mapped[str] = mapped_column(String(10))

