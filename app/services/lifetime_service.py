from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.member_repository import MemberRepository


class LifetimeService:
    def __init__(self, session: AsyncSession):
        self.member_repository = MemberRepository(session)

    async def list_member_lifetimes(self, channel_id: int) -> list[dict]:
        members = await self.member_repository.list_by_channel_id(channel_id)

        return [self._build_lifetime_response(member) for member in members]

    def _build_lifetime_response(self, member) -> dict:
        lifetime_seconds = self._calculate_lifetime_seconds(
            joined_at=member.joined_at,
            left_at=member.left_at,
        )

        return {
            "id": member.id,
            "channel_id": member.channel_id,
            "telegram_user_id": member.telegram_user_id,
            "username": member.username,
            "first_name": member.first_name,
            "last_name": member.last_name,
            "status": member.status,
            "joined_at": member.joined_at,
            "left_at": member.left_at,
            "lifetime_seconds": lifetime_seconds,
            "lifetime_human": self._format_duration(lifetime_seconds),
        }

    def _calculate_lifetime_seconds(
        self,
        joined_at: datetime | None,
        left_at: datetime | None,
    ) -> int | None:
        if joined_at is None:
            return None

        end_time = left_at or datetime.now(timezone.utc)

        if joined_at.tzinfo is None:
            joined_at = joined_at.replace(tzinfo=timezone.utc)

        if end_time.tzinfo is None:
            end_time = end_time.replace(tzinfo=timezone.utc)

        duration = end_time - joined_at

        return max(0, int(duration.total_seconds()))

    def _format_duration(self, seconds: int | None) -> str | None:
        if seconds is None:
            return None

        days = seconds // 86400
        remaining = seconds % 86400

        hours = remaining // 3600
        remaining = remaining % 3600

        minutes = remaining // 60
        secs = remaining % 60

        if days > 0:
            return f"{days}d {hours}h {minutes}m"

        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"

        if minutes > 0:
            return f"{minutes}m {secs}s"

        return f"{secs}s"
