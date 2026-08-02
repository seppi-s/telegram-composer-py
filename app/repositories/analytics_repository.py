from datetime import datetime, timedelta, timezone

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.invite_link import InviteLink
from app.models.member_event import MemberEvent


class AnalyticsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_growth_stats(self, channel_id: int) -> dict:
        stmt = select(
            func.count(
                case(
                    (MemberEvent.event_type == "joined", 1),
                    else_=None,
                )
            ).label("total_joined"),
            func.count(
                case(
                    (MemberEvent.event_type.in_(["left", "kicked"]), 1),
                    else_=None,
                )
            ).label("total_left"),
        ).where(MemberEvent.channel_id == channel_id)

        result = await self.session.execute(stmt)
        row = result.one()

        total_joined = row.total_joined or 0
        total_left = row.total_left or 0

        return {
            "total_joined": total_joined,
            "total_left": total_left,
        }

    async def get_growth_stats_since(
        self,
        channel_id: int,
        since: datetime,
    ) -> dict:
        stmt = select(
            func.count(
                case(
                    (MemberEvent.event_type == "joined", 1),
                    else_=None,
                )
            ).label("total_joined"),
            func.count(
                case(
                    (MemberEvent.event_type.in_(["left", "kicked"]), 1),
                    else_=None,
                )
            ).label("total_left"),
        ).where(
            MemberEvent.channel_id == channel_id,
            MemberEvent.occurred_at >= since,
        )

        result = await self.session.execute(stmt)
        row = result.one()

        total_joined = row.total_joined or 0
        total_left = row.total_left or 0

        return {
            "total_joined": total_joined,
            "total_left": total_left,
        }

    async def get_7_day_growth_stats(self, channel_id: int) -> dict:
        since = datetime.now(timezone.utc) - timedelta(days=7)

        return await self.get_growth_stats_since(
            channel_id=channel_id,
            since=since,
        )

    async def get_growth_by_invite_link(self, channel_id: int) -> list[dict]:
        joined_count = func.count(
            case(
                (MemberEvent.event_type == "joined", 1),
                else_=None,
            )
        ).label("total_joined")

        left_count = func.count(
            case(
                (MemberEvent.event_type.in_(["left", "kicked"]), 1),
                else_=None,
            )
        ).label("total_left")

        stmt = (
            select(
                MemberEvent.invite_link_id,
                InviteLink.invite_link,
                InviteLink.name,
                InviteLink.source,
                InviteLink.campaign,
                joined_count,
                left_count,
            )
            .outerjoin(
                InviteLink,
                InviteLink.id == MemberEvent.invite_link_id,
            )
            .where(MemberEvent.channel_id == channel_id)
            .group_by(
                MemberEvent.invite_link_id,
                InviteLink.invite_link,
                InviteLink.name,
                InviteLink.source,
                InviteLink.campaign,
            )
            .order_by(joined_count.desc())
        )

        result = await self.session.execute(stmt)
        rows = result.all()

        return [
            {
                "invite_link_id": row.invite_link_id,
                "invite_link": row.invite_link,
                "name": row.name,
                "source": row.source,
                "campaign": row.campaign,
                "total_joined": row.total_joined or 0,
                "total_left": row.total_left or 0,
            }
            for row in rows
        ]
