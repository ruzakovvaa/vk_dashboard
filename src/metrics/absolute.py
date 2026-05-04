"""Калькуляторы абсолютных метрик активности аудитории."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AbsoluteMetrics:
    total_views: int
    total_likes: int
    total_comments: int
    total_reposts: int
    total_reactions: int
    posts_count: int


def calc_absolute(
    views: list[int],
    likes: list[int],
    comments: list[int],
    reposts: list[int],
) -> AbsoluteMetrics:
    """Суммирует абсолютные показатели за период.

    Реализует подготовительный расчёт для формул 1.1–1.10 курсовой.

    Args:
        views: список просмотров по постам.
        likes: список лайков по постам.
        comments: список комментариев по постам.
        reposts: список репостов по постам.

    Returns:
        AbsoluteMetrics с суммарными показателями.
    """
    total_reactions = [l + c + r for l, c, r in zip(likes, comments, reposts)]
    return AbsoluteMetrics(
        total_views=sum(views),
        total_likes=sum(likes),
        total_comments=sum(comments),
        total_reposts=sum(reposts),
        total_reactions=sum(total_reactions),
        posts_count=len(views),
    )
