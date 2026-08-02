from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.member import Member


class MemberRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_channel_and_user(
        self,
        channel_id: int,
        telegram_user_id: int,
    ) -> Member | None:
        result = await self.session.execute(
            select(Member).where(
                Member.channel_id == channel_id,
                Member.telegram_user_id == telegram_user_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_by_channel_id(self, channel_id: int) -> list[Member]:
        result = await self.session.execute(
            select(Member)
            .where(Member.channel_id == channel_id)
            .order_by(Member.id.desc())
        )
        return list(result.scalars().all())

    async def upsert_member(
        self,
        channel_id: int,
        telegram_user_id: int,
        username: str | None,
        first_name: str | None,
        last_name: str | None,
        status: str,
        event_type: str,
    ) -> Member:
        now = datetime.now(timezone.utc)

        member = await self.get_by_channel_and_user(
            channel_id=channel_id,
            telegram_user_id=telegram_user_id,
        )

        if member is None:
            member = Member(
                channel_id=channel_id,
                telegram_user_id=telegram_user_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                status=status,
                joined_at=now if event_type == "joined" else None,
                left_at=now if event_type in ("left", "kicked") else None,
            )

            self.session.add(member)
            await self.session.commit()
            await self.session.refresh(member)

            return member

        member.username = username
        member.first_name = first_name
        member.last_name = last_name
        member.status = status

        if event_type == "joined":
            member.joined_at = now
            member.left_at = None

        if event_type in ("left", "kicked"):
            member.left_at = now

        await self.session.commit()
        await self.session.refresh(member)

        return member