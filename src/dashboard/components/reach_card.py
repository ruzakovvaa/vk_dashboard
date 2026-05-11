"""Карточки охвата и виральности (оценочные — без прав администратора)."""
from __future__ import annotations

from typing import Any

import dash_bootstrap_components as dbc
from dash import html


def _card(title: str, value_str: str, sub: str, is_estimate: bool = False) -> dbc.Card:
    children = [
        html.Div(
            value_str,
            style={
                "fontSize": "2rem",
                "fontWeight": "700",
                "color": "#1e40af",
                "lineHeight": "1.1",
            },
        ),
        html.Div(
            title,
            style={
                "fontSize": "0.75rem",
                "fontWeight": "600",
                "color": "#64748b",
                "textTransform": "uppercase",
                "letterSpacing": "0.05em",
                "marginTop": "6px",
            },
        ),
        html.Div(
            sub,
            style={"fontSize": "0.75rem", "color": "#94a3b8", "marginTop": "4px"},
        ),
    ]
    if is_estimate:
        children.append(
            html.Span(
                "оценка",
                style={
                    "fontSize": "0.65rem",
                    "background": "#fef9c3",
                    "color": "#854d0e",
                    "borderRadius": "4px",
                    "padding": "1px 6px",
                    "marginTop": "6px",
                    "display": "inline-block",
                },
            )
        )
    return dbc.Card(
        dbc.CardBody(children, style={"padding": "20px"}),
        style={
            "borderRadius": "12px",
            "boxShadow": "0 1px 3px rgba(15,23,42,0.06)",
            "border": "1px solid #e2e8f0",
            "backgroundColor": "#ffffff",
            "height": "100%",
        },
    )


def reach_card(data: dict[str, Any]) -> dbc.Card:
    """Карточка охвата. Использует просмотры как нижнюю оценку охвата."""
    reach = data.get("reach_estimated")
    val = f"{int(reach):,}".replace(",", " ") if reach else "—"
    return _card("ОХВАТ", val, "≈ просмотры (оценка, нет прав адм.)", is_estimate=True)


def virality_card(data: dict[str, Any]) -> dbc.Card:
    """Карточка виральности через прокси репостов."""
    pct = data.get("virality_pct")
    insufficient = data.get("data_insufficient", False)
    if insufficient:
        val = "—"
        sub = "недостаточно данных"
    elif pct is not None:
        val = f"{float(pct):.2f}%"
        sub = "репосты × 40% охвата / просмотры"
    else:
        val = "—"
        sub = "репосты × 40% охвата / просмотры"
    return _card("ВИРАЛЬНОСТЬ", val, sub, is_estimate=True)
