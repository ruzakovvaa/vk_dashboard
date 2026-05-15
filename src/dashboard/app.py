"""Точка входа Dash-приложения с навигацией и глобальным date-picker."""
from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, callback, dcc, html

from src.config import settings
from src.dashboard.styles import BACKGROUND, CARD_BG

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

# ── Шапка ──────────────────────────────────────────────────────────────────────
header = html.Div(
    dbc.Container(
        html.Div([
            # Левая часть: логотип + заголовок
            html.Div([
                html.Img(
                    src="/assets/header_logo.png",
                    style={"height": "36px", "width": "auto", "marginRight": "12px"},
                ),
                dcc.Link(
                    "Аналитический дашборд сообщества «Единая Россия» во ВКонтакте",
                    href="/",
                    style={
                        "fontWeight": "700",
                        "fontSize": "1rem",
                        "color": "#0f172a",
                        "lineHeight": "1.2",
                        "textDecoration": "none",
                        "cursor": "pointer",
                    },
                ),
            ], style={"display": "flex", "alignItems": "center"}),

            # Центр: навигация
            html.Div([
                dbc.Nav([
                    dbc.NavItem(dbc.NavLink(
                        "Обзор", href="/", active="exact",
                        style={"color": "#0f172a", "fontWeight": "500", "padding": "6px 16px"},
                    )),
                    dbc.NavItem(dbc.NavLink(
                        "Статистика", href="/statistics", active="exact",
                        style={"color": "#0f172a", "fontWeight": "500", "padding": "6px 16px"},
                    )),
                ], navbar=True),
            ]),

            # Правая часть: дата-пикер в виде пилюли
            html.Div(
                dcc.DatePickerRange(
                    id="date-picker",
                    start_date=_DEFAULT_FROM,
                    end_date=_TODAY,
                    max_date_allowed=_TODAY,
                    display_format="DD.MM.YYYY",
                    first_day_of_week=1,
                    style={
                        "fontSize": "0.875rem",
                        "borderRadius": "9999px",
                        "border": "1px solid #e2e8f0",
                        "padding": "0",
                    },
                ),
            ),
        ], style={
            "display": "flex",
            "alignItems": "center",
            "justifyContent": "space-between",
            "padding": "12px 0",
        }),
        fluid=True,
    ),
    style={
        "backgroundColor": CARD_BG,
        "borderBottom": "1px solid #e2e8f0",
        "position": "sticky",
        "top": "0",
        "zIndex": "1000",
        "boxShadow": "0 1px 3px rgba(15,23,42,0.06)",
    },
)

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
            style={"paddingTop": "24px", "paddingBottom": "40px", "maxWidth": "1440px"},
        ),
    ],
    style={"backgroundColor": BACKGROUND, "fontFamily": 'Inter, -apple-system, "Segoe UI", sans-serif'},
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

    app.run(
        host=settings.dash_host,
        port=settings.dash_port,
        debug=settings.dash_debug,
    )
