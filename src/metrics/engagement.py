"""Калькуляторы коэффициентов вовлечённости (ER)."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class EngagementMetrics:
    er_post_avg: float | None
    er_view_avg: float | None
    er_day_avg: float | None


def calc_er_post(reactions: int, members: int) -> float | None:
    """ERpost конкретного поста (формула 1.1): R/n × 100%.

    Реализует формулу 1.1 курсовой Рязановой А. А.

    Args:
        reactions: сумма лайков + комментариев + репостов поста.
        members: число подписчиков сообщества.

    Returns:
        ERpost в % или None при n=0.
    """
    if members == 0:
        return None
    return reactions / members * 100


def calc_er_post_avg(
    reactions_list: list[int],
    members: int,
) -> float | None:
    """Средний ERpost за период (формула 1.2): ΣR / (N × n) × 100%.

    Реализует формулу 1.2 курсовой Рязановой А. А.

    Args:
        reactions_list: список реакций по постам.
        members: число подписчиков.

    Returns:
        Средний ERpost в % или None при N=0 или n=0.
    """
    n_posts = len(reactions_list)
    if n_posts == 0 or members == 0:
        return None
    return sum(reactions_list) / (n_posts * members) * 100


def calc_er_view(reactions: int, views: int) -> float | None:
    """ERview конкретного поста (формула 1.3): R/V × 100%.

    Реализует формулу 1.3 курсовой Рязановой А. А.

    Args:
        reactions: реакции поста.
        views: просмотры поста.

    Returns:
        ERview в % или None при V=0.
    """
    if views == 0:
        return None
    return reactions / views * 100


def calc_er_view_avg(
    reactions_list: list[int],
    views_list: list[int],
) -> float | None:
    """Средний ERview за период (формула 1.4): среднее ERview_i по постам.

    Реализует формулу 1.4 курсовой Рязановой А. А.

    Args:
        reactions_list: реакции по постам.
        views_list: просмотры по постам.

    Returns:
        Средний ERview в % или None если нет постов с просмотрами > 0.
    """
    er_views = [
        r / v * 100
        for r, v in zip(reactions_list, views_list)
        if v > 0
    ]
    if not er_views:
        return None
    return sum(er_views) / len(er_views)


def calc_er_day(reactions_day: int, members: int) -> float | None:
    """ERday за конкретный день (формула 1.5): R_day/n × 100%.

    Реализует формулу 1.5 курсовой Рязановой А. А.

    Args:
        reactions_day: суммарные реакции за день.
        members: число подписчиков.

    Returns:
        ERday в % или None при n=0.
    """
    if members == 0:
        return None
    return reactions_day / members * 100


def calc_er_day_avg(
    daily_reactions: list[int],
    members: int,
) -> float | None:
    """Средний ERday за период (формула 1.6): ΣERday_i / d.

    Реализует формулу 1.6 курсовой Рязановой А. А.

    Args:
        daily_reactions: суммарные реакции по каждому дню периода.
        members: число подписчиков.

    Returns:
        Средний ERday в % или None при d=0 или n=0.
    """
    d = len(daily_reactions)
    if d == 0 or members == 0:
        return None
    er_days = [r / members * 100 for r in daily_reactions]
    return sum(er_days) / d
