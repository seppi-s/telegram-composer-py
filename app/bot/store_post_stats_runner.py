import asyncio
import os

from app.db.session import AsyncSessionLocal
from app.services.post_stats_storage_service import PostStatsStorageService


async def main() -> None:
    channel_id = int(os.getenv("POST_STATS_CHANNEL_ID", "2"))
    limit = int(os.getenv("POST_STATS_LIMIT", "10"))

    async with AsyncSessionLocal() as session:
        service = PostStatsStorageService(session)

        result = await service.fetch_and_store_latest_posts(
            channel_id=channel_id,
            limit=limit,
        )

        print("Post stats stored successfully")
        print("Channel ID:", result["channel_id"])
        print("Stored count:", result["stored_count"])

        for post in result["posts"]:
            print(
                f"message_id={post['telegram_message_id']} "
                f"post_id={post['post_id']} "
                f"snapshot_id={post['snapshot_id']} "
                f"views={post['views']} "
                f"forwards={post['forwards']} "
                f"reactions={post['reactions_count']}"
            )


if __name__ == "__main__":
    asyncio.run(main())
