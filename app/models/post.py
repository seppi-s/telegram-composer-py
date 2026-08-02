from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    channel_id: Mapped[int] = mapped_column(
        ForeignKey("channels.id"),
        index=True,
        nullable=False,
    )

    telegram_channel_id: Mapped[int] = mapped_column(
        BigInteger,
        index=True,
        nullable=False,
    )

    telegram_message_id: Mapped[int] = mapped_column(
        Integer,
        index=True,
        nullable=False,
    )

    text_preview: Mapped[str | None] = mapped_column(Text, nullable=True)

    posted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "channel_id",
            "telegram_message_id",
            name="uq_posts_channel_message",
        ),
    )
