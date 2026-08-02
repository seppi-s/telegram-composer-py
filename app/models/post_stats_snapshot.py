from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PostStatsSnapshot(Base):
    __tablename__ = "post_stats_snapshots"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id"),
        index=True,
        nullable=False,
    )

    views: Mapped[int | None] = mapped_column(Integer, nullable=True)
    forwards: Mapped[int | None] = mapped_column(Integer, nullable=True)
    reactions_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    captured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
