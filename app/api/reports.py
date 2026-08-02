from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.report import DailyReportResponse
from app.services.report_service import ReportService


router = APIRouter(
    prefix="/channels",
    tags=["reports"],
)


@router.get(
    "/{channel_id}/reports/daily",
    response_model=DailyReportResponse,
)
async def get_daily_report(
    channel_id: int,
    session: AsyncSession = Depends(get_db),
):
    service = ReportService(session)

    return await service.build_daily_report(channel_id)
