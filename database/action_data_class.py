import datetime

from sqlalchemy import select, insert, update, column, text, delete
from sqlalchemy.dialects.postgresql import insert as postgres_insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from database.model import (ChannelsTable)


class DataInteraction():
    def __init__(self, session: async_sessionmaker):
        self._sessions = session

    async def add_channel(self, channel: str, count: int, warning_channels: list[str]):
        async with self._sessions() as session:
            await session.execute(postgres_insert(ChannelsTable).values(
                channel=channel,
                count=count,
                warning_channels=warning_channels
            ).on_conflict_do_nothing(index_elements=['channel']))
            await session.commit()

    async def add_channel_post(self, id: int):
        async with self._sessions() as session:
            await session.execute(update(ChannelsTable).where(ChannelsTable.id == id).values(
                posts=ChannelsTable.posts + 1
            ))
            await session.commit()

    async def get_channels(self):
        async with self._sessions() as session:
            result = await session.scalars(select(ChannelsTable))
        return result.fetchall()

    async def get_channel(self, id: int):
        async with self._sessions() as session:
            result = await session.scalar(select(ChannelsTable).where(ChannelsTable.id == id))
        return result

    async def update_channel(self, id: int, **kwargs):
        async with self._sessions() as session:
            await session.execute(update(ChannelsTable).where(ChannelsTable.id == id).values(kwargs))
            await session.commit()

    async def set_posts(self):
        channels = await self.get_channels()
        async with self._sessions() as session:
            for channel in channels:
                await session.execute(update(ChannelsTable).where(ChannelsTable.id == channel.id).values(
                    posts=0
                ))
            await session.commit()

    async def del_channel(self, id):
        async with self._sessions() as session:
            await session.execute(delete(ChannelsTable).where(ChannelsTable.id == id))
            await session.commit()
