import httpx

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.services.report_service import ReportService


class BotReportService:
    def __init__(self, session: AsyncSession):
        self.report_service = ReportService(session)
        self.base_url = f"https://api.telegram.org/bot{settings.bot_token}"

    async def send_daily_report(
        self,
        channel_id: int,
        target_chat_id: int,
    ) -> dict:
        report = await self.report_service.build_daily_report(channel_id)

        payload = {
            "chat_id": target_chat_id,
            "text": report["text_report"],
            "parse_mode": "HTML",
        }

        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.post(
                f"{self.base_url}/sendMessage",
                json=payload,
            )

        data = response.json()

        if not data.get("ok"):
            raise RuntimeError(f"Telegram sendMessage failed: {data}")

        return {
            "sent": True,
            "target_chat_id": target_chat_id,
            "report": report,
        }
