"""APScheduler: периодический запуск парсинга параллельно с дашбордом."""
from __future__ import annotations

from apscheduler.schedulers.background import BackgroundScheduler
from loguru import logger

from src.config import settings
from src.parser.vk_parser import run_parsing


def _parse_job() -> None:
    logger.info("Scheduled parsing started")
    run_parsing(lookback_days=settings.parser_lookback_days)


def start_scheduler() -> BackgroundScheduler:
    """Запускает BackgroundScheduler и возвращает его экземпляр."""
    scheduler = BackgroundScheduler(timezone="Europe/Moscow")
    scheduler.add_job(
        _parse_job,
        trigger="cron",
        minute=f"*/{settings.parser_interval_minutes}",
        id="vk_parser",
        replace_existing=True,
    )
    scheduler.start()
    logger.info(
        f"Scheduler started: parsing every {settings.parser_interval_minutes} minutes"
    )
    return scheduler
