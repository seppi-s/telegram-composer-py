from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.channel_repository import ChannelRepository
from app.repositories.post_repository import PostRepository
from app.services.post_stats_service import PostStatsService


class PostStatsStorageService:
    def __init__(self, session: AsyncSession):
        self.channel_repository = ChannelRepository(session)
        self.post_repository = PostRepository(session)
        self.post_stats_service = PostStatsService()

    async def fetch_and_store_latest_posts(
        self,
        channel_id: int,
        limit: int = 10,
    ) -> dict:
        channel = await self.channel_repository.get_by_id(channel_id)

        if channel is None:
            raise ValueError("Channel not found")

        posts = await self.post_stats_service.fetch_latest_post_stats(
            channel=None,
            limit=limit,
        )

        saved_posts = []

        for item in posts:
            post = await self.post_repository.upsert_post(
                channel_id=channel.id,
                telegram_channel_id=channel.telegram_chat_id,
                telegram_message_id=item["message_id"],
                text_preview=item["text_preview"],
                posted_at=item["date"],
            )

            snapshot = await self.post_repository.create_snapshot(
                post_id=post.id,
                views=item["views"],
                forwards=item["forwards"],
                reactions_count=item["reactions_count"],
            )

            saved_posts.append(
                {
                    "post_id": post.id,
                    "telegram_message_id": post.telegram_message_id,
                    "snapshot_id": snapshot.id,
                    "views": snapshot.views,
                    "forwards": snapshot.forwards,
                    "reactions_count": snapshot.reactions_count,
                }
            )

        return {
            "channel_id": channel_id,
            "stored_count": len(saved_posts),
            "posts": saved_posts,
        }