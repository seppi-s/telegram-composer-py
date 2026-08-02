from datetime import datetime

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.channel import Channel
from app.models.invite_link import InviteLink
from app.models.member_event import MemberEvent


class ReportRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_channel(self, channel_id: int) -> Channel | None:
        result = await self.session.execute(
            select(Channel).where(Channel.id == channel_id)
        )
        return result.scalar_one_or_none()

    async def get_counts_between(
        self,
        channel_id: int,
        start_time: datetime,
        end_time: datetime,
    ) -> dict:
        stmt = select(
            func.count(
                case(
                    (MemberEvent.event_type == "joined", 1),
                    else_=None,
                )
            ).label("joined"),
            func.count(
                case(
                    (MemberEvent.event_type.in_(["left", "kicked"]), 1),
                    else_=None,
                )
            ).label("left"),
        ).where(
            MemberEvent.channel_id == channel_id,
            MemberEvent.occurred_at >= start_time,
            MemberEvent.occurred_at < end_time,
        )

        result = await self.session.execute(stmt)
        row = result.one()

        return {
            "joined": row.joined or 0,
            "left": row.left or 0,
        }

    async def get_top_invite_links_between(
        self,
        channel_id: int,
        start_time: datetime,
        end_time: datetime,
        limit: int = 5,
    ) -> list[dict]:
        joined_count = func.count(
            case(
                (MemberEvent.event_type == "joined", 1),
                else_=None,
            )
        ).label("joined")

        left_count = func.count(
            case(
                (MemberEvent.event_type.in_(["left", "kicked"]), 1),
                else_=None,
            )
        ).label("left")

        stmt = (
            select(
                MemberEvent.invite_link_id,
                InviteLink.name,
                InviteLink.source,
                InviteLink.campaign,
                InviteLink.invite_link,
                joined_count,
                left_count,
            )
            .outerjoin(
                InviteLink,
                InviteLink.id == MemberEvent.invite_link_id,
            )
            .where(
                MemberEvent.channel_id == channel_id,
                MemberEvent.occurred_at >= start_time,
                MemberEvent.occurred_at < end_time,
            )
            .group_by(
                MemberEvent.invite_link_id,
                InviteLink.name,
                InviteLink.source,
                InviteLink.campaign,
                InviteLink.invite_link,
            )
            .order_by(joined_count.desc())
            .limit(limit)
        )

        result = await self.session.execute(stmt)

        return [
            {
                "invite_link_id": row.invite_link_id,
                "name": row.name,
                "source": row.source,
                "campaign": row.campaign,
                "invite_link": row.invite_link,
                "joined": row.joined or 0,
                "left": row.left or 0,
            }
            for row in result.all()
        ]
