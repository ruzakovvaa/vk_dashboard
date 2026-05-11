"""Donut-диаграмма распределения реакций."""
from __future__ import annotations

from typing import Any

import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import dcc, html

from src.utils.plotly_theme import apply_theme


def _audience_label(likes: int, comments: int, reposts: int) -> str:
    total = likes + comments + reposts
    if total == 0:
        return ""
    comments_pct = comments / total * 100
    likes_pct = likes / total * 100
    if comments_pct > 15:
        return "Активная дискуссионная аудитория"
    if likes_pct > 85:
        return "Пассивно-одобрительная аудитория"
    return ""


def reactions_donut(abs_data: dict[str, Any]) -> dbc.Card:
    likes = int(abs_data.get("total_likes") or 0)
    comments = int(abs_data.get("total_comments") or 0)
    reposts = int(abs_data.get("total_reposts") or 0)
    total = likes + comments + reposts

    if total == 0:
        chart = html.Div("Нет данных за выбранный период.", className="text-muted")
        legend = html.Div()
        label = html.Div()
    else:
        fig = go.Figure(go.Pie(
            labels=["Лайки", "Комментарии", "Репосты"],
            values=[likes, comments, reposts],
            hole=0.6,
            marker_colors=["#3b82f6", "#f97316", "#10b981"],
            textinfo="none",
            hovertemplate="%{label}: %{value:,} (%{percent})<extra></extra>",
        ))
        fig.update_layout(
            paper_bgcolor="white",
            plot_bgcolor="white",
            margin=dict(l=0, r=0, t=0, b=0),
            height=200,
            showlegend=False,
            annotations=[dict(
                text=f"<b>{total:,}</b>".replace(",", " "),
                x=0.5, y=0.5,
                font=dict(size=18, color="#0f172a", family="Inter, sans-serif"),
                showarrow=False,
            )],
        )
        chart = dcc.Graph(
            figure=fig,
            config={"displayModeBar": False},
            style={"height": "200px"},
        )

        def _row(label: str, val: int, color: str) -> html.Div:
            pct = val / total * 100
            return html.Div([
                html.Span("●", style={"color": color, "marginRight": "6px"}),
                html.Span(label, style={"color": "#0f172a", "fontSize": "0.85rem"}),
                html.Span(
                    f"{val:,}  ({pct:.1f}%)".replace(",", " "),
                    style={"color": "#64748b", "fontSize": "0.8rem", "marginLeft": "auto"},
                ),
            ], style={"display": "flex", "alignItems": "center", "padding": "4px 0"})

        legend = html.Div([
            _row("Лайки", likes, "#3b82f6"),
            _row("Комментарии", comments, "#f97316"),
            _row("Репосты", reposts, "#10b981"),
        ], style={"marginTop": "12px"})

        audience = _audience_label(likes, comments, reposts)
        label = html.Div(
            audience,
            style={
                "marginTop": "12px",
                "fontSize": "0.8rem",
                "color": "#1e40af",
                "fontWeight": "600",
                "textAlign": "center",
                "background": "#eff6ff",
                "borderRadius": "8px",
                "padding": "6px 12px",
            },
        ) if audience else html.Div()

    return dbc.Card(
        dbc.CardBody([
            html.H6(
                "Распределение реакций",
                style={
                    "fontSize": "0.75rem",
                    "fontWeight": "600",
                    "color": "#64748b",
                    "textTransform": "uppercase",
                    "letterSpacing": "0.05em",
                    "marginBottom": "12px",
                },
            ),
            chart,
            legend,
            label,
        ], style={"padding": "20px"}),
        style={
            "borderRadius": "12px",
            "boxShadow": "0 1px 3px rgba(15,23,42,0.06)",
            "border": "1px solid #e2e8f0",
            "backgroundColor": "#ffffff",
            "height": "100%",
        },
    )
