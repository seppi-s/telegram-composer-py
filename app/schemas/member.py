from datetime import datetime

from pydantic import BaseModel


class MemberLifetimeResponse(BaseModel):
    id: int
    channel_id: int
    telegram_user_id: int
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    status: str
    joined_at: datetime | None = None
    left_at: datetime | None = None
    lifetime_seconds: int | None = None
    lifetime_human: str | None = None
