"""Слой доступа к данным: запросы к SQL-функциям/views, кэширование."""
from __future__ import annotations

from datetime import date, datetime
from typing import Any

import pandas as pd
from loguru import logger
from sqlalchemy import text

from src.db.engine import engine

_CACHE: dict[tuple[Any, ...], tuple[datetime, Any]] = {}
_TTL_SECONDS = 300


def _cached(key: tuple[Any, ...], fn: Any) -> Any:
    """Простой TTL-кэш поверх dict."""
    now = datetime.utcnow()
    if key in _CACHE:
        ts, value = _CACHE[key]
        if (now - ts).total_seconds() < _TTL_SECONDS:
            return value
    value = fn()
    _CACHE[key] = (now, value)
    return value


def _exec(sql: str, params: dict[str, Any]) -> list[dict[str, Any]]:
    with engine.connect() as conn:
        result = conn.execute(text(sql), params)
        cols = list(result.keys())
        return [dict(zip(cols, row)) for row in result]


# ──────────────────────────────────────────────────────────────────────────────

def get_absolute(date_from: date, date_to: date) -> dict[str, Any]:
    key = ("absolute", date_from, date_to)
    def _fetch() -> dict[str, Any]:
        rows = _exec("SELECT * FROM agg_absolute(:df, :dt)", {"df": date_from, "dt": date_to})
        return rows[0] if rows else {}
    return _cached(key, _fetch)


def get_engagement(date_from: date, date_to: date) -> dict[str, Any]:
    key = ("engagement", date_from, date_to)
    def _fetch() -> dict[str, Any]:
        rows = _exec("SELECT * FROM agg_engagement(:df, :dt)", {"df": date_from, "dt": date_to})
        return rows[0] if rows else {}
    return _cached(key, _fetch)


def get_reactions(date_from: date, date_to: date) -> dict[str, Any]:
    key = ("reactions", date_from, date_to)
    def _fetch() -> dict[str, Any]:
        rows = _exec("SELECT * FROM agg_reactions(:df, :dt)", {"df": date_from, "dt": date_to})
        return rows[0] if rows else {}
    return _cached(key, _fetch)


def get_visibility(date_from: date, date_to: date) -> dict[str, Any]:
    key = ("visibility", date_from, date_to)
    def _fetch() -> dict[str, Any]:
        rows = _exec("SELECT * FROM agg_visibility(:df, :dt)", {"df": date_from, "dt": date_to})
        return rows[0] if rows else {}
    return _cached(key, _fetch)


def get_content_type(date_from: date, date_to: date) -> pd.DataFrame:
    key = ("content_type", date_from, date_to)
    def _fetch() -> pd.DataFrame:
        rows = _exec("SELECT * FROM agg_content_type(:df, :dt)", {"df": date_from, "dt": date_to})
        return pd.DataFrame(rows)
    return _cached(key, _fetch)


def get_top_posts(date_from: date, date_to: date, limit: int = 10) -> pd.DataFrame:
    key = ("top_posts", date_from, date_to, limit)
    def _fetch() -> pd.DataFrame:
        rows = _exec(
            "SELECT * FROM top_posts(:df, :dt, :lim)",
            {"df": date_from, "dt": date_to, "lim": limit},
        )
        return pd.DataFrame(rows)
    return _cached(key, _fetch)


def get_daily_absolute(date_from: date, date_to: date) -> pd.DataFrame:
    """Суммарные показатели по дням для спарклайнов."""
    key = ("daily_absolute", date_from, date_to)
    def _fetch() -> pd.DataFrame:
        rows = _exec("SELECT * FROM daily_absolute(:df, :dt)", {"df": date_from, "dt": date_to})
        return pd.DataFrame(rows)
    return _cached(key, _fetch)


def get_erday_series(date_from: date, date_to: date) -> pd.DataFrame:
    key = ("erday_series", date_from, date_to)
    def _fetch() -> pd.DataFrame:
        rows = _exec("SELECT * FROM erday_series(:df, :dt)", {"df": date_from, "dt": date_to})
        return pd.DataFrame(rows)
    return _cached(key, _fetch)


