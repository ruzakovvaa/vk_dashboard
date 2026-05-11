"""Единая светлая тема для всех графиков Plotly."""
from __future__ import annotations

BASE_LAYOUT = dict(
    paper_bgcolor="white",
    plot_bgcolor="white",
    font=dict(family='Inter, -apple-system, "Segoe UI", sans-serif', color="#0f172a", size=12),
    margin=dict(l=40, r=16, t=40, b=32),
    xaxis=dict(gridcolor="#f1f5f9", showline=False, zeroline=False),
    yaxis=dict(gridcolor="#f1f5f9", showline=False, zeroline=False),
    hoverlabel=dict(bgcolor="white", bordercolor="#e2e8f0", font=dict(color="#0f172a")),
    legend=dict(bgcolor="rgba(0,0,0,0)", borderwidth=0),
)


def apply_theme(fig, title: str = "", height: int | None = None) -> None:
    """Применяет базовую светлую тему к figure на месте."""
    update = dict(**BASE_LAYOUT)
    if title:
        update["title"] = dict(text=title, font=dict(size=14, color="#0f172a", weight=600), x=0, xanchor="left")
    if height:
        update["height"] = height
    fig.update_layout(**update)
    fig.update_xaxes(gridcolor="#f1f5f9", showline=False, zeroline=False)
    fig.update_yaxes(gridcolor="#f1f5f9", showline=False, zeroline=False)


# Цвета для графиков
BLUE = "#3b82f6"
ORANGE = "#f97316"
GREEN = "#10b981"
PURPLE = "#8b5cf6"
GRAY_PREV = "#cbd5e1"       # предыдущий период
BRAND = "#1e40af"           # акцент бренда
