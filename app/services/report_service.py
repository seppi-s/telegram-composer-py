from datetime import datetime, time, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.report_repository import ReportRepository


class ReportService:
    def __init__(self, session: AsyncSession):
        self.report_repository = ReportRepository(session)

    async def build_daily_report(self, channel_id: int) -> dict:
        now = datetime.now(timezone.utc)

        today_start = datetime.combine(
            now.date(),
            time.min,
            tzinfo=timezone.utc,
        )

        tomorrow_start = today_start + timedelta(days=1)
        seven_days_ago = now - timedelta(days=7)

        channel = await self.report_repository.get_channel(channel_id)

        today_counts = await self.report_repository.get_counts_between(
            channel_id=channel_id,
            start_time=today_start,
            end_time=tomorrow_start,
        )

        seven_day_counts = await self.report_repository.get_counts_between(
            channel_id=channel_id,
            start_time=seven_days_ago,
            end_time=now,
        )

        top_invite_links = await self.report_repository.get_top_invite_links_between(
            channel_id=channel_id,
            start_time=today_start,
            end_time=tomorrow_start,
            limit=5,
        )

        report = {
            "channel_id": channel_id,
            "title": channel.title if channel else None,
            "joined_today": today_counts["joined"],
            "left_today": today_counts["left"],
            "net_growth_today": today_counts["joined"] - today_counts["left"],
            "churn_rate_today": self._calculate_churn_rate(
                total_joined=today_counts["joined"],
                total_left=today_counts["left"],
            ),
            "joined_7d": seven_day_counts["joined"],
            "left_7d": seven_day_counts["left"],
            "net_growth_7d": seven_day_counts["joined"] - seven_day_counts["left"],
            "churn_rate_7d": self._calculate_churn_rate(
                total_joined=seven_day_counts["joined"],
                total_left=seven_day_counts["left"],
            ),
            "top_invite_links": [
                self._build_invite_link_item(item)
                for item in top_invite_links
            ],
        }

        report["text_report"] = self.format_daily_report(report)

        return report

    def _build_invite_link_item(self, item: dict) -> dict:
        joined = item["joined"]
        left = item["left"]

        return {
            "invite_link_id": item["invite_link_id"],
            "name": item["name"],
            "source": item["source"],
            "campaign": item["campaign"],
            "invite_link": item["invite_link"],
            "joined": joined,
            "left": left,
            "net_growth": joined - left,
            "churn_rate": self._calculate_churn_rate(
                total_joined=joined,
                total_left=left,
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

    def format_daily_report(self, report: dict) -> str:
        title = report["title"] or f"Channel {report['channel_id']}"

        lines = [
            f"📊 Daily Telegram Report",
            f"",
            f"Channel: {title}",
            f"",
            f"Today:",
            f"Joined: +{report['joined_today']}",
            f"Left: -{report['left_today']}",
            f"Net Growth: {report['net_growth_today']}",
            f"Churn Rate: {report['churn_rate_today']}%",
            f"",
            f"Last 7 Days:",
            f"Joined: +{report['joined_7d']}",
            f"Left: -{report['left_7d']}",
            f"Net Growth: {report['net_growth_7d']}",
            f"Churn Rate: {report['churn_rate_7d']}%",
            f"",
            f"Top Invite Links Today:",
        ]

        if not report["top_invite_links"]:
            lines.append("No invite link data today.")
        else:
            for index, item in enumerate(report["top_invite_links"], start=1):
                name = item["name"] or item["source"] or "Organic / Unknown"
                lines.append(
                    f"{index}. {name}: "
                    f"+{item['joined']} joined, "
                    f"-{item['left']} left, "
                    f"churn {item['churn_rate']}%"
                )

        return "\n".join(lines)
