from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.channel_repository import ChannelRepository
from app.repositories.invite_link_repository import InviteLinkRepository
from app.repositories.member_event_repository import MemberEventRepository
from app.repositories.member_repository import MemberRepository


class MemberService:
    def __init__(self, session: AsyncSession):
        self.channel_repository = ChannelRepository(session)
        self.member_repository = MemberRepository(session)
        self.member_event_repository = MemberEventRepository(session)
        self.invite_link_repository = InviteLinkRepository(session)

    async def handle_chat_member_update(self, chat_member_update: dict) -> None:
        chat = chat_member_update.get("chat")
        old_chat_member = chat_member_update.get("old_chat_member")
        new_chat_member = chat_member_update.get("new_chat_member")

        if not chat or not old_chat_member or not new_chat_member:
            return

        user = new_chat_member.get("user")
        if not user:
            return

        telegram_chat_id = chat.get("id")
        chat_title = chat.get("title") or chat.get("username") or chat.get("first_name")
        chat_type = chat.get("type")

        if telegram_chat_id is None:
            return

        channel = await self.channel_repository.upsert(
            telegram_chat_id=telegram_chat_id,
            title=chat_title,
            chat_type=chat_type,
        )

        old_status = old_chat_member.get("status")
        new_status = new_chat_member.get("status")

        event_type = self._detect_event_type(old_status, new_status)

        if event_type is None:
            return

        invite_link_id = None
        invite_link_data = chat_member_update.get("invite_link")

        if invite_link_data:
            telegram_invite_link = invite_link_data.get("invite_link")

            if telegram_invite_link:
                invite_link = await self.invite_link_repository.get_by_invite_link(
                    telegram_invite_link
                )

                if invite_link:
                    invite_link_id = invite_link.id

        telegram_user_id = user.get("id")
        if telegram_user_id is None:
            return

        username = user.get("username")
        first_name = user.get("first_name")
        last_name = user.get("last_name")

        current_status = "active" if event_type == "joined" else "left"

        member = await self.member_repository.upsert_member(
            channel_id=channel.id,
            telegram_user_id=telegram_user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            status=current_status,
            event_type=event_type,
        )

        await self.member_event_repository.create_event(
            channel_id=channel.id,
            telegram_user_id=telegram_user_id,
            member_id=member.id,
            event_type=event_type,
            old_status=old_status,
            new_status=new_status,
            invite_link_id=invite_link_id,
        )

    def _detect_event_type(
        self,
        old_status: str | None,
        new_status: str | None,
    ) -> str | None:
        left_statuses = {"left", "kicked"}
        active_statuses = {"member", "administrator", "creator"}

        if old_status in left_statuses and new_status in active_statuses:
            return "joined"

        if old_status in active_statuses and new_status == "left":
            return "left"

        if old_status in active_statuses and new_status == "kicked":
            return "kicked"

        return None