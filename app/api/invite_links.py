from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.invite_link import CreateInviteLinkRequest, InviteLinkResponse
from app.services.invite_link_service import InviteLinkService


router = APIRouter(
    prefix="/channels",
    tags=["invite-links"],
)


@router.post(
    "/{channel_id}/invite-links",
    response_model=InviteLinkResponse,
)
async def create_invite_link(
    channel_id: int,
    payload: CreateInviteLinkRequest,
    session: AsyncSession = Depends(get_db),
):
    service = InviteLinkService(session)

    try:
        invite_link = await service.create_invite_link(
            channel_id=channel_id,
            name=payload.name,
            source=payload.source,
            campaign=payload.campaign,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return invite_link
