from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.channel_repository import ChannelRepository
from app.repositories.invite_link_repository import InviteLinkRepository
from app.telegram.bot_api_client import TelegramBotApiClient


class InviteLinkService:
    def __init__(self, session: AsyncSession):
        self.channel_repository = ChannelRepository(session)
        self.invite_link_repository = InviteLinkRepository(session)
        self.telegram_client = TelegramBotApiClient()

    async def create_invite_link(
        self,
        channel_id: int,
        name: str,
        source: str | None,
        campaign: str | None,
    ):
        channel = await self.channel_repository.get_by_id(channel_id)

        if channel is None:
            raise ValueError("Channel not found")

        telegram_result = await self.telegram_client.create_chat_invite_link(
            telegram_chat_id=channel.telegram_chat_id,
            name=name,
        )

        invite_url = telegram_result["invite_link"]

        return await self.invite_link_repository.upsert(
            channel_id=channel.id,
            invite_link=invite_url,
            name=name,
            source=source,
            campaign=campaign,
        )

    async def find_by_telegram_invite_link(
        self,
        invite_link: str | None,
    ):
        if not invite_link:
            return None

        return await self.invite_link_repository.get_by_invite_link(invite_link)
