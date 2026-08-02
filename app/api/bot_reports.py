from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.bot_report_service import BotReportService


class SendDailyReportRequest(BaseModel):
    target_chat_id: int


router = APIRouter(
    prefix="/channels",
    tags=["bot-reports"],
)


@router.post("/{channel_id}/bot/reports/daily/send")
async def send_daily_report_to_bot(
    channel_id: int,
    payload: SendDailyReportRequest,
    session: AsyncSession = Depends(get_db),
):
    service = BotReportService(session)

    try:
        return await service.send_daily_report(
            channel_id=channel_id,
            target_chat_id=payload.target_chat_id,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
