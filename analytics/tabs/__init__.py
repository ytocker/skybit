"""Tab render functions — one module per dashboard tab. Each exposes a
render(df, window) that draws its Streamlit layout, keeping app.py to
pure orchestration."""
from __future__ import annotations

from tabs.overview import render as render_overview  # noqa: F401
from tabs.players import render as render_players  # noqa: F401
from tabs.gameplay import render as render_gameplay  # noqa: F401
