from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.invite_link import InviteLink


class InviteLinkRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_invite_link(self, invite_link: str) -> InviteLink | None:
        result = await self.session.execute(
            select(InviteLink).where(InviteLink.invite_link == invite_link)
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        channel_id: int,
        invite_link: str,
        name: str | None,
        source: str | None,
        campaign: str | None,
    ) -> InviteLink:
        item = InviteLink(
            channel_id=channel_id,
            invite_link=invite_link,
            name=name,
            source=source,
            campaign=campaign,
        )

        self.session.add(item)
        await self.session.commit()
        await self.session.refresh(item)

        return item

    async def upsert(
        self,
        channel_id: int,
        invite_link: str,
        name: str | None,
        source: str | None,
        campaign: str | None,
    ) -> InviteLink:
        item = await self.get_by_invite_link(invite_link)

        if item is None:
            return await self.create(
                channel_id=channel_id,
                invite_link=invite_link,
                name=name,
                source=source,
                campaign=campaign,
            )

        item.channel_id = channel_id
        item.name = name
        item.source = source
        item.campaign = campaign

        await self.session.commit()
        await self.session.refresh(item)

        return item