def get_erday_series_prev(date_from: date, date_to: date) -> pd.DataFrame:
    """ERday по дням для предыдущего периода той же длины."""
    key = ("erday_series_prev", date_from, date_to)
    def _fetch() -> pd.DataFrame:
        rows = _exec(
            "SELECT * FROM erday_series_prev(:df, :dt)",
            {"df": date_from, "dt": date_to},
        )
        return pd.DataFrame(rows)
    return _cached(key, _fetch)


def get_heatmap(date_from: date, date_to: date) -> pd.DataFrame:
    key = ("heatmap", date_from, date_to)
    def _fetch() -> pd.DataFrame:
        rows = _exec("SELECT * FROM heatmap_views(:df, :dt)", {"df": date_from, "dt": date_to})
        return pd.DataFrame(rows)
    return _cached(key, _fetch)


def get_views_series(date_from: date, date_to: date) -> pd.DataFrame:
    """Суммарные просмотры по дням — текущий период."""
    key = ("views_series", date_from, date_to)
    def _fetch() -> pd.DataFrame:
        rows = _exec("SELECT * FROM views_series(:df, :dt)", {"df": date_from, "dt": date_to})
        return pd.DataFrame(rows)
    return _cached(key, _fetch)


def get_views_series_prev(date_from: date, date_to: date) -> pd.DataFrame:
    """Суммарные просмотры по дням — предыдущий период."""
    key = ("views_series_prev", date_from, date_to)
    def _fetch() -> pd.DataFrame:
        rows = _exec(
            "SELECT * FROM views_series_prev(:df, :dt)",
            {"df": date_from, "dt": date_to},
        )
        return pd.DataFrame(rows)
    return _cached(key, _fetch)


def get_subscribers_delta(date_from: date, date_to: date) -> dict[str, Any]:
    """Динамика подписчиков за период из таблицы groups_raw."""
    key = ("subscribers_delta", date_from, date_to)
    def _fetch() -> dict[str, Any]:
        # Получаем group_id из первого доступного снапшота
        id_rows = _exec(
            "SELECT group_id FROM groups_raw ORDER BY snapshot_at DESC LIMIT 1", {}
        )
        if not id_rows:
            return {}
        group_id = id_rows[0]["group_id"]
        rows = _exec(
            "SELECT * FROM subscribers_delta(:gid, :df, :dt)",
            {"gid": group_id, "df": date_from, "dt": date_to},
        )
        return rows[0] if rows else {}
    return _cached(key, _fetch)


def get_previous_absolute(date_from: date, date_to: date) -> dict[str, Any]:
    """Абсолютные показатели за предыдущий период той же длины."""
    delta = date_to - date_from
    prev_from_d = date_from - delta
    return get_absolute(prev_from_d, date_from)


def get_reach_estimate(date_from: date, date_to: date) -> dict[str, Any]:
    """Оценочный охват через прокси репостов (нет прав админа сообщества).

    reach_estimated = total_views (как нижняя оценка уникального охвата).
    virality_estimated = reposts_total × repost_reach_factor / views_total × 100%.
    """
    from src.utils.benchmarks import get_repost_reach_factor
    abs_data = get_absolute(date_from, date_to)
    views = int(abs_data.get("total_views") or 0)
    reposts = int(abs_data.get("total_reposts") or 0)
    factor = get_repost_reach_factor()
    if views > 0:
        raw = reposts * factor / views * 100
        if raw > 100:
            virality_pct = None
            data_insufficient = True
        else:
            virality_pct = round(raw, 2)
            data_insufficient = False
    else:
        virality_pct = None
        data_insufficient = False
    return {
        "reach_estimated": views,
        "virality_pct": virality_pct,
        "data_insufficient": data_insufficient,
        "is_estimate": True,
    }
