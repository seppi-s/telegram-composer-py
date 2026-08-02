import asyncio

from app.services.post_stats_service import PostStatsService


async def main() -> None:
    service = PostStatsService()

    print("Listing admin channels...")
    channels = await service.list_admin_channels()

    for channel in channels:
        print(
            f"- id={channel['id']} "
            f"title={channel['title']} "
            f"username={channel['username']} "
            f"broadcast={channel['broadcast']} "
            f"megagroup={channel['megagroup']}"
        )

    print("")
    print("Fetching latest post stats...")

    posts = await service.fetch_latest_post_stats(limit=10)

    for post in posts:
        print(
            f"message_id={post['message_id']} | "
            f"date={post['date']} | "
            f"views={post['views']} | "
            f"forwards={post['forwards']} | "
            f"reactions={post['reactions_count']} | "
            f"text={post['text_preview']}"
        )


if __name__ == "__main__":
    asyncio.run(main())
