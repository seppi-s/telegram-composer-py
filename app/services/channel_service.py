from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.channel_repository import ChannelRepository


class ChannelService:
    def __init__(self, session: AsyncSession):
        self.channel_repository = ChannelRepository(session)

    async def save_chat(
        self,
        telegram_chat_id: int,
        title: str | None,
        chat_type: str | None,
    ):
        return await self.channel_repository.upsert(
            telegram_chat_id=telegram_chat_id,
            title=title,
            chat_type=chat_type,
        )