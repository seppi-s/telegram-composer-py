from fastapi import APIRouter, HTTPException, Query

from app.services.native_stats_service import NativeStatsService
from app.services.post_stats_service import PostStatsService


router = APIRouter(
    prefix="/mtproto",
    tags=["mtproto"],
)


@router.get("/admin-channels")
async def list_admin_channels():
    service = PostStatsService()

    return await service.list_admin_channels()


@router.get("/native-stats/eligibility")
async def check_native_stats_eligibility(
    channel: str | None = Query(default=None),
):
    service = NativeStatsService()

    try:
        return await service.check_channel_stats_eligibility(channel=channel)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/native-stats/channel")
async def get_native_channel_stats(
    channel: str | None = Query(default=None),
):
    service = NativeStatsService()

    try:
        return await service.fetch_broadcast_stats(channel=channel)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/native-stats/messages/{message_id}")
async def get_native_message_stats(
    message_id: int,
    channel: str | None = Query(default=None),
):
    service = NativeStatsService()

    try:
        return await service.fetch_message_stats(
            channel=channel,
            message_id=message_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
