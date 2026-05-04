"""Калькуляторы видимости публикаций (VR)."""
from __future__ import annotations


def calc_vr_post(views_list: list[int], members: int) -> float | None:
    """VRpost (формула 1.9): ΣV / (N × n) × 100%.

    Реализует формулу 1.9 курсовой Рязановой А. А.

    Args:
        views_list: список просмотров по постам.
        members: число подписчиков.

    Returns:
        VRpost в % или None при N=0 или n=0.
    """
    n = len(views_list)
    if n == 0 or members == 0:
        return None
    return sum(views_list) / (n * members) * 100


def calc_vr_day(views_list: list[int], members: int, days: int) -> float | None:
    """VRday (формула 1.10): ΣV / (n × d) × 100%.

    Реализует формулу 1.10 курсовой Рязановой А. А.

    Args:
        views_list: список просмотров по постам.
        members: число подписчиков.
        days: количество дней в периоде.

    Returns:
        VRday в % или None при n=0 или d=0.
    """
    if members == 0 or days == 0:
        return None
    return sum(views_list) / (members * days) * 100
