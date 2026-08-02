import asyncio

from app.config import settings
from app.db.session import AsyncSessionLocal
from app.services.bot_report_service import BotReportService


def parse_target_chat_ids() -> list[int]:
    if settings.report_target_chat_ids:
        chat_ids: list[int] = []

        for item in settings.report_target_chat_ids.split(","):
            item = item.strip()

            if not item:
                continue

            chat_ids.append(int(item))

        if chat_ids:
            return chat_ids

    if settings.report_target_chat_id is not None:
        return [settings.report_target_chat_id]

    raise ValueError(
        "You must set REPORT_TARGET_CHAT_ID or REPORT_TARGET_CHAT_IDS in .env"
    )


async def run_daily_report(channel_id: int, target_chat_ids: list[int]) -> None:
    async with AsyncSessionLocal() as session:
        service = BotReportService(session)

        for target_chat_id in target_chat_ids:
            try:
                result = await service.send_daily_report(
                    channel_id=channel_id,
                    target_chat_id=target_chat_id,
                )

                print("Daily report sent successfully")
                print("Target chat id:", result["target_chat_id"])

            except Exception as exc:
                print(f"Failed to send report to {target_chat_id}: {exc}")


async def main() -> None:
    if settings.report_channel_id is None:
        raise ValueError("REPORT_CHANNEL_ID is missing in .env")

    target_chat_ids = parse_target_chat_ids()

    await run_daily_report(
        channel_id=settings.report_channel_id,
        target_chat_ids=target_chat_ids,
    )


if __name__ == "__main__":
    asyncio.run(main())