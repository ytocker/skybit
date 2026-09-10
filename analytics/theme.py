"""
One visual identity for every Plotly figure on the dashboard.

Centralising the palette + the base layout here (rather than per chart)
is what keeps the three tabs reading as one product: same accent, same
transparent background that lets the Streamlit dark theme show through,
same tight margins and title treatment. Chart builders import from here
and never re-declare colours.
"""
from __future__ import annotations

import plotly.graph_objects as go

# Core palette — matches the game's biome sky + coin gold so the
# dashboard feels of-a-piece with Skybit itself.
SKY = "#4DA3FF"
SKY_SOFT = "rgba(77, 163, 255, 0.35)"
GOLD = "#F4C95D"
CORAL = "#FF8E5C"          # secondary accent for "max"/"p90" type series
INK = "#0F1B2D"
MUTED = "#9AA7BD"          # subtitles, captions, de-emphasised text
GRID = "rgba(120,120,120,0.18)"

# Ordered categorical palette for multi-series charts (cohorts, segments).
SEQUENCE = (SKY, GOLD, CORAL, "#7ED9A6", "#B58BFF", "#FF6FA5", "#5BC8E6")

_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="system-ui, sans-serif"),
    hoverlabel=dict(bgcolor="white"),
    colorway=list(SEQUENCE),
)


def style(
    fig: go.Figure,
    title: str | None = None,
    subtitle: str | None = None,
    height: int = 320,
) -> go.Figure:
    """Apply the shared layout. `subtitle` (Plotly's native title.subtitle,
    so it never collides with the title) is the place for a caveat
    ("correlational, not causal") or a window note. automargin on both
    axes keeps tick labels and axis titles from clipping regardless of
    how wide the panel renders."""
    title_spec = None
    if title:
        title_spec = dict(text=title, x=0.0, xanchor="left", font=dict(size=15))
        if subtitle:
            title_spec["subtitle"] = dict(text=subtitle,
                                          font=dict(size=11, color=MUTED))
    fig.update_layout(
        **_LAYOUT,
        height=height,
        margin=dict(l=12, r=16, t=64 if subtitle else 48, b=12),
        title=title_spec,
    )
    fig.update_xaxes(showgrid=False, zeroline=False, automargin=True)
    fig.update_yaxes(gridcolor=GRID, zeroline=False, automargin=True)
    return fig
