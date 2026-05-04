"""Компонент KPI-карточки для дашборда."""
from __future__ import annotations

from typing import Any

import dash_bootstrap_components as dbc
from dash import html

from src.dashboard.styles import (
    CARD_STYLE,
    DELTA_DOWN_STYLE,
    DELTA_NEUTRAL_STYLE,
    DELTA_UP_STYLE,
    KPI_LABEL_STYLE,
    KPI_VALUE_STYLE,
)


def _format_value(value: Any, fmt: str = ",.0f") -> str:
    if value is None:
        return "—"
    if isinstance(value, float):
        return f"{value:{fmt}}"
    return f"{value:,}"


def _delta_element(current: Any, previous: Any) -> html.Span:
    if current is None or previous is None or previous == 0:
        return html.Span()
    pct = (current - previous) / previous * 100
    if pct > 0:
        arrow, style = f"▲ {pct:.1f}%", DELTA_UP_STYLE
    elif pct < 0:
        arrow, style = f"▼ {abs(pct):.1f}%", DELTA_DOWN_STYLE
    else:
        arrow, style = "— 0%", DELTA_NEUTRAL_STYLE
    return html.Span(arrow, style={**style, "fontSize": "0.85rem", "marginLeft": "6px"})


def kpi_card(
    label: str,
    value: Any,
    previous: Any = None,
    value_fmt: str = ",.0f",
    suffix: str = "",
    tooltip: str = "",
) -> dbc.Card:
    """Создаёт KPI-карточку с опциональным сравнением с предыдущим периодом."""
    val_str = _format_value(value, value_fmt) + suffix
    delta = _delta_element(value, previous)

    card_id = f"kpi-{label.lower().replace(' ', '-')}"
    children = [
        html.Div(
            [html.Span(val_str, style=KPI_VALUE_STYLE), delta],
            style={"display": "flex", "alignItems": "baseline"},
        ),
        html.Div(label, style=KPI_LABEL_STYLE),
    ]

    card = dbc.Card(
        dbc.CardBody(children, style={"padding": "16px"}),
        style=CARD_STYLE,
    )

    if tooltip:
        return html.Div(
            [
                card,
                dbc.Tooltip(tooltip, target=card_id, placement="top"),
            ],
            id=card_id,
        )
    return card
