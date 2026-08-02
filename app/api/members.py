from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.member import MemberLifetimeResponse
from app.services.lifetime_service import LifetimeService


router = APIRouter(
    prefix="/channels",
    tags=["members"],
)


@router.get(
    "/{channel_id}/members/lifetimes",
    response_model=list[MemberLifetimeResponse],
)
async def list_member_lifetimes(
    channel_id: int,
    session: AsyncSession = Depends(get_db),
):
    service = LifetimeService(session)

    return await service.list_member_lifetimes(channel_id)
