"""Страница «Статистика»: ER-коэффициенты, donut, графики, тепловая карта, топ постов."""
from __future__ import annotations

from datetime import date

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
from dash import Input, Output, callback, dash_table, dcc, html, register_page

from src.dashboard import data_access as da
from src.dashboard.components.er_block import er_metric_card
from src.dashboard.components.reactions_donut import reactions_donut
from src.dashboard.styles import (
    BACKGROUND,
    CARD_STYLE,
    CONTENT_TYPE_COLORS,
    PRIMARY,
    SECONDARY,
    SECTION_TITLE_STYLE,
)
from src.utils.benchmarks import get_norm
from src.utils.plotly_theme import apply_theme

register_page(__name__, path="/statistics", name="Статистика")

_DAY_NAMES = {1: "Пн", 2: "Вт", 3: "Ср", 4: "Чт", 5: "Пт", 6: "Сб", 7: "Вс"}

_TYPE_CHIP_STYLES = {
    "photo": {"backgroundColor": "#eff6ff", "color": "#1d4ed8"},
    "video": {"backgroundColor": "#f5f3ff", "color": "#6d28d9"},
    "text":  {"backgroundColor": "#f8fafc",  "color": "#475569"},
    "link":  {"backgroundColor": "#fff7ed",  "color": "#c2410c"},
}


def layout() -> html.Div:
    return html.Div(
        dcc.Loading(
            id="stats-loading",
            type="circle",
            children=html.Div(id="stats-content"),
        ),
        style={"backgroundColor": BACKGROUND},
    )


