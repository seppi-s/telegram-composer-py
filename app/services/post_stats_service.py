from typing import Any

from telethon.tl.types import Channel

from app.config import settings
from app.telegram.mtproto_client import create_mtproto_client


class PostStatsService:
    def __init__(self):
        self.client = create_mtproto_client()

    async def list_admin_channels(self) -> list[dict[str, Any]]:
        channels: list[dict[str, Any]] = []

        async with self.client:
            async for dialog in self.client.iter_dialogs():
                entity = dialog.entity

                if not isinstance(entity, Channel):
                    continue

                # broadcast=True means normal channel.
                # megagroup=True means supergroup.
                if not getattr(entity, "creator", False) and not getattr(entity, "admin_rights", None):
                    continue

                channels.append(
                    {
                        "id": entity.id,
                        "title": getattr(entity, "title", None),
                        "username": getattr(entity, "username", None),
                        "broadcast": getattr(entity, "broadcast", None),
                        "megagroup": getattr(entity, "megagroup", None),
                    }
                )

        return channels

    async def fetch_latest_post_stats(
        self,
        channel: str | int | None = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        target_channel = channel or settings.mtproto_target_channel

        if not target_channel:
            raise ValueError("MTPROTO_TARGET_CHANNEL is missing in .env")

        posts: list[dict[str, Any]] = []

        async with self.client:
            entity = await self.client.get_entity(target_channel)

            async for message in self.client.iter_messages(entity, limit=limit):
                reactions_count = self._count_reactions(message)

                posts.append(
                    {
                        "message_id": message.id,
                        "date": message.date,
                        "text_preview": self._preview(message.message),
                        "views": message.views,
                        "forwards": message.forwards,
                        "reactions_count": reactions_count,
                    }
                )

        return posts

    def _preview(self, text: str | None, max_len: int = 80) -> str | None:
        if not text:
            return None

        text = text.replace("\n", " ").strip()

        if len(text) <= max_len:
            return text

        return text[:max_len] + "..."

    def _count_reactions(self, message) -> int | None:
        reactions = getattr(message, "reactions", None)

        if not reactions:
            return None

        results = getattr(reactions, "results", None)

        if not results:
            return 0

        total = 0

        for item in results:
            count = getattr(item, "count", 0) or 0
            total += count

        return total
