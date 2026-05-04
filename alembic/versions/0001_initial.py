"""Initial schema: groups_raw and posts_raw

Revision ID: 0001
Revises:
Create Date: 2026-05-01

"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "groups_raw",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("group_id", sa.BigInteger(), nullable=False),
        sa.Column("screen_name", sa.Text(), nullable=True),
        sa.Column("name", sa.Text(), nullable=True),
        sa.Column("members_count", sa.Integer(), nullable=False),
        sa.Column(
            "snapshot_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_groups_raw_group_snapshot", "groups_raw", ["group_id", "snapshot_at"])

    op.create_table(
        "posts_raw",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("group_id", sa.BigInteger(), nullable=False),
        sa.Column("post_id", sa.BigInteger(), nullable=False),
        sa.Column("posted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("text", sa.Text(), nullable=True),
        sa.Column("post_type", sa.Text(), nullable=True),
        sa.Column("content_type", sa.Text(), nullable=False),
        sa.Column("attachments_json", postgresql.JSONB(), nullable=True),
        sa.Column("likes_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("comments_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("reposts_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column("views_count", sa.Integer(), server_default="0", nullable=False),
        sa.Column(
            "fetched_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("group_id", "post_id", name="uq_posts_raw_group_post"),
    )
    op.create_index("ix_posts_raw_group_posted", "posts_raw", ["group_id", "posted_at"])
    op.create_index("ix_posts_raw_content_type", "posts_raw", ["content_type"])


def downgrade() -> None:
    op.drop_index("ix_posts_raw_content_type", table_name="posts_raw")
    op.drop_index("ix_posts_raw_group_posted", table_name="posts_raw")
    op.drop_table("posts_raw")
    op.drop_index("ix_groups_raw_group_snapshot", table_name="groups_raw")
    op.drop_table("groups_raw")
