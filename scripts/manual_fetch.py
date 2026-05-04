"""Ручной запуск парсера для отладки."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger

from src.parser.vk_parser import run_parsing, _setup_logging

if __name__ == "__main__":
    _setup_logging()
    logger.info("Manual fetch started")
    run_parsing(lookback_days=14)
