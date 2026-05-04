"""Калькуляторы Love Rate и Talk Rate."""
from __future__ import annotations


def calc_love_rate(likes_list: list[int], members: int) -> float | None:
    """Love Rate (формула 1.7): Σlikes / (N × n) × 100%.

    Реализует формулу 1.7 курсовой Рязановой А. А.

    Args:
        likes_list: список лайков по постам.
        members: число подписчиков.

    Returns:
        Love Rate в % или None при N=0 или n=0.
    """
    n = len(likes_list)
    if n == 0 or members == 0:
        return None
    return sum(likes_list) / (n * members) * 100


def calc_talk_rate(comments_list: list[int], members: int) -> float | None:
    """Talk Rate (формула 1.8): Σcomments / (N × n) × 100%.

    Реализует формулу 1.8 курсовой Рязановой А. А.

    Args:
        comments_list: список комментариев по постам.
        members: число подписчиков.

    Returns:
        Talk Rate в % или None при N=0 или n=0.
    """
    n = len(comments_list)
    if n == 0 or members == 0:
        return None
    return sum(comments_list) / (n * members) * 100
