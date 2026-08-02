from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.analytics import AnalyticsSummaryResponse
from app.services.analytics_service import AnalyticsService


router = APIRouter(
    prefix="/channels",
    tags=["analytics"],
)


@router.get(
    "/{channel_id}/analytics/summary",
    response_model=AnalyticsSummaryResponse,
)
async def get_analytics_summary(
    channel_id: int,
    session: AsyncSession = Depends(get_db),
):
    service = AnalyticsService(session)

    return await service.get_summary(channel_id)
