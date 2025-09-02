from typing import List

import datetime

from sqlalchemy import BigInteger, VARCHAR, ForeignKey, DateTime, Boolean, Column, Integer, String, func, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs


class Base(AsyncAttrs, DeclarativeBase):
    pass


class ChannelsTable(Base):
    __tablename__ = 'channels'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    channel: Mapped[str] = mapped_column(VARCHAR, unique=True)
    warning_channels: Mapped[List] = mapped_column(ARRAY(VARCHAR))
    count: Mapped[int] = mapped_column(Integer)
    posts: Mapped[int] = mapped_column(Integer, default=0)


