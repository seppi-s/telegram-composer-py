from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.channel import Channel


class ChannelRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, channel_id: int) -> Channel | None:
        result = await self.session.execute(
            select(Channel).where(Channel.id == channel_id)
        )
        return result.scalar_one_or_none()

    async def get_by_telegram_chat_id(self, telegram_chat_id: int) -> Channel | None:
        result = await self.session.execute(
            select(Channel).where(Channel.telegram_chat_id == telegram_chat_id)
        )
        return result.scalar_one_or_none()

    async def list_all(self) -> list[Channel]:
        result = await self.session.execute(
            select(Channel).order_by(Channel.id.asc())
        )
        return list(result.scalars().all())

    async def create(
        self,
        telegram_chat_id: int,
        title: str | None,
        chat_type: str | None,
    ) -> Channel:
        channel = Channel(
            telegram_chat_id=telegram_chat_id,
            title=title,
            type=chat_type,
        )

        self.session.add(channel)
        await self.session.commit()
        await self.session.refresh(channel)

        return channel

    async def update(
        self,
        channel: Channel,
        title: str | None,
        chat_type: str | None,
    ) -> Channel:
        channel.title = title
        channel.type = chat_type

        await self.session.commit()
        await self.session.refresh(channel)

        return channel

    async def upsert(
        self,
        telegram_chat_id: int,
        title: str | None,
        chat_type: str | None,
    ) -> Channel:
        channel = await self.get_by_telegram_chat_id(telegram_chat_id)

        if channel is None:
            return await self.create(
                telegram_chat_id=telegram_chat_id,
                title=title,
                chat_type=chat_type,
            )

        return await self.update(
            channel=channel,
            title=title,
            chat_type=chat_type,
        )

    async def delete(self, channel: Channel) -> None:
        await self.session.delete(channel)
        await self.session.commit()