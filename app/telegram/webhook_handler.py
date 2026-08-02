from sqlalchemy.ext.asyncio import AsyncSession

from app.services.channel_service import ChannelService
from app.services.member_service import MemberService


class TelegramWebhookHandler:
    def __init__(self, session: AsyncSession):
        self.channel_service = ChannelService(session)
        self.member_service = MemberService(session)

    async def handle_update(self, update: dict) -> None:
        if "message" in update:
            await self._handle_message(update["message"])

        if "channel_post" in update:
            await self._handle_message(update["channel_post"])

        if "my_chat_member" in update:
            await self._handle_my_chat_member(update["my_chat_member"])

        if "chat_member" in update:
            await self.member_service.handle_chat_member_update(update["chat_member"])

    async def _handle_message(self, message: dict) -> None:
        chat = message.get("chat")
        if not chat:
            return

        await self._save_chat(chat)

    async def _handle_my_chat_member(self, my_chat_member: dict) -> None:
        chat = my_chat_member.get("chat")
        if not chat:
            return

        await self._save_chat(chat)

    async def _save_chat(self, chat: dict) -> None:
        telegram_chat_id = chat.get("id")
        chat_type = chat.get("type")

        title = (
            chat.get("title")
            or chat.get("username")
            or chat.get("first_name")
        )

        if telegram_chat_id is None:
            return

        await self.channel_service.save_chat(
            telegram_chat_id=telegram_chat_id,
            title=title,
            chat_type=chat_type,
        )