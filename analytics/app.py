"""
Skybit analytics dashboard — Streamlit entrypoint.

Three tabs, one data pull. The sidebar window drives display charts; the
fetch always pulls a wider frame (≥120d) so retention cohorts are real
regardless of the chosen window. Tabs delegate to tabs/*.render so this
file stays pure orchestration.

Live refresh: streamlit-autorefresh ticks every 60s; data fetchers are
st.cache_data(ttl=60) so concurrent viewers share one Supabase pull.

Run locally with sample data:
    STREAMLIT_USE_FIXTURE=1 streamlit run analytics/app.py
With live Supabase: drop creds into .streamlit/secrets.toml first.
"""
from __future__ import annotations

import streamlit as st
from streamlit_autorefresh import st_autorefresh

import data
import tabs
from constants import MAX_PLAUSIBLE_SCORE
from filters import plausible

# Cohorts need history older than any display window; fetch at least this
# many days so D7 retention has settled cohorts to measure.
COHORT_DAYS = 120


st.set_page_config(
    page_title="Skybit · Analytics",
    page_icon="🐦",
    layout="wide",
    initial_sidebar_state="expanded",
)

st_autorefresh(interval=60_000, key="tick")


# ── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### Skybit · Analytics")
    st.caption("Live, anonymous gameplay telemetry. UTC.")

    window = st.selectbox(
        "Window",
        options=[7, 30, 90],
        index=1,
        format_func=lambda d: f"Last {d} days",
        help="Drives the display charts. 'Today' KPIs always look at "
             "UTC-today; retention always uses a wide ≥120-day frame.",
    )

    if st.button("Refresh now", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.divider()
    st.caption(
        f"Plausibility-filtered: rows with score > {MAX_PLAUSIBLE_SCORE:,} are "
        "dropped before any chart sees them. Matches the game's own ceiling."
    )


# ── Data ─────────────────────────────────────────────────────────────────────

try:
    raw = data.fetch_plays(days=max(window, COHORT_DAYS))
except RuntimeError as e:
    st.error(str(e))
    st.stop()

df = plausible(raw)

st.title("🐦 Skybit Analytics")

if df.empty:
    st.warning("No plays in the selected window yet. Once players run the "
               "deployed game, rows will appear here within ~60s.")
    st.stop()

if data.hit_row_cap(raw):
    st.warning(f"Fetch hit the {data.ROW_CAP:,}-row cap — the oldest history "
               "in this window may be truncated.")


# ── Tabs ─────────────────────────────────────────────────────────────────────

tab_overview, tab_players, tab_gameplay = st.tabs(
    ["📡 Overview", "👥 Players & Retention", "🎮 Gameplay & Balance"]
)

with tab_overview:
    tabs.render_overview(df, window)

with tab_players:
    tabs.render_players(df, window)

with tab_gameplay:
    tabs.render_gameplay(df, window)
