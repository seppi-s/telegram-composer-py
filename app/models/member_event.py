from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class MemberEvent(Base):
    __tablename__ = "member_events"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    channel_id: Mapped[int] = mapped_column(
        ForeignKey("channels.id"),
        index=True,
        nullable=False,
    )

    telegram_user_id: Mapped[int] = mapped_column(
        BigInteger,
        index=True,
        nullable=False,
    )

    member_id: Mapped[int | None] = mapped_column(
        ForeignKey("members.id"),
        nullable=True,
    )

    invite_link_id: Mapped[int | None] = mapped_column(
        ForeignKey("invite_links.id"),
        nullable=True,
    )

    event_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    old_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    new_status: Mapped[str | None] = mapped_column(String(50), nullable=True)

    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )