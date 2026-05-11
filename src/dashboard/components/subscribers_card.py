"""Карточка динамики подписчиков."""
from __future__ import annotations

from typing import Any

import dash_bootstrap_components as dbc
from dash import html


def subscribers_card(data: dict[str, Any]) -> dbc.Card:
    """Карточка с текущим числом подписчиков и приростом за период."""
    n_end = data.get("n_end")
    delta = data.get("delta")
    delta_pct = data.get("delta_pct")

    if n_end is None:
        value_str = "—"
        delta_el = html.Span()
    else:
        value_str = f"{int(n_end):,}".replace(",", " ")
        if delta is not None and delta_pct is not None:
            arrow = "▲" if delta >= 0 else "▼"
            color = "#16a34a" if delta >= 0 else "#dc2626"
            sign = "+" if delta >= 0 else ""
            delta_el = html.Div([
                html.Span(
                    f"{arrow} {sign}{int(delta):,}".replace(",", " "),
                    style={"color": color, "fontWeight": "600", "fontSize": "0.9rem"},
                ),
                html.Span(
                    f"  ({sign}{float(delta_pct):.2f}%)",
                    style={"color": color, "fontSize": "0.8rem", "marginLeft": "4px"},
                ),
            ], style={"marginTop": "4px"})
        else:
            delta_el = html.Span()

    return dbc.Card(
        dbc.CardBody([
            html.Div(
                value_str,
                style={
                    "fontSize": "2rem",
                    "fontWeight": "700",
                    "color": "#1e40af",
                    "lineHeight": "1.1",
                },
            ),
            delta_el,
            html.Div(
                "ПОДПИСЧИКИ",
                style={
                    "fontSize": "0.75rem",
                    "fontWeight": "600",
                    "color": "#64748b",
                    "textTransform": "uppercase",
                    "letterSpacing": "0.05em",
                    "marginTop": "6px",
                },
            ),
        ], style={"padding": "20px"}),
        style={
            "borderRadius": "12px",
            "boxShadow": "0 1px 3px rgba(15,23,42,0.06)",
            "border": "1px solid #e2e8f0",
            "backgroundColor": "#ffffff",
            "height": "100%",
        },
    )
