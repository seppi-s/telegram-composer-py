from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.analytics_repository import AnalyticsRepository


class AnalyticsService:
    def __init__(self, session: AsyncSession):
        self.analytics_repository = AnalyticsRepository(session)

    async def get_summary(self, channel_id: int) -> dict:
        growth = await self.analytics_repository.get_growth_stats(channel_id)
        seven_day_growth = await self.analytics_repository.get_7_day_growth_stats(
            channel_id
        )
        growth_by_invite_link = (
            await self.analytics_repository.get_growth_by_invite_link(channel_id)
        )

        return {
            "growth": self._build_growth_response(
                channel_id=channel_id,
                total_joined=growth["total_joined"],
                total_left=growth["total_left"],
            ),
            "seven_day_growth": self._build_7_day_growth_response(
                channel_id=channel_id,
                total_joined=seven_day_growth["total_joined"],
                total_left=seven_day_growth["total_left"],
            ),
            "growth_by_invite_link": [
                self._build_invite_link_growth_response(item)
                for item in growth_by_invite_link
            ],
        }

    def _build_growth_response(
        self,
        channel_id: int,
        total_joined: int,
        total_left: int,
    ) -> dict:
        net_growth = total_joined - total_left

        return {
            "channel_id": channel_id,
            "total_joined": total_joined,
            "total_left": total_left,
            "net_growth": net_growth,
            "churn_rate": self._calculate_churn_rate(
                total_joined=total_joined,
                total_left=total_left,
            ),
        }

    def _build_7_day_growth_response(
        self,
        channel_id: int,
        total_joined: int,
        total_left: int,
    ) -> dict:
        net_growth = total_joined - total_left

        return {
            "channel_id": channel_id,
            "total_joined_7d": total_joined,
            "total_left_7d": total_left,
            "net_growth_7d": net_growth,
            "churn_rate_7d": self._calculate_churn_rate(
                total_joined=total_joined,
                total_left=total_left,
            ),
        }

    def _build_invite_link_growth_response(self, item: dict) -> dict:
        total_joined = item["total_joined"]
        total_left = item["total_left"]
        net_growth = total_joined - total_left

        return {
            "invite_link_id": item["invite_link_id"],
            "invite_link": item["invite_link"],
            "name": item["name"],
            "source": item["source"],
            "campaign": item["campaign"],
            "total_joined": total_joined,
            "total_left": total_left,
            "net_growth": net_growth,
            "churn_rate": self._calculate_churn_rate(
                total_joined=total_joined,
                total_left=total_left,
            ),
        }

    def _calculate_churn_rate(
        self,
        total_joined: int,
        total_left: int,
    ) -> float:
        if total_joined == 0:
            return 0.0

        return round((total_left / total_joined) * 100, 2)
