from sqlalchemy.ext.asyncio import AsyncSession

from app.models.member_event import MemberEvent


class MemberEventRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_event(
        self,
        channel_id: int,
        telegram_user_id: int,
        member_id: int | None,
        event_type: str,
        old_status: str | None,
        new_status: str | None,
        invite_link_id: int | None = None,
    ) -> MemberEvent:
        event = MemberEvent(
            channel_id=channel_id,
            telegram_user_id=telegram_user_id,
            member_id=member_id,
            event_type=event_type,
            old_status=old_status,
            new_status=new_status,
            invite_link_id=invite_link_id,
        )

        self.session.add(event)
        await self.session.commit()
        await self.session.refresh(event)

        return event