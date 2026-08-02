from datetime import datetime

from pydantic import BaseModel


class PostStatsSnapshotResponse(BaseModel):
    id: int
    views: int | None = None
    forwards: int | None = None
    reactions_count: int | None = None
    captured_at: datetime


class PostStatsResponse(BaseModel):
    id: int
    channel_id: int
    telegram_channel_id: int
    telegram_message_id: int
    text_preview: str | None = None
    posted_at: datetime | None = None
    latest_views: int | None = None
    latest_forwards: int | None = None
    latest_reactions_count: int | None = None
    latest_captured_at: datetime | None = None
    snapshots: list[PostStatsSnapshotResponse] = []


class FetchPostStatsResponse(BaseModel):
    channel_id: int
    stored_count: int
    posts: list[dict]
