"""Калькулятор ERcontent по типам контента."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ContentMetric:
    content_type: str
    er_content: float | None
    posts_count: int
    avg_reactions: float


def calc_er_content(
    reactions_by_type: dict[str, list[int]],
    members: int,
) -> list[ContentMetric]:
    """ERcontent по типам контента (формула 1.11): ΣR_content / (N_content × n) × 100%.

    Реализует формулу 1.11 курсовой Рязановой А. А.

    Args:
        reactions_by_type: словарь {content_type: [reactions_per_post]}.
        members: число подписчиков.

    Returns:
        Список ContentMetric, отсортированный по ERcontent desc.
    """
    result: list[ContentMetric] = []
    for ctype, reactions in reactions_by_type.items():
        n = len(reactions)
        total_r = sum(reactions)
        er = None if (n == 0 or members == 0) else total_r / (n * members) * 100
        avg_r = total_r / n if n > 0 else 0.0
        result.append(ContentMetric(content_type=ctype, er_content=er, posts_count=n, avg_reactions=avg_r))
    result.sort(key=lambda x: (x.er_content or 0.0), reverse=True)
    return result
