"""Компонент KPI-карточки с опциональным спарклайном."""
from __future__ import annotations

from typing import Any

import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import dcc, html

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
        return f"{value:{fmt}}".replace(",", " ")
    return f"{value:,}".replace(",", " ")


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


def _sparkline(current_vals: list[float], prev_vals: list[float]) -> dcc.Graph:
    """Мини-график ~120×30px: текущая неделя поверх прошлой."""
    fig = go.Figure()
    if prev_vals:
        fig.add_trace(go.Scatter(
            y=prev_vals,
            mode="lines",
            line=dict(color="#cbd5e1", width=1.5),
            hoverinfo="skip",
        ))
    if current_vals:
        fig.add_trace(go.Scatter(
            y=current_vals,
            mode="lines",
            line=dict(color="#3b82f6", width=2),
            hoverinfo="skip",
        ))
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        height=30,
    )
    return dcc.Graph(
        figure=fig,
        config={"displayModeBar": False, "staticPlot": True},
        style={"height": "30px", "marginTop": "8px"},
    )


def kpi_card(
    label: str,
    value: Any,
    previous: Any = None,
    value_fmt: str = ",.0f",
    suffix: str = "",
    tooltip: str = "",
    sparkline_current: list[float] | None = None,
    sparkline_prev: list[float] | None = None,
) -> dbc.Card:
    """KPI-карточка с опциональным сравнением и спарклайном."""
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

    if sparkline_current:
        children.append(_sparkline(sparkline_current, sparkline_prev or []))

    card = dbc.Card(
        dbc.CardBody(children, style={"padding": "16px"}),
        style=CARD_STYLE,
    )

    if tooltip:
        return html.Div(
            [card, dbc.Tooltip(tooltip, target=card_id, placement="top")],
            id=card_id,
        )
    return card
