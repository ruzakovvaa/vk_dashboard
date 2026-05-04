"""Создание схемы БД и SQL-представлений с нуля."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger
from sqlalchemy import text

from src.db.engine import engine

VIEWS_SQL = Path(__file__).parent.parent / "src" / "db" / "views.sql"


def main() -> None:
    sql = VIEWS_SQL.read_text(encoding="utf-8")
    with engine.begin() as conn:
        conn.execute(text(sql))
    logger.info("SQL views created/updated successfully")


if __name__ == "__main__":
    main()
