import asyncio

from app.services.native_stats_service import NativeStatsService
from app.services.post_stats_service import PostStatsService


async def main() -> None:
    native_service = NativeStatsService()
    post_service = PostStatsService()

    print("Checking channel stats eligibility...")
    eligibility = await native_service.check_channel_stats_eligibility()
    print(eligibility)

    print("")
    print("Trying channel native stats...")
    broadcast_stats = await native_service.fetch_broadcast_stats()
    print(broadcast_stats)

    print("")
    print("Fetching latest posts to test message stats...")
    posts = await post_service.fetch_latest_post_stats(limit=3)

    for post in posts:
        message_id = post["message_id"]

        print("")
        print(f"Trying native message stats for message_id={message_id}...")

        message_stats = await native_service.fetch_message_stats(
            message_id=message_id,
        )

        print(message_stats)


if __name__ == "__main__":
    asyncio.run(main())
