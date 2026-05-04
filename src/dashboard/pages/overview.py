"""Страница «Обзор»: KPI-карточки, коэффициенты вовлечённости, ERday."""
from __future__ import annotations

from datetime import date

import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import Input, Output, callback, dcc, html, register_page

from src.dashboard import data_access as da
from src.dashboard.components.kpi_card import kpi_card
from src.dashboard.styles import PRIMARY, SECONDARY, BACKGROUND

register_page(__name__, path="/", name="Обзор")


def layout() -> html.Div:
    return html.Div(
        [
            dcc.Loading(
                id="overview-loading",
                type="circle",
                children=html.Div(id="overview-content"),
            )
        ],
        style={"backgroundColor": BACKGROUND, "minHeight": "100vh", "padding": "24px"},
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
        eng = da.get_engagement(date_from, date_to)
        react = da.get_reactions(date_from, date_to)
        vis = da.get_visibility(date_from, date_to)
        erday_df = da.get_erday_series(date_from, date_to)
    except Exception as exc:
        return html.Div(f"Ошибка загрузки данных: {exc}", className="text-danger")

    # ── Блок 1: KPI-карточки (абсолютные показатели) ─────────────────────────
    kpi_row = dbc.Row(
        [
            dbc.Col(kpi_card(
                "Просмотры",
                abs_cur.get("total_views"),
                abs_prev.get("total_views"),
            ), width=12, md=True),
            dbc.Col(kpi_card(
                "Реакции",
                abs_cur.get("total_reactions"),
                abs_prev.get("total_reactions"),
            ), width=12, md=True),
            dbc.Col(kpi_card(
                "Комментарии",
                abs_cur.get("total_comments"),
                abs_prev.get("total_comments"),
            ), width=12, md=True),
            dbc.Col(kpi_card(
                "Репосты",
                abs_cur.get("total_reposts"),
                abs_prev.get("total_reposts"),
            ), width=12, md=True),
            dbc.Col(kpi_card(
                "Публикации",
                abs_cur.get("posts_count"),
                abs_prev.get("posts_count"),
            ), width=12, md=True),
        ],
        className="g-3 mb-4",
    )

    # ── Блок 2: Коэффициенты вовлечённости ────────────────────────────────────
    er_post = eng.get("er_post_avg")
    er_view = eng.get("er_view_avg")
    er_day = eng.get("er_day_avg")
    love = react.get("love_rate")
    talk = react.get("talk_rate")
    vr_post = vis.get("vr_post")
    vr_day = vis.get("vr_day")

    def _pct(v: float | None) -> str:
        return f"{v:.2f}%" if v is not None else "—"

    coeff_row_1 = dbc.Row(
        [
            dbc.Col(kpi_card(
                "ERpost (средний)",
                er_post,
                value_fmt=".4f",
                suffix="%",
                tooltip="Формула 1.2: ΣR / (N × n) × 100%",
            ), width=12, sm=6, md=3),
            dbc.Col(kpi_card(
                "ERday (средний)",
                er_day,
                value_fmt=".4f",
                suffix="%",
                tooltip="Формула 1.6: Σ ERday_i / d",
            ), width=12, sm=6, md=3),
            dbc.Col(kpi_card(
                "ERview (средний)",
                er_view,
                value_fmt=".4f",
                suffix="%",
                tooltip="Формула 1.4: среднее R_i/V_i × 100%",
            ), width=12, sm=6, md=3),
            dbc.Col(kpi_card(
                "Love Rate",
                love,
                value_fmt=".4f",
                suffix="%",
                tooltip="Формула 1.7: Σlikes / (N × n) × 100%",
            ), width=12, sm=6, md=3),
        ],
        className="g-3 mb-3",
    )

    coeff_row_2 = dbc.Row(
        [
            dbc.Col(kpi_card(
                "Talk Rate",
                talk,
                value_fmt=".4f",
                suffix="%",
                tooltip="Формула 1.8: Σcomments / (N × n) × 100%",
            ), width=12, sm=6, md=3),
            dbc.Col(kpi_card(
                "VRpost",
                vr_post,
                value_fmt=".4f",
                suffix="%",
                tooltip="Формула 1.9: ΣV / (N × n) × 100%",
            ), width=12, sm=6, md=3),
            dbc.Col(kpi_card(
                "VRday",
                vr_day,
                value_fmt=".4f",
                suffix="%",
                tooltip="Формула 1.10: ΣV / (n × d) × 100%",
            ), width=12, sm=6, md=3),
            dbc.Col(
                html.Div(
                    [
                        html.P("Обозначения:", style={"fontWeight": "600", "marginBottom": "6px"}),
                        html.Small("R = лайки + комментарии + репосты", className="d-block text-muted"),
                        html.Small("n = подписчики, N = постов, V = просмотры", className="d-block text-muted"),
                        html.Small("d = дней в периоде", className="d-block text-muted"),
                    ],
                    style={"padding": "16px", "background": "#EEF2FF", "borderRadius": "12px"},
                ),
                width=12, sm=6, md=3,
            ),
        ],
        className="g-3 mb-4",
    )

    # ── Блок 3: График динамики ERday ─────────────────────────────────────────
    if not erday_df.empty and "post_date" in erday_df.columns:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=erday_df["post_date"],
            y=erday_df["er_day"].astype(float),
            mode="lines+markers",
            name="ERday",
            line=dict(color=PRIMARY, width=2),
            marker=dict(color=SECONDARY, size=6),
            hovertemplate="%{x|%d %b}<br>ERday: %{y:.4f}%<extra></extra>",
        ))
        fig.update_layout(
            title="Динамика ERday по дням",
            xaxis_title="Дата",
            yaxis_title="ERday, %",
            plot_bgcolor="white",
            paper_bgcolor="white",
            margin=dict(l=40, r=20, t=50, b=40),
            hovermode="x unified",
        )
        erday_chart = dcc.Graph(figure=fig, config={"displayModeBar": False})
    else:
        erday_chart = html.Div("Нет данных за выбранный период.", className="text-muted")

    erday_card = dbc.Card(
        dbc.CardBody([
            html.H5("Динамика вовлечённости (ERday)", className="card-title mb-3"),
            erday_chart,
        ]),
        style={"borderRadius": "12px", "boxShadow": "0 2px 8px rgba(0,0,0,0.08)"},
        className="mb-4",
    )

    return html.Div([kpi_row, coeff_row_1, coeff_row_2, erday_card])
