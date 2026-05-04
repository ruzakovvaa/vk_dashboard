from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Index, Integer, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# TIMESTAMPTZ через DateTime(timezone=True) — совместимо со всеми версиями SQLAlchemy
TIMESTAMPTZ = DateTime(timezone=True)


class Base(DeclarativeBase):
    pass


class GroupRaw(Base):
    """Снапшоты метаданных сообщества (подписчики на дату)."""

    __tablename__ = "groups_raw"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    group_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    screen_name: Mapped[str | None] = mapped_column(Text)
    name: Mapped[str | None] = mapped_column(Text)
    members_count: Mapped[int] = mapped_column(Integer, nullable=False)
    snapshot_at: Mapped[datetime] = mapped_column(
        TIMESTAMPTZ, nullable=False, server_default="now()"
    )

    __table_args__ = (
        Index("ix_groups_raw_group_snapshot", "group_id", "snapshot_at"),
    )


class PostRaw(Base):
    """Сырые данные публикаций из VK API."""

    __tablename__ = "posts_raw"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    group_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    post_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    posted_at: Mapped[datetime] = mapped_column(TIMESTAMPTZ, nullable=False)
    text: Mapped[str | None] = mapped_column(Text)
    post_type: Mapped[str | None] = mapped_column(Text)
    content_type: Mapped[str] = mapped_column(Text, nullable=False)
    attachments_json: Mapped[dict | None] = mapped_column(JSONB)
    likes_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    comments_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    reposts_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    views_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    fetched_at: Mapped[datetime] = mapped_column(
        TIMESTAMPTZ, nullable=False, server_default="now()"
    )

    __table_args__ = (
        UniqueConstraint("group_id", "post_id", name="uq_posts_raw_group_post"),
        Index("ix_posts_raw_group_posted", "group_id", "posted_at"),
        Index("ix_posts_raw_content_type", "content_type"),
    )
