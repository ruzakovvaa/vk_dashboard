"""Основной скрипт парсинга публикаций сообщества из VK API."""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from loguru import logger
from pydantic import ValidationError
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert as pg_insert

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.config import settings
from src.db.engine import SessionLocal
from src.db.models import GroupRaw, PostRaw
from src.parser.schemas import VKGroup, VKGroupsResponse, VKPost, VKWallGetResponse
from src.parser.vk_client import VKClient, VKAPIError

_PRIORITY = {"video": 3, "photo": 2, "link": 1, "text": 0}


def _classify_content_type(attachments: list[dict[str, Any]]) -> str:
    """Определяет тип контента по вложениям (приоритет: video > photo > link > text)."""
    best = "text"
    for att in attachments:
        t = att.get("type", "")
        if t in _PRIORITY and _PRIORITY[t] > _PRIORITY[best]:
            best = t
    return best


def _upsert_group(session: Any, group: VKGroup) -> None:
    stmt = pg_insert(GroupRaw).values(
        group_id=group.id,
        screen_name=group.screen_name,
        name=group.name,
        members_count=group.members_count,
        snapshot_at=datetime.now(tz=timezone.utc),
    )
    session.execute(stmt)
    session.commit()
    logger.info(f"Group snapshot saved: {group.name} ({group.members_count} members)")


def _upsert_posts(session: Any, posts: list[VKPost], group_id: int) -> tuple[int, int]:
    """Upsert постов в posts_raw. Возвращает (inserted, updated)."""
    inserted = updated = 0
    for post in posts:
        att_list: list[dict[str, Any]] = [a.model_dump() for a in post.attachments]
        content_type = _classify_content_type(att_list)
        posted_at = datetime.fromtimestamp(post.date, tz=timezone.utc)
        values = {
            "group_id": group_id,
            "post_id": post.id,
            "posted_at": posted_at,
            "text": post.text,
            "post_type": post.post_type,
            "content_type": content_type,
            "attachments_json": att_list or None,
            "likes_count": post.likes.count,
            "comments_count": post.comments.count,
            "reposts_count": post.reposts.count,
            "views_count": post.views.count,
            "fetched_at": datetime.now(tz=timezone.utc),
        }
        stmt = (
            pg_insert(PostRaw)
            .values(**values)
            .on_conflict_do_update(
                constraint="uq_posts_raw_group_post",
                set_={
                    "likes_count": values["likes_count"],
                    "comments_count": values["comments_count"],
                    "reposts_count": values["reposts_count"],
                    "views_count": values["views_count"],
                    "fetched_at": values["fetched_at"],
                },
            )
        )
        result = session.execute(stmt)
        # rowcount=1 — insert, rowcount=2 — update (pg behaviour with DO UPDATE)
        if result.rowcount == 1:
            inserted += 1
        else:
            updated += 1
    session.commit()
    return inserted, updated


def run_parsing(lookback_days: int = 14) -> None:
    """Основная функция парсинга: группа → посты → БД."""
    start = datetime.now(tz=timezone.utc)
    screen_name = settings.vk_group_screen_name

    with VKClient() as client:
        # 1. Получить метаданные группы
        try:
            raw = client.groups_get_by_id(screen_name)
            gr = VKGroupsResponse.model_validate(raw)
            group = gr.groups[0]
        except (VKAPIError, ValidationError, IndexError) as exc:
            logger.error(f"Failed to fetch group info: {exc}")
            return

        group_id = group.id
        # owner_id для стены сообщества — отрицательный
        owner_id = -group_id

        with SessionLocal() as session:
            _upsert_group(session, group)

            # 2. Страничный обход wall.get
            cutoff_ts = (
                datetime.now(tz=timezone.utc).timestamp() - lookback_days * 86400
            )
            offset = 0
            total_inserted = total_updated = 0
            batch_posts: list[VKPost] = []

            while True:
                try:
                    raw_wall = client.wall_get(owner_id, count=100, offset=offset)
                    wall = VKWallGetResponse.model_validate(raw_wall)
                except (VKAPIError, ValidationError) as exc:
                    logger.error(f"wall.get error at offset {offset}: {exc}")
                    break

                items = wall.response.items
                if not items:
                    break

                stop = False
                for post in items:
                    if post.date < cutoff_ts:
                        stop = True
                        break
                    batch_posts.append(post)

                if batch_posts:
                    ins, upd = _upsert_posts(session, batch_posts, group_id)
                    total_inserted += ins
                    total_updated += upd
                    logger.info(
                        f"offset={offset}: +{ins} inserted, ~{upd} updated"
                    )
                    batch_posts = []

                if stop or len(items) < 100:
                    break
                offset += 100

    elapsed = (datetime.now(tz=timezone.utc) - start).total_seconds()
    logger.success(
        f"Parsing done in {elapsed:.1f}s: "
        f"{total_inserted} inserted, {total_updated} updated"
    )


def _setup_logging() -> None:
    from pathlib import Path

    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    logger.add(
        log_dir / "{time:YYYY-MM-DD}.log",
        rotation="00:00",
        retention="30 days",
        level="INFO",
        encoding="utf-8",
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="VK community post parser")
    parser.add_argument("--lookback-days", type=int, default=settings.parser_lookback_days)
    args = parser.parse_args()
    _setup_logging()
    run_parsing(lookback_days=args.lookback_days)
