"""Точка входа Dash-приложения с навигацией и глобальным date-picker."""
from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, State, dcc, html, callback

from src.config import settings
from src.dashboard.styles import BACKGROUND, PRIMARY, CARD_BG

# Инициализация приложения с поддержкой Dash Pages
app = dash.Dash(
    __name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.FLATLY, dbc.icons.BOOTSTRAP],
    suppress_callback_exceptions=True,
    title="VK Dashboard — ЕДИНАЯ РОССИЯ",
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)

_TODAY = date.today()
_DEFAULT_FROM = _TODAY - timedelta(days=7)

# ── Хедер ──────────────────────────────────────────────────────────────────────
header = dbc.Navbar(
    dbc.Container(
        [
            dbc.NavbarBrand(
                [
                    html.Span("📊", style={"marginRight": "8px"}),
                    "ЕДИНАЯ РОССИЯ — Аналитика аудитории",
                ],
                className="fw-bold",
                style={"color": "white", "fontSize": "1.1rem"},
            ),
            dbc.Nav(
                [
                    dbc.NavItem(dbc.NavLink("Обзор", href="/", active="exact",
                                            style={"color": "rgba(255,255,255,0.85)"})),
                    dbc.NavItem(dbc.NavLink("Статистика", href="/statistics", active="exact",
                                            style={"color": "rgba(255,255,255,0.85)"})),
                ],
                navbar=True,
                className="ms-3",
            ),
            html.Div(
                dcc.DatePickerRange(
                    id="date-picker",
                    start_date=_DEFAULT_FROM,
                    end_date=_TODAY,
                    display_format="DD.MM.YYYY",
                    first_day_of_week=1,
                    style={"fontSize": "0.875rem"},
                ),
                className="ms-auto",
            ),
        ],
        fluid=True,
    ),
    color=PRIMARY,
    dark=True,
    sticky="top",
    style={"boxShadow": "0 2px 8px rgba(0,0,0,0.15)"},
)

# ── Хранилище дат (глобальное состояние) ──────────────────────────────────────
date_store = dcc.Store(
    id="date-store",
    data={"date_from": _DEFAULT_FROM.isoformat(), "date_to": _TODAY.isoformat()},
)

app.layout = html.Div(
    [
        date_store,
        header,
        dbc.Container(
            dash.page_container,
            fluid=True,
            style={"paddingTop": "24px", "paddingBottom": "40px"},
        ),
    ],
    style={"backgroundColor": BACKGROUND},
)


@callback(
    Output("date-store", "data"),
    Input("date-picker", "start_date"),
    Input("date-picker", "end_date"),
)
def update_date_store(start: str | None, end: str | None) -> dict:
    start = start or _DEFAULT_FROM.isoformat()
    end = end or _TODAY.isoformat()
    return {"date_from": start[:10], "date_to": end[:10]}


if __name__ == "__main__":
    from loguru import logger
    from pathlib import Path as P

    log_dir = P("logs")
    log_dir.mkdir(exist_ok=True)
    logger.add(
        log_dir / "{time:YYYY-MM-DD}.log",
        rotation="00:00",
        retention="30 days",
        level="INFO",
        encoding="utf-8",
    )

    # Запускаем планировщик парсинга в фоне
    if not settings.dash_debug:
        from src.scheduler import start_scheduler
        _scheduler = start_scheduler()

    app.run(
        host=settings.dash_host,
        port=settings.dash_port,
        debug=settings.dash_debug,
    )
