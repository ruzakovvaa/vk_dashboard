"""Цветовая палитра и общие стили дашборда (светлая тема)."""
from __future__ import annotations

# ── Цвета ─────────────────────────────────────────────────────────────────────
PRIMARY    = "#1e40af"   # бренд-синий
SECONDARY  = "#3b82f6"   # графики — синий
ACCENT     = "#f97316"   # оранжевый (комментарии, ссылки)
SUCCESS    = "#16a34a"   # зелёный (рост, норма+)
WARNING    = "#ca8a04"   # жёлтый (норма±)
ERROR      = "#dc2626"   # красный (ниже нормы)
MUTED      = "#64748b"   # вторичный текст
BACKGROUND = "#f8fafc"   # фон страницы (slate-50)
CARD_BG    = "#ffffff"   # фон карточек

# Цвета графиков
PLOTLY_PALETTE = [SECONDARY, ACCENT, "#10b981", "#8b5cf6", PRIMARY, "#ec4899"]
GRAY_PREV      = "#cbd5e1"   # предыдущий период на графиках

CONTENT_TYPE_COLORS = {
    "photo": SECONDARY,
    "video": "#8b5cf6",
    "text":  MUTED,
    "link":  ACCENT,
}

# ── Стили карточек ─────────────────────────────────────────────────────────────
CARD_STYLE = {
    "borderRadius": "12px",
    "boxShadow": "0 1px 3px rgba(15,23,42,0.06)",
    "border": "1px solid #e2e8f0",
    "backgroundColor": CARD_BG,
    "height": "100%",
}

KPI_VALUE_STYLE = {
    "fontSize": "2rem",
    "fontWeight": "700",
    "color": PRIMARY,
    "lineHeight": "1.1",
}

KPI_LABEL_STYLE = {
    "fontSize": "0.75rem",
    "fontWeight": "600",
    "color": MUTED,
    "textTransform": "uppercase",
    "letterSpacing": "0.05em",
    "marginTop": "6px",
}

DELTA_UP_STYLE      = {"color": SUCCESS, "fontWeight": "600"}
DELTA_DOWN_STYLE    = {"color": ERROR,   "fontWeight": "600"}
DELTA_NEUTRAL_STYLE = {"color": MUTED,   "fontWeight": "600"}

SECTION_TITLE_STYLE = {
    "fontSize": "0.75rem",
    "fontWeight": "600",
    "color": MUTED,
    "textTransform": "uppercase",
    "letterSpacing": "0.05em",
    "marginBottom": "12px",
    "marginTop": "8px",
}
