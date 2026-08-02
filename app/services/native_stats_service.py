from typing import Any

from telethon import functions
from telethon.tl.types import Channel, StatsGraph, StatsGraphAsync, StatsGraphError

from app.config import settings
from app.telegram.mtproto_client import create_mtproto_client


class NativeStatsService:
    def __init__(self):
        self.client = create_mtproto_client()

    async def check_channel_stats_eligibility(
        self,
        channel: str | int | None = None,
    ) -> dict[str, Any]:
        target_channel = channel or settings.mtproto_target_channel

        if not target_channel:
            raise ValueError("MTPROTO_TARGET_CHANNEL is missing in .env")

        async with self.client:
            entity = await self.client.get_entity(target_channel)

            full = await self.client(
                functions.channels.GetFullChannelRequest(
                    channel=entity,
                )
            )

            full_chat = full.full_chat

            return {
                "channel_id": getattr(entity, "id", None),
                "title": getattr(entity, "title", None),
                "username": getattr(entity, "username", None),
                "broadcast": getattr(entity, "broadcast", None),
                "megagroup": getattr(entity, "megagroup", None),
                "can_view_stats": getattr(full_chat, "can_view_stats", False),
                "stats_dc": getattr(full_chat, "stats_dc", None),
                "participants_count": getattr(full_chat, "participants_count", None),
            }

    async def fetch_broadcast_stats(
        self,
        channel: str | int | None = None,
    ) -> dict[str, Any]:
        target_channel = channel or settings.mtproto_target_channel

        if not target_channel:
            raise ValueError("MTPROTO_TARGET_CHANNEL is missing in .env")

        async with self.client:
            entity = await self.client.get_entity(target_channel)

            if not isinstance(entity, Channel):
                raise ValueError("Target is not a channel/supergroup")

            full = await self.client(
                functions.channels.GetFullChannelRequest(
                    channel=entity,
                )
            )

            can_view_stats = getattr(full.full_chat, "can_view_stats", False)

            if not can_view_stats:
                return {
                    "ok": False,
                    "reason": "can_view_stats is false",
                    "channel_id": entity.id,
                    "title": getattr(entity, "title", None),
                    "username": getattr(entity, "username", None),
                    "broadcast": getattr(entity, "broadcast", None),
                    "megagroup": getattr(entity, "megagroup", None),
                    "stats_dc": getattr(full.full_chat, "stats_dc", None),
                }

            if getattr(entity, "megagroup", False):
                stats = await self.client(
                    functions.stats.GetMegagroupStatsRequest(
                        channel=entity,
                    )
                )
                stats_type = "megagroup"
            else:
                stats = await self.client(
                    functions.stats.GetBroadcastStatsRequest(
                        channel=entity,
                    )
                )
                stats_type = "broadcast"

            return {
                "ok": True,
                "stats_type": stats_type,
                "channel_id": entity.id,
                "title": getattr(entity, "title", None),
                "username": getattr(entity, "username", None),
                "summary": self._summarize_stats(stats),
                "raw_type": type(stats).__name__,
            }

    async def fetch_message_stats(
        self,
        message_id: int,
        channel: str | int | None = None,
    ) -> dict[str, Any]:
        target_channel = channel or settings.mtproto_target_channel

        if not target_channel:
            raise ValueError("MTPROTO_TARGET_CHANNEL is missing in .env")

        async with self.client:
            entity = await self.client.get_entity(target_channel)

            full = await self.client(
                functions.channels.GetFullChannelRequest(
                    channel=entity,
                )
            )

            can_view_stats = getattr(full.full_chat, "can_view_stats", False)

            if not can_view_stats:
                return {
                    "ok": False,
                    "reason": "can_view_stats is false",
                    "channel_id": entity.id,
                    "message_id": message_id,
                    "stats_dc": getattr(full.full_chat, "stats_dc", None),
                }

            stats = await self.client(
                functions.stats.GetMessageStatsRequest(
                    channel=entity,
                    msg_id=message_id,
                )
            )

            return {
                "ok": True,
                "channel_id": entity.id,
                "message_id": message_id,
                "raw_type": type(stats).__name__,
                "summary": self._summarize_message_stats(stats),
            }

    def _summarize_stats(self, stats: Any) -> dict[str, Any]:
        summary: dict[str, Any] = {}

        for attr in [
            "period",
            "followers",
            "views_per_post",
            "shares_per_post",
            "enabled_notifications",
            "recent_message_interactions",
        ]:
            value = getattr(stats, attr, None)

            if value is not None:
                summary[attr] = self._safe_value(value)

        return summary

    def _summarize_message_stats(self, stats: Any) -> dict[str, Any]:
        summary: dict[str, Any] = {}

        for attr in [
            "views_graph",
            "reactions_by_emotion_graph",
        ]:
            value = getattr(stats, attr, None)

            if value is not None:
                summary[attr] = self._safe_graph_value(value)

        return summary

    def _safe_graph_value(self, value: Any) -> dict[str, Any]:
        if isinstance(value, StatsGraph):
            return {
                "type": "StatsGraph",
                "json": getattr(value, "json", None),
            }

        if isinstance(value, StatsGraphAsync):
            return {
                "type": "StatsGraphAsync",
                "token": getattr(value, "token", None),
            }

        if isinstance(value, StatsGraphError):
            return {
                "type": "StatsGraphError",
                "error": getattr(value, "error", None),
            }

        return {
            "type": type(value).__name__,
            "value": str(value),
        }

    def _safe_value(self, value: Any) -> Any:
        if isinstance(value, list):
            return [self._safe_value(item) for item in value]

        if hasattr(value, "to_dict"):
            return value.to_dict()

        if hasattr(value, "__dict__"):
            return {
                key: self._safe_value(val)
                for key, val in value.__dict__.items()
                if not key.startswith("_")
            }

        return value
