"""Слой доступа к данным: запросы к SQL-функциям/views, кэширование."""
from __future__ import annotations

import functools
from datetime import date, datetime
from typing import Any

import pandas as pd
from loguru import logger
from sqlalchemy import text

from src.db.engine import engine

# Простое in-memory кэширование с TTL 5 минут через functools.lru_cache.
# lru_cache кэширует по аргументам — это достаточно для нашего сценария.
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
    """Абсолютные показатели за период."""
    key = ("absolute", date_from, date_to)
    def _fetch() -> dict[str, Any]:
        rows = _exec(
            "SELECT * FROM agg_absolute(:df, :dt)",
            {"df": date_from, "dt": date_to},
        )
        return rows[0] if rows else {}
    return _cached(key, _fetch)


def get_engagement(date_from: date, date_to: date) -> dict[str, Any]:
    """Коэффициенты вовлечённости."""
    key = ("engagement", date_from, date_to)
    def _fetch() -> dict[str, Any]:
        rows = _exec(
            "SELECT * FROM agg_engagement(:df, :dt)",
            {"df": date_from, "dt": date_to},
        )
        return rows[0] if rows else {}
    return _cached(key, _fetch)


def get_reactions(date_from: date, date_to: date) -> dict[str, Any]:
    """Love Rate и Talk Rate."""
    key = ("reactions", date_from, date_to)
    def _fetch() -> dict[str, Any]:
        rows = _exec(
            "SELECT * FROM agg_reactions(:df, :dt)",
            {"df": date_from, "dt": date_to},
        )
        return rows[0] if rows else {}
    return _cached(key, _fetch)


def get_visibility(date_from: date, date_to: date) -> dict[str, Any]:
    """VRpost и VRday."""
    key = ("visibility", date_from, date_to)
    def _fetch() -> dict[str, Any]:
        rows = _exec(
            "SELECT * FROM agg_visibility(:df, :dt)",
            {"df": date_from, "dt": date_to},
        )
        return rows[0] if rows else {}
    return _cached(key, _fetch)


def get_content_type(date_from: date, date_to: date) -> pd.DataFrame:
    """ERcontent по типам контента."""
    key = ("content_type", date_from, date_to)
    def _fetch() -> pd.DataFrame:
        rows = _exec(
            "SELECT * FROM agg_content_type(:df, :dt)",
            {"df": date_from, "dt": date_to},
        )
        return pd.DataFrame(rows)
    return _cached(key, _fetch)


def get_top_posts(date_from: date, date_to: date, limit: int = 10) -> pd.DataFrame:
    """Топ-N публикаций по ERpost."""
    key = ("top_posts", date_from, date_to, limit)
    def _fetch() -> pd.DataFrame:
        rows = _exec(
            "SELECT * FROM top_posts(:df, :dt, :lim)",
            {"df": date_from, "dt": date_to, "lim": limit},
        )
        return pd.DataFrame(rows)
    return _cached(key, _fetch)


def get_erday_series(date_from: date, date_to: date) -> pd.DataFrame:
    """ERday по дням для графика динамики."""
    key = ("erday_series", date_from, date_to)
    def _fetch() -> pd.DataFrame:
        rows = _exec(
            "SELECT * FROM erday_series(:df, :dt)",
            {"df": date_from, "dt": date_to},
        )
        return pd.DataFrame(rows)
    return _cached(key, _fetch)


def get_heatmap(date_from: date, date_to: date) -> pd.DataFrame:
    """Средние просмотры по ячейке день_недели × час."""
    key = ("heatmap", date_from, date_to)
    def _fetch() -> pd.DataFrame:
        rows = _exec(
            "SELECT * FROM heatmap_views(:df, :dt)",
            {"df": date_from, "dt": date_to},
        )
        return pd.DataFrame(rows)
    return _cached(key, _fetch)


def get_previous_absolute(date_from: date, date_to: date) -> dict[str, Any]:
    """Абсолютные показатели за предыдущий период той же длины."""
    delta = date_to - date_from
    prev_to = date_from
    prev_from = date(prev_to.year, prev_to.month, prev_to.day)
    import datetime as dt
    prev_to_d = date_from
    prev_from_d = date_from - delta
    return get_absolute(prev_from_d, prev_to_d)
