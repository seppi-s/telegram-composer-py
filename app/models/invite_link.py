from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class InviteLink(Base):
    __tablename__ = "invite_links"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    channel_id: Mapped[int] = mapped_column(
        ForeignKey("channels.id"),
        index=True,
        nullable=False,
    )

    invite_link: Mapped[str] = mapped_column(
        String(500),
        unique=True,
        nullable=False,
    )

    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source: Mapped[str | None] = mapped_column(String(255), nullable=True)
    campaign: Mapped[str | None] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )