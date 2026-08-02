from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.post import Post
from app.models.post_stats_snapshot import PostStatsSnapshot


class PostRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_channel_and_message_id(
        self,
        channel_id: int,
        telegram_message_id: int,
    ) -> Post | None:
        result = await self.session.execute(
            select(Post).where(
                Post.channel_id == channel_id,
                Post.telegram_message_id == telegram_message_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_by_channel_id(self, channel_id: int) -> list[Post]:
        result = await self.session.execute(
            select(Post)
            .where(Post.channel_id == channel_id)
            .order_by(Post.telegram_message_id.desc())
        )
        return list(result.scalars().all())

    async def list_snapshots_by_post_id(
        self,
        post_id: int,
        limit: int = 20,
    ) -> list[PostStatsSnapshot]:
        result = await self.session.execute(
            select(PostStatsSnapshot)
            .where(PostStatsSnapshot.post_id == post_id)
            .order_by(PostStatsSnapshot.captured_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_latest_snapshot(
        self,
        post_id: int,
    ) -> PostStatsSnapshot | None:
        result = await self.session.execute(
            select(PostStatsSnapshot)
            .where(PostStatsSnapshot.post_id == post_id)
            .order_by(PostStatsSnapshot.captured_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def upsert_post(
        self,
        channel_id: int,
        telegram_channel_id: int,
        telegram_message_id: int,
        text_preview: str | None,
        posted_at: datetime | None,
    ) -> Post:
        post = await self.get_by_channel_and_message_id(
            channel_id=channel_id,
            telegram_message_id=telegram_message_id,
        )

        if post is None:
            post = Post(
                channel_id=channel_id,
                telegram_channel_id=telegram_channel_id,
                telegram_message_id=telegram_message_id,
                text_preview=text_preview,
                posted_at=posted_at,
            )

            self.session.add(post)
            await self.session.commit()
            await self.session.refresh(post)

            return post

        post.text_preview = text_preview
        post.posted_at = posted_at

        await self.session.commit()
        await self.session.refresh(post)

        return post

    async def create_snapshot(
        self,
        post_id: int,
        views: int | None,
        forwards: int | None,
        reactions_count: int | None,
    ) -> PostStatsSnapshot:
        snapshot = PostStatsSnapshot(
            post_id=post_id,
            views=views,
            forwards=forwards,
            reactions_count=reactions_count,
        )

        self.session.add(snapshot)
        await self.session.commit()
        await self.session.refresh(snapshot)

        return snapshot
