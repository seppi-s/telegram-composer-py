from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.post_stats import FetchPostStatsResponse, PostStatsResponse
from app.services.post_stats_query_service import PostStatsQueryService
from app.services.post_stats_storage_service import PostStatsStorageService


router = APIRouter(
    prefix="/channels",
    tags=["post-stats"],
)


@router.get(
    "/{channel_id}/posts/stats",
    response_model=list[PostStatsResponse],
)
async def list_post_stats(
    channel_id: int,
    snapshots_limit: int = Query(default=5, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
):
    service = PostStatsQueryService(session)

    return await service.list_post_stats(
        channel_id=channel_id,
        snapshots_limit=snapshots_limit,
    )


@router.post(
    "/{channel_id}/posts/stats/fetch",
    response_model=FetchPostStatsResponse,
)
async def fetch_and_store_post_stats(
    channel_id: int,
    limit: int = Query(default=10, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
):
    service = PostStatsStorageService(session)

    try:
        return await service.fetch_and_store_latest_posts(
            channel_id=channel_id,
            limit=limit,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
