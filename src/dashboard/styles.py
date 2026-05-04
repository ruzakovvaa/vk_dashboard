"""Цветовая палитра и общие стили дашборда."""
from __future__ import annotations

PRIMARY = "#1565C0"
SECONDARY = "#42A5F5"
ACCENT = "#E53935"
SUCCESS = "#43A047"
WARNING = "#FB8C00"
MUTED = "#78909C"
BACKGROUND = "#F5F7FA"
CARD_BG = "#FFFFFF"

PLOTLY_PALETTE = [PRIMARY, SECONDARY, "#66BB6A", WARNING, ACCENT, "#AB47BC"]

CONTENT_TYPE_COLORS = {
    "photo": PRIMARY,
    "video": ACCENT,
    "text": MUTED,
    "link": WARNING,
}

CARD_STYLE = {
    "borderRadius": "12px",
    "boxShadow": "0 2px 8px rgba(0,0,0,0.08)",
    "padding": "20px",
    "backgroundColor": CARD_BG,
    "height": "100%",
}

KPI_VALUE_STYLE = {
    "fontSize": "2rem",
    "fontWeight": "700",
    "color": PRIMARY,
    "marginBottom": "4px",
}

KPI_LABEL_STYLE = {
    "fontSize": "0.85rem",
    "color": MUTED,
    "textTransform": "uppercase",
    "letterSpacing": "0.05em",
}

DELTA_UP_STYLE = {"color": SUCCESS, "fontWeight": "600"}
DELTA_DOWN_STYLE = {"color": ACCENT, "fontWeight": "600"}
DELTA_NEUTRAL_STYLE = {"color": MUTED, "fontWeight": "600"}
