"""Загрузка бенчмарков и логика цветовой индикации."""
from __future__ import annotations

from pathlib import Path

import yaml

_BENCHMARKS_PATH = Path(__file__).parent.parent.parent / "config" / "benchmarks.yaml"
_config: dict | None = None


def _load() -> dict:
    global _config
    if _config is None:
        with open(_BENCHMARKS_PATH, encoding="utf-8") as f:
            _config = yaml.safe_load(f)
    return _config


def get_norm(metric: str) -> float | None:
    """Возвращает эталонное значение нормы для метрики (в %)."""
    cfg = _load()
    entry = cfg.get("benchmarks", {}).get(metric)
    return entry["norm"] if entry else None


def get_benchmark_status(value: float, norm: float) -> tuple[str, str]:
    """Возвращает (статус, цвет) для значения относительно нормы.

    Статусы: 'good', 'normal', 'bad'.
    Цвета: зелёный / жёлтый / красный.
    """
    cfg = _load()
    thresholds = cfg.get("thresholds", {})
    green = thresholds.get("green", 1.2)
    yellow_low = thresholds.get("yellow_low", 0.8)

    if norm <= 0:
        return "normal", "#ca8a04"
    ratio = float(value) / float(norm)
    if ratio >= green:
        return "good", "#16a34a"
    elif ratio >= yellow_low:
        return "normal", "#ca8a04"
    else:
        return "bad", "#dc2626"


def get_repost_reach_factor() -> float:
    return _load().get("repost_reach_factor", 0.40)


def all_benchmarks() -> dict:
    return _load().get("benchmarks", {})
