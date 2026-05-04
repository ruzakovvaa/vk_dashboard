"""Страница «Статистика»: тепловая карта, ERcontent, топ публикаций."""
from __future__ import annotations

from datetime import date

import dash_bootstrap_components as dbc
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, callback, dash_table, dcc, html, register_page

from src.dashboard import data_access as da
from src.dashboard.styles import BACKGROUND, CONTENT_TYPE_COLORS, PRIMARY

register_page(__name__, path="/statistics", name="Статистика")

_DAY_NAMES = {1: "Пн", 2: "Вт", 3: "Ср", 4: "Чт", 5: "Пт", 6: "Сб", 7: "Вс"}


def layout() -> html.Div:
    return html.Div(
        [
            dcc.Loading(
                id="stats-loading",
                type="circle",
                children=html.Div(id="stats-content"),
            )
        ],
        style={"backgroundColor": BACKGROUND, "minHeight": "100vh", "padding": "24px"},
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
        heatmap_df = da.get_heatmap(date_from, date_to)
        content_df = da.get_content_type(date_from, date_to)
        top_df = da.get_top_posts(date_from, date_to, limit=10)
    except Exception as exc:
        return html.Div(f"Ошибка загрузки данных: {exc}", className="text-danger")

    # ── Блок 1: Тепловая карта просмотров ─────────────────────────────────────
    if not heatmap_df.empty and "day_of_week" in heatmap_df.columns:
        pivot = heatmap_df.pivot_table(
            index="day_of_week", columns="hour_of_day", values="avg_views", aggfunc="mean"
        )
        # Заполняем недостающие часы нулями
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
        heatmap_fig.update_layout(
            title="Средние просмотры публикаций: день недели × час",
            xaxis_title="Час публикации",
            yaxis_title="День недели",
            plot_bgcolor="white",
            paper_bgcolor="white",
            margin=dict(l=60, r=20, t=60, b=40),
        )
        heatmap_chart = dcc.Graph(figure=heatmap_fig, config={"displayModeBar": False})
    else:
        heatmap_chart = html.Div("Нет данных за выбранный период.", className="text-muted")

    heatmap_card = dbc.Card(
        dbc.CardBody([
            html.H5("Активность по времени публикации", className="card-title mb-3"),
            heatmap_chart,
        ]),
        style={"borderRadius": "12px", "boxShadow": "0 2px 8px rgba(0,0,0,0.08)"},
        className="mb-4",
    )

    # ── Блок 2: ERcontent по типам контента ───────────────────────────────────
    if not content_df.empty and "content_type" in content_df.columns:
        content_df["er_content"] = pd.to_numeric(content_df["er_content"], errors="coerce")
        content_df["label"] = content_df.apply(
            lambda r: f"{r['er_content']:.2f}% ({int(r['posts_count'])} постов)"
            if pd.notna(r["er_content"])
            else f"— ({int(r['posts_count'])} постов)",
            axis=1,
        )
        bar_colors = [
            CONTENT_TYPE_COLORS.get(ct, PRIMARY)
            for ct in content_df["content_type"]
        ]
        bar_fig = go.Figure(go.Bar(
            x=content_df["er_content"],
            y=content_df["content_type"],
            orientation="h",
            text=content_df["label"],
            textposition="outside",
            marker_color=bar_colors,
            hovertemplate="Тип: %{y}<br>ERcontent: %{x:.4f}%<extra></extra>",
        ))
        bar_fig.update_layout(
            title="Вовлечённость по типу контента (ERcontent)",
            xaxis_title="ERcontent, %",
            yaxis_title="Тип контента",
            plot_bgcolor="white",
            paper_bgcolor="white",
            margin=dict(l=80, r=120, t=60, b=40),
        )
        bar_chart = dcc.Graph(figure=bar_fig, config={"displayModeBar": False})
    else:
        bar_chart = html.Div("Нет данных за выбранный период.", className="text-muted")

    content_card = dbc.Card(
        dbc.CardBody([
            html.H5("Вовлечённость по типу контента", className="card-title mb-3"),
            bar_chart,
        ]),
        style={"borderRadius": "12px", "boxShadow": "0 2px 8px rgba(0,0,0,0.08)"},
        className="mb-4",
    )

    # ── Блок 3: Топ-10 публикаций по ERpost ───────────────────────────────────
    if not top_df.empty:
        top_df["posted_at_fmt"] = pd.to_datetime(top_df["posted_at"]).dt.strftime("%d.%m.%Y %H:%M")
        top_df["er_post_fmt"] = pd.to_numeric(top_df["er_post"], errors="coerce").apply(
            lambda v: f"{v:.4f}%" if pd.notna(v) else "—"
        )
        top_df["link"] = top_df["url"].apply(
            lambda u: f"[Открыть]({u})"
        )

        table_cols = [
            {"name": "Дата", "id": "posted_at_fmt"},
            {"name": "Тип", "id": "content_type"},
            {"name": "Текст (превью)", "id": "text_preview"},
            {"name": "Просмотры", "id": "views_count"},
            {"name": "Лайки", "id": "likes_count"},
            {"name": "Комментарии", "id": "comments_count"},
            {"name": "Репосты", "id": "reposts_count"},
            {"name": "ERpost", "id": "er_post_fmt"},
            {"name": "Ссылка", "id": "url", "presentation": "markdown"},
        ]

        table_data = top_df[
            ["posted_at_fmt", "content_type", "text_preview", "views_count",
             "likes_count", "comments_count", "reposts_count", "er_post_fmt", "url"]
        ].rename(columns={"url": "url"}).to_dict("records")

        # Сделаем ссылки кликабельными через markdown
        for row in table_data:
            row["url"] = f"[Открыть]({row['url']})"

        top_table = dash_table.DataTable(
            data=table_data,
            columns=table_cols,
            sort_action="native",
            page_size=10,
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
                "backgroundColor": "#EEF2FF",
                "fontWeight": "600",
                "fontSize": "0.8rem",
                "color": "#374151",
            },
            style_data_conditional=[
                {"if": {"row_index": "odd"}, "backgroundColor": "#F9FAFB"},
            ],
            tooltip_data=[
                {
                    "text_preview": {"value": row.get("text_preview", ""), "type": "text"}
                }
                for row in table_data
            ],
            tooltip_delay=0,
            tooltip_duration=None,
        )
    else:
        top_table = html.Div("Нет данных за выбранный период.", className="text-muted")

    top_card = dbc.Card(
        dbc.CardBody([
            html.H5("Топ-10 публикаций по ERpost", className="card-title mb-3"),
            top_table,
        ]),
        style={"borderRadius": "12px", "boxShadow": "0 2px 8px rgba(0,0,0,0.08)"},
        className="mb-4",
    )

    return html.Div([heatmap_card, content_card, top_card])
