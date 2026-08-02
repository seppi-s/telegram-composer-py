from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.post_repository import PostRepository


class PostStatsQueryService:
    def __init__(self, session: AsyncSession):
        self.post_repository = PostRepository(session)

    async def list_post_stats(
        self,
        channel_id: int,
        snapshots_limit: int = 5,
    ) -> list[dict]:
        posts = await self.post_repository.list_by_channel_id(channel_id)

        response = []

        for post in posts:
            latest_snapshot = await self.post_repository.get_latest_snapshot(post.id)
            snapshots = await self.post_repository.list_snapshots_by_post_id(
                post_id=post.id,
                limit=snapshots_limit,
            )

            response.append(
                {
                    "id": post.id,
                    "channel_id": post.channel_id,
                    "telegram_channel_id": post.telegram_channel_id,
                    "telegram_message_id": post.telegram_message_id,
                    "text_preview": post.text_preview,
                    "posted_at": post.posted_at,
                    "latest_views": latest_snapshot.views if latest_snapshot else None,
                    "latest_forwards": latest_snapshot.forwards if latest_snapshot else None,
                    "latest_reactions_count": (
                        latest_snapshot.reactions_count if latest_snapshot else None
                    ),
                    "latest_captured_at": (
                        latest_snapshot.captured_at if latest_snapshot else None
                    ),
                    "snapshots": [
                        {
                            "id": snapshot.id,
                            "views": snapshot.views,
                            "forwards": snapshot.forwards,
                            "reactions_count": snapshot.reactions_count,
                            "captured_at": snapshot.captured_at,
                        }
                        for snapshot in snapshots
                    ],
                }
            )

        return response