@callback(
    Output("stats-content", "children"),
    Input("date-store", "data"),
)
def update_statistics(date_data: dict | None) -> html.Div:
    if not date_data:
        return html.Div("Выберите период в фильтре сверху.")

    date_from = date.fromisoformat(date_data["date_from"])
    date_to = date.fromisoformat(date_data["date_to"])

    try:
        abs_cur = da.get_absolute(date_from, date_to)
        eng = da.get_engagement(date_from, date_to)
        react = da.get_reactions(date_from, date_to)
        vis = da.get_visibility(date_from, date_to)
        erday_df = da.get_erday_series(date_from, date_to)
        heatmap_df = da.get_heatmap(date_from, date_to)
        content_df = da.get_content_type(date_from, date_to)
        top_df = da.get_top_posts(date_from, date_to, limit=5)
        views_df = da.get_views_series(date_from, date_to)
    except Exception as exc:
        return html.Div(f"Ошибка загрузки данных: {exc}", className="text-danger")

    # ── ER-коэффициенты с бенчмарками ─────────────────────────────────────────
    er_post = eng.get("er_post_avg")
    er_view = eng.get("er_view_avg")
    er_day  = eng.get("er_day_avg")
    love    = react.get("love_rate")
    talk    = react.get("talk_rate")
    vr_post = vis.get("vr_post")
    vr_day  = vis.get("vr_day")

    er_row_1 = dbc.Row([
        dbc.Col(er_metric_card("ERpost (средний)", er_post, "er_post",
                               tooltip="Формула 1.2: ΣR / (N × n) × 100%"), width=12, sm=6, md=3),
        dbc.Col(er_metric_card("ERday (средний)", er_day, "er_day",
                               tooltip="Формула 1.6: Σ ERday_i / d"), width=12, sm=6, md=3),
        dbc.Col(er_metric_card("ERview (средний)", er_view, "er_view",
                               tooltip="Формула 1.4: среднее R_i/V_i × 100%"), width=12, sm=6, md=3),
        dbc.Col(er_metric_card("Love Rate", love, "love_rate",
                               tooltip="Формула 1.7: Σlikes / (N × n) × 100%"), width=12, sm=6, md=3),
    ], className="g-3 mb-3")

    er_row_2 = dbc.Row([
        dbc.Col(er_metric_card("Talk Rate", talk, "talk_rate",
                               tooltip="Формула 1.8: Σcomments / (N × n) × 100%"), width=12, sm=6, md=3),
        dbc.Col(er_metric_card("VRpost", vr_post, "vr_post",
                               tooltip="Формула 1.9: ΣV / (N × n) × 100%"), width=12, sm=6, md=3),
        dbc.Col(er_metric_card("VRday", vr_day, "vr_day",
                               tooltip="Формула 1.10: ΣV / (n × d) × 100%"), width=12, sm=6, md=3),
        dbc.Col(
            html.Div([
                html.P("Обозначения:", style={"fontWeight": "600", "marginBottom": "6px", "fontSize": "0.85rem"}),
                html.Small("R = лайки + комментарии + репосты", className="d-block text-muted"),
                html.Small("n = подписчики, N = постов", className="d-block text-muted"),
                html.Small("V = просмотры, d = дней", className="d-block text-muted"),
            ], style={
                "padding": "16px", "background": "#eff6ff", "borderRadius": "12px",
                "height": "100%", "display": "flex", "flexDirection": "column", "justifyContent": "center",
            }),
            width=12, sm=6, md=3,
        ),
    ], className="g-3 mb-4")

    # ── Donut реакций + График ERday с линией нормы ───────────────────────────
    donut = reactions_donut(abs_cur)

    er_day_norm = get_norm("er_day")
    if not erday_df.empty and "post_date" in erday_df.columns:
        erday_fig = go.Figure()
        erday_fig.add_trace(go.Scatter(
            x=erday_df["post_date"].tolist(),
            y=erday_df["er_day"].astype(float).tolist(),
            mode="lines+markers",
            name="ERday",
            line=dict(color=PRIMARY, width=2),
            marker=dict(color=SECONDARY, size=5),
            hovertemplate="%{x|%d %b}<br>ERday: %{y:.4f}%<extra></extra>",
        ))
        apply_theme(erday_fig, title="Динамика ERday по дням", height=280)
        erday_fig.update_layout(yaxis_title="ERday, %", xaxis_title="Дата", hovermode="x unified")
        if er_day_norm:
            erday_fig.add_hline(
                y=float(er_day_norm),
                line_dash="dot",
                line_color="#94a3b8",
                line_width=1.5,
                annotation_text=f"Норма: {er_day_norm}%",
                annotation_position="top right",
                annotation_font_size=11,
                annotation_font_color="#64748b",
            )
        erday_chart = dcc.Graph(figure=erday_fig, config={"displayModeBar": False})
    else:
        erday_chart = html.Div("Нет данных за выбранный период.", className="text-muted p-3")

    erday_card = dbc.Card(
        dbc.CardBody([
            html.H6("Динамика ERday по дням", style=SECTION_TITLE_STYLE),
            erday_chart,
        ], style={"padding": "20px"}),
        style={**CARD_STYLE, "height": "100%"},
    )

    mid_row = dbc.Row([
        dbc.Col(donut, width=12, md=4),
        dbc.Col(erday_card, width=12, md=8),
    ], className="g-3 mb-4")

    # ── Тепловая карта просмотров ─────────────────────────────────────────────
    if not heatmap_df.empty and "day_of_week" in heatmap_df.columns:
        pivot = heatmap_df.pivot_table(
            index="day_of_week", columns="hour_of_day", values="avg_views", aggfunc="mean"
        )
        pivot = pivot.reindex(index=range(1, 8), columns=range(0, 24), fill_value=0)
        y_labels = [_DAY_NAMES[i] for i in range(1, 8)]
        heatmap_fig = go.Figure(go.Heatmap(
            z=pivot.values.tolist(),
            x=[str(h) for h in range(0, 24)],
            y=y_labels,
            colorscale="Blues",
            hoverongaps=False,
            hovertemplate="День: %{y}<br>Час: %{x}<br>Ср.просмотры: %{z:.0f}<extra></extra>",
        ))
        apply_theme(heatmap_fig, title="Средние просмотры: день недели × час", height=300)
        heatmap_fig.update_layout(
            xaxis_title="Час публикации",
            yaxis_title="День недели",
            margin=dict(l=60, r=20, t=50, b=40),
        )
        heatmap_chart = dcc.Graph(figure=heatmap_fig, config={"displayModeBar": False})
    else:
        heatmap_chart = html.Div("Нет данных за выбранный период.", className="text-muted")

    heatmap_card = dbc.Card(
        dbc.CardBody([
            html.H6("Активность по времени публикации", style=SECTION_TITLE_STYLE),
            heatmap_chart,
        ], style={"padding": "20px"}),
        style=CARD_STYLE,
        className="mb-4",
    )

    # ── Динамика просмотров (текущий период) ──────────────────────────────────
    if not views_df.empty and "post_date" in views_df.columns:
        views_fig = go.Figure()
        views_fig.add_trace(go.Scatter(
            x=views_df["post_date"].tolist(),
            y=[float(v) for v in views_df["total_views"].tolist()],
            mode="lines+markers",
            name="Просмотры",
            line=dict(color=SECONDARY, width=2),
            marker=dict(color=PRIMARY, size=5),
            hovertemplate="%{x|%d %b}<br>Просмотры: %{y:,.0f}<extra></extra>",
        ))
        apply_theme(views_fig, title="Динамика просмотров по дням", height=260)
        views_fig.update_layout(yaxis_title="Просмотры", xaxis_title="Дата", hovermode="x unified")
        views_chart = dcc.Graph(figure=views_fig, config={"displayModeBar": False})
    else:
        views_chart = html.Div("Нет данных за выбранный период.", className="text-muted")

    views_card = dbc.Card(
        dbc.CardBody([
            html.H6("Динамика просмотров", style=SECTION_TITLE_STYLE),
            views_chart,
        ], style={"padding": "20px"}),
        style=CARD_STYLE,
        className="mb-4",
    )

    # ── ERcontent по типам контента ───────────────────────────────────────────
    if not content_df.empty and "content_type" in content_df.columns:
        content_df["er_content"] = pd.to_numeric(content_df["er_content"], errors="coerce")
        content_df["label"] = content_df.apply(
            lambda r: f"{r['er_content']:.2f}%  ({int(r['posts_count'])} пост.)"
            if pd.notna(r["er_content"])
            else f"— ({int(r['posts_count'])} пост.)",
            axis=1,
        )
        bar_colors = [CONTENT_TYPE_COLORS.get(ct, PRIMARY) for ct in content_df["content_type"]]
        bar_fig = go.Figure(go.Bar(
            x=content_df["er_content"],
            y=content_df["content_type"],
            orientation="h",
            text=content_df["label"],
            textposition="outside",
            marker_color=bar_colors,
            hovertemplate="Тип: %{y}<br>ERcontent: %{x:.4f}%<extra></extra>",
        ))
        apply_theme(bar_fig, title="Вовлечённость по типу контента (ERcontent)", height=240)
        bar_fig.update_layout(
            xaxis_title="ERcontent, %",
            yaxis_title="",
            margin=dict(l=80, r=220, t=50, b=40),
        )
        bar_fig.update_xaxes(automargin=True)
        bar_fig.update_yaxes(automargin=True)
        bar_fig.update_traces(cliponaxis=False)
        bar_chart = dcc.Graph(figure=bar_fig, config={"displayModeBar": False})
    else:
        bar_chart = html.Div("Нет данных за выбранный период.", className="text-muted")

    content_card = dbc.Card(
        dbc.CardBody([
            html.H6("Вовлечённость по типу контента", style=SECTION_TITLE_STYLE),
            bar_chart,
        ], style={"padding": "20px"}),
        style=CARD_STYLE,
        className="mb-4",
    )

    # ── Топ-5 публикаций по ERpost ────────────────────────────────────────────
    if not top_df.empty:
        top_df["posted_at_fmt"] = pd.to_datetime(top_df["posted_at"]).dt.strftime("%d.%m.%Y %H:%M")
        top_df["er_post_fmt"] = pd.to_numeric(top_df["er_post"], errors="coerce").apply(
            lambda v: f"{v:.4f}%" if pd.notna(v) else "—"
        )

        table_cols = [
            {"name": "Дата",          "id": "posted_at_fmt"},
            {"name": "Тип",           "id": "content_type"},
            {"name": "Текст (превью)","id": "text_preview"},
            {"name": "Просмотры",     "id": "views_count"},
            {"name": "Лайки",         "id": "likes_count"},
            {"name": "Комментарии",   "id": "comments_count"},
            {"name": "Репосты",       "id": "reposts_count"},
            {"name": "ERpost",        "id": "er_post_fmt"},
            {"name": "Открыть",       "id": "url", "presentation": "markdown"},
        ]

        table_data = top_df[
            ["posted_at_fmt", "content_type", "text_preview", "views_count",
             "likes_count", "comments_count", "reposts_count", "er_post_fmt", "url"]
        ].to_dict("records")

        for row in table_data:
            row["url"] = f"[→]({row['url']})"

        type_styles = [
            {
                "if": {"filter_query": f'{{content_type}} = "{ct}"', "column_id": "content_type"},
                "backgroundColor": colors["backgroundColor"],
                "color": colors["color"],
                "fontWeight": "600",
                "textAlign": "center",
            }
            for ct, colors in _TYPE_CHIP_STYLES.items()
        ]

        top_table = dash_table.DataTable(
            data=table_data,
            columns=table_cols,
            sort_action="native",
            page_size=5,
            style_table={"overflowX": "auto"},
            style_cell={
                "fontFamily": "inherit",
                "fontSize": "0.875rem",
                "padding": "10px 12px",
                "maxWidth": "300px",
                "overflow": "hidden",
                "textOverflow": "ellipsis",
                "whiteSpace": "nowrap",
            },
            style_header={
                "backgroundColor": "#eff6ff",
                "fontWeight": "600",
                "fontSize": "0.8rem",
                "color": "#374151",
                "borderBottom": "1px solid #e2e8f0",
            },
            style_data_conditional=[
                {"if": {"row_index": "odd"}, "backgroundColor": "#f8fafc"},
                *type_styles,
            ],
            tooltip_data=[
                {"text_preview": {"value": row.get("text_preview", ""), "type": "text"}}
                for row in table_data
            ],
            tooltip_delay=0,
            tooltip_duration=None,
        )
    else:
        top_table = html.Div("Нет данных за выбранный период.", className="text-muted")

    top_card = dbc.Card(
        dbc.CardBody([
            html.H6("Топ-5 публикаций по ERpost", style=SECTION_TITLE_STYLE),
            top_table,
        ], style={"padding": "20px"}),
        style=CARD_STYLE,
        className="mb-4",
    )

    return html.Div([er_row_1, er_row_2, mid_row, heatmap_card, views_card, content_card, top_card])
