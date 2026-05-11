"""Страница «Обзор»: информационный блок о сообществе и KPI-карточки."""
from __future__ import annotations

from datetime import date

import dash_bootstrap_components as dbc
from dash import Input, Output, callback, dcc, html, register_page

from src.dashboard import data_access as da
from src.dashboard.components.kpi_card import kpi_card
from src.dashboard.components.subscribers_card import subscribers_card
from src.dashboard.styles import BACKGROUND, CARD_STYLE, MUTED, SECTION_TITLE_STYLE

register_page(__name__, path="/", name="Обзор")


def layout() -> html.Div:
    return html.Div(
        dcc.Loading(
            id="overview-loading",
            type="circle",
            children=html.Div(id="overview-content"),
        ),
        style={"backgroundColor": BACKGROUND},
    )


@callback(
    Output("overview-content", "children"),
    Input("date-store", "data"),
)
def update_overview(date_data: dict | None) -> html.Div:
    if not date_data:
        return html.Div("Выберите период в фильтре сверху.")

    date_from = date.fromisoformat(date_data["date_from"])
    date_to = date.fromisoformat(date_data["date_to"])

    try:
        abs_cur = da.get_absolute(date_from, date_to)
        abs_prev = da.get_previous_absolute(date_from, date_to)
        daily_df = da.get_daily_absolute(date_from, date_to)
        subs_data = da.get_subscribers_delta(date_from, date_to)
    except Exception as exc:
        return html.Div(f"Ошибка загрузки данных: {exc}", className="text-danger")

    def _spark(col: str) -> list[float]:
        if not daily_df.empty and col in daily_df.columns:
            return [float(v) for v in daily_df[col].tolist()]
        return []

    # ── Информационный блок о сообществе ──────────────────────────────────────
    _li = {"fontSize": "0.9rem", "lineHeight": "1.8", "color": "#0f172a"}
    _p = {"fontSize": "0.9rem", "lineHeight": "1.6", "color": "#0f172a", "marginBottom": "8px"}

    info_card = dbc.Card(
        dbc.CardBody(
            html.Div([
                html.Div([
                    html.H6("О сообществе", style=SECTION_TITLE_STYLE),
                    html.P(
                        "«Единая Россия» — всероссийская политическая партия, основана в 2001 году. "
                        "Является крупнейшей парламентской партией Российской Федерации.",
                        style=_p,
                    ),
                    html.P(
                        f"Официальное сообщество во «ВКонтакте» насчитывает более 200 тысяч подписчиков "
                        "и является одним из наиболее активных по публикационной частоте "
                        "политических пабликов рунета.",
                        style=_p,
                    ),
                    html.P(
                        "Что публикуется в сообществе:",
                        style={"fontSize": "0.9rem", "fontWeight": "600", "color": "#0f172a", "marginBottom": "4px"},
                    ),
                    html.Ul([
                        html.Li("новости партии и её региональных отделений;", style=_li),
                        html.Li("прямые трансляции мероприятий (съезды, форумы, заседания);", style=_li),
                        html.Li("тематические рубрики и разъяснения законопроектов;", style=_li),
                        html.Li("опросы аудитории;", style=_li),
                        html.Li("фото- и видеоматериалы.", style=_li),
                    ], style={"paddingLeft": "20px", "marginBottom": "12px"}),
                    html.A(
                        "Перейти в сообщество →",
                        href="https://vk.com/er_ru",
                        target="_blank",
                        style={
                            "display": "inline-block",
                            "border": "1px solid #1e40af",
                            "color": "#1e40af",
                            "padding": "8px 16px",
                            "borderRadius": "8px",
                            "textDecoration": "none",
                            "fontSize": "0.875rem",
                            "fontWeight": "500",
                        },
                    ),
                ], style={"flex": "1", "minWidth": "0"}),
                html.Div(
                    html.Img(
                        src="/assets/er_logo.png",
                        style={"width": "100%", "height": "100%", "objectFit": "contain"},
                    ),
                    style={
                        "flexShrink": "0",
                        "width": "220px",
                        "marginLeft": "40px",
                        "alignSelf": "stretch",
                        "display": "flex",
                        "alignItems": "center",
                    },
                ),
            ], style={"display": "flex", "alignItems": "flex-start"}),
            style={"padding": "24px"},
        ),
        style=CARD_STYLE,
        className="mb-4",
    )

    # ── KPI: верхний ряд — Подписчики, Просмотры, Публикации ─────────────────
    top_kpi_row = dbc.Row([
        dbc.Col(subscribers_card(subs_data), width=12, md=4),
        dbc.Col(kpi_card(
            "Просмотры",
            abs_cur.get("total_views"),
            abs_prev.get("total_views"),
            sparkline_current=_spark("total_views"),
        ), width=12, md=4),
        dbc.Col(kpi_card(
            "Публикации",
            abs_cur.get("posts_count"),
            abs_prev.get("posts_count"),
            sparkline_current=_spark("posts_count"),
        ), width=12, md=4),
    ], className="g-3 mb-3")

    # ── KPI: нижний ряд — Реакции, Комментарии, Репосты ──────────────────────
    bot_kpi_row = dbc.Row([
        dbc.Col(kpi_card(
            "Реакции",
            abs_cur.get("total_reactions"),
            abs_prev.get("total_reactions"),
            sparkline_current=_spark("total_reactions"),
        ), width=12, md=4),
        dbc.Col(kpi_card(
            "Комментарии",
            abs_cur.get("total_comments"),
            abs_prev.get("total_comments"),
            sparkline_current=_spark("total_comments"),
        ), width=12, md=4),
        dbc.Col(kpi_card(
            "Репосты",
            abs_cur.get("total_reposts"),
            abs_prev.get("total_reposts"),
            sparkline_current=_spark("total_reposts"),
        ), width=12, md=4),
    ], className="g-3 mb-4")

    return html.Div([info_card, top_kpi_row, bot_kpi_row])
