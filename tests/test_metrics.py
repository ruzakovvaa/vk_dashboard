"""Тесты калькуляторов метрик на синтетических данных."""
from __future__ import annotations

import pytest

from src.metrics.absolute import calc_absolute
from src.metrics.content import calc_er_content
from src.metrics.engagement import (
    calc_er_day,
    calc_er_day_avg,
    calc_er_post,
    calc_er_post_avg,
    calc_er_view,
    calc_er_view_avg,
)
from src.metrics.reactions import calc_love_rate, calc_talk_rate
from src.metrics.visibility import calc_vr_day, calc_vr_post

# Синтетические данные: 5 постов, 1 000 подписчиков
MEMBERS = 1_000
LIKES    = [10, 20, 5, 15, 30]
COMMENTS = [2,  4,  1, 3,  6]
REPOSTS  = [1,  2,  0, 1,  3]
VIEWS    = [500, 800, 200, 600, 1_000]
REACTIONS = [l + c + r for l, c, r in zip(LIKES, COMMENTS, REPOSTS)]  # [13, 26, 6, 19, 39]
# По дням: допустим, посты разбиты по 2 дня (3 + 2)
DAILY_REACTIONS = [13 + 26 + 6, 19 + 39]  # [45, 58]


# ── Absolute ──────────────────────────────────────────────────────────────────

def test_absolute_totals() -> None:
    m = calc_absolute(VIEWS, LIKES, COMMENTS, REPOSTS)
    assert m.total_views == sum(VIEWS)       # 3100
    assert m.total_likes == sum(LIKES)       # 80
    assert m.total_comments == sum(COMMENTS) # 16
    assert m.total_reposts == sum(REPOSTS)   # 7
    assert m.total_reactions == sum(REACTIONS) # 103
    assert m.posts_count == 5


def test_absolute_empty() -> None:
    m = calc_absolute([], [], [], [])
    assert m.posts_count == 0
    assert m.total_reactions == 0


# ── ERpost ────────────────────────────────────────────────────────────────────

def test_er_post_formula_1_1() -> None:
    # Пост 0: R=13, n=1000 → 13/1000 × 100 = 1.3%
    assert calc_er_post(13, 1_000) == pytest.approx(1.3)


def test_er_post_zero_members() -> None:
    assert calc_er_post(13, 0) is None


def test_er_post_avg_formula_1_2() -> None:
    # ΣR=103, N=5, n=1000 → 103/(5×1000) × 100 = 2.06%
    result = calc_er_post_avg(REACTIONS, MEMBERS)
    assert result == pytest.approx(103 / (5 * 1_000) * 100)


def test_er_post_avg_empty() -> None:
    assert calc_er_post_avg([], 1_000) is None


# ── ERview ────────────────────────────────────────────────────────────────────

def test_er_view_formula_1_3() -> None:
    # Пост 0: R=13, V=500 → 13/500 × 100 = 2.6%
    assert calc_er_view(13, 500) == pytest.approx(2.6)


def test_er_view_zero_views() -> None:
    assert calc_er_view(5, 0) is None


def test_er_view_avg_formula_1_4() -> None:
    er_views = [r / v * 100 for r, v in zip(REACTIONS, VIEWS) if v > 0]
    expected = sum(er_views) / len(er_views)
    assert calc_er_view_avg(REACTIONS, VIEWS) == pytest.approx(expected)


# ── ERday ─────────────────────────────────────────────────────────────────────

def test_er_day_formula_1_5() -> None:
    # R_day=45, n=1000 → 4.5%
    assert calc_er_day(45, 1_000) == pytest.approx(4.5)


def test_er_day_zero_members() -> None:
    assert calc_er_day(45, 0) is None


def test_er_day_avg_formula_1_6() -> None:
    # ERday_1 = 45/1000×100 = 4.5, ERday_2 = 58/1000×100 = 5.8 → avg = 5.15
    result = calc_er_day_avg(DAILY_REACTIONS, MEMBERS)
    assert result == pytest.approx(5.15)


def test_er_day_avg_empty() -> None:
    assert calc_er_day_avg([], 1_000) is None


# ── Love Rate / Talk Rate ─────────────────────────────────────────────────────

def test_love_rate_formula_1_7() -> None:
    # Σlikes=80, N=5, n=1000 → 80/(5×1000)×100 = 1.6%
    assert calc_love_rate(LIKES, MEMBERS) == pytest.approx(1.6)


def test_love_rate_zero_members() -> None:
    assert calc_love_rate(LIKES, 0) is None


def test_talk_rate_formula_1_8() -> None:
    # Σcomments=16, N=5, n=1000 → 16/(5×1000)×100 = 0.32%
    assert calc_talk_rate(COMMENTS, MEMBERS) == pytest.approx(0.32)


# ── VRpost / VRday ────────────────────────────────────────────────────────────

def test_vr_post_formula_1_9() -> None:
    # ΣV=3100, N=5, n=1000 → 3100/(5×1000)×100 = 62%
    assert calc_vr_post(VIEWS, MEMBERS) == pytest.approx(62.0)


def test_vr_post_zero_members() -> None:
    assert calc_vr_post(VIEWS, 0) is None


def test_vr_day_formula_1_10() -> None:
    # ΣV=3100, n=1000, d=2 → 3100/(1000×2)×100 = 155%
    assert calc_vr_day(VIEWS, MEMBERS, 2) == pytest.approx(155.0)


def test_vr_day_zero_days() -> None:
    assert calc_vr_day(VIEWS, MEMBERS, 0) is None


# ── ERcontent ─────────────────────────────────────────────────────────────────

def test_er_content_formula_1_11() -> None:
    # photo: 2 поста, R=[13, 26], n=1000 → (13+26)/(2×1000)×100 = 1.95%
    # video: 1 пост, R=[39], n=1000 → 39/1000×100 = 3.9%
    by_type = {"photo": [13, 26], "video": [39], "text": [6, 19]}
    result = calc_er_content(by_type, MEMBERS)
    er_map = {m.content_type: m.er_content for m in result}
    assert er_map["photo"] == pytest.approx(1.95)
    assert er_map["video"] == pytest.approx(3.9)
    assert er_map["text"] == pytest.approx((6 + 19) / (2 * 1_000) * 100)
    # Отсортированы по убыванию ER
    assert result[0].content_type == "video"


def test_er_content_empty_members() -> None:
    result = calc_er_content({"photo": [10, 20]}, 0)
    assert result[0].er_content is None
