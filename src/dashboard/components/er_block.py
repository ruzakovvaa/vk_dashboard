"""Карточка коэффициента ER с бенчмарком и цветовой индикацией."""
from __future__ import annotations

from typing import Any

import dash_bootstrap_components as dbc
from dash import html

from src.utils.benchmarks import all_benchmarks, get_benchmark_status, get_norm


def _benchmark_bar(value: float, norm: float, color: str) -> html.Div:
    """Горизонтальная мини-шкала с засечкой нормы и точкой текущего значения."""
    max_val = max(value, norm) * 1.5 or 1.0
    value_pct = min(value / max_val * 100, 100)
    norm_pct = min(norm / max_val * 100, 100)
    diff_pct = round((value - norm) / norm * 100) if norm else 0
    sign = "+" if diff_pct >= 0 else ""

    return html.Div([
        # Шкала
        html.Div([
            html.Div(style={
                "position": "absolute",
                "left": 0, "top": 0, "bottom": 0,
                "width": f"{value_pct}%",
                "backgroundColor": color,
                "borderRadius": "4px",
                "opacity": "0.25",
                "transition": "width 0.3s",
            }),
            # Засечка нормы
            html.Div(style={
                "position": "absolute",
                "left": f"{norm_pct}%",
                "top": 0, "bottom": 0,
                "width": "2px",
                "backgroundColor": "#94a3b8",
            }),
            # Точка текущего значения
            html.Div(style={
                "position": "absolute",
                "left": f"calc({value_pct}% - 4px)",
                "top": "50%",
                "transform": "translateY(-50%)",
                "width": "8px",
                "height": "8px",
                "borderRadius": "50%",
                "backgroundColor": color,
            }),
        ], style={
            "position": "relative",
            "height": "8px",
            "backgroundColor": "#f1f5f9",
            "borderRadius": "4px",
            "marginTop": "8px",
            "marginBottom": "4px",
        }),
        # Подпись
        html.Div(
            f"Норма: {norm:.3f}%",
            style={"fontSize": "0.7rem", "color": "#94a3b8"},
        ),
    ])


def er_metric_card(
    label: str,
    value: float | None,
    metric_key: str,
    tooltip: str = "",
) -> dbc.Card:
    """Карточка одного ER-коэффициента с цветовой индикацией бенчмарка."""
    norm = get_norm(metric_key)
    if value is not None:
        value = float(value)

    if value is None:
        value_str = "—"
        indicator = html.Div()
        border_color = "#e2e8f0"
        dot_color = "#94a3b8"
    else:
        value_str = f"{value:.4f}%"
        if norm:
            _, color = get_benchmark_status(value, norm)
            indicator = _benchmark_bar(value, norm, color)
            border_color = color
            dot_color = color
        else:
            indicator = html.Div()
            border_color = "#e2e8f0"
            dot_color = "#1e40af"

    card_content = dbc.CardBody([
        html.Div([
            # Цветной кружок-индикатор
            html.Span(style={
                "width": "10px",
                "height": "10px",
                "borderRadius": "50%",
                "backgroundColor": dot_color,
                "display": "inline-block",
                "marginRight": "8px",
                "flexShrink": "0",
                "marginTop": "6px",
            }),
            html.Div([
                html.Div(
                    value_str,
                    style={
                        "fontSize": "1.6rem",
                        "fontWeight": "700",
                        "color": "#0f172a",
                        "lineHeight": "1.1",
                    },
                ),
                html.Div(
                    label,
                    style={
                        "fontSize": "0.75rem",
                        "fontWeight": "600",
                        "color": "#64748b",
                        "textTransform": "uppercase",
                        "letterSpacing": "0.05em",
                        "marginTop": "4px",
                    },
                ),
            ]),
        ], style={"display": "flex", "alignItems": "flex-start"}),
        indicator,
        html.Div(
            tooltip,
            style={"fontSize": "0.7rem", "color": "#94a3b8", "marginTop": "6px"},
        ) if tooltip else html.Div(),
    ], style={"padding": "16px"})

    return dbc.Card(
        card_content,
        style={
            "borderRadius": "12px",
            "boxShadow": "0 1px 3px rgba(15,23,42,0.06)",
            "border": f"1px solid {border_color}",
            "backgroundColor": "#ffffff",
            "height": "100%",
        },
    )
