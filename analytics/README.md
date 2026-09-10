# Skybit Analytics Dashboard

Live KPI dashboard for the Skybit game. Reads anonymous per-run
telemetry from Supabase (`public.plays`) and presents it across three
tabs — **Overview / Live-ops**, **Players & Retention**, and **Gameplay
& Balance** — with each player shown as a deterministic petname + color
swatch instead of a raw UUID.

Built with Streamlit + Plotly + pandas. Deployed to Streamlit
Community Cloud.

## Layout

```
app.py        entrypoint — sidebar, one wide data pull, 3× st.tabs → tabs/*
data.py       Supabase REST fetch + 60s cache; fixture mode rebases to "now"
filters.py    plausibility ceiling + date helpers
theme.py      single Plotly visual identity (palette + style())
metrics/      pure pandas aggregations, split overview/players/gameplay
charts/       Plotly builders, split the same way
tabs/         per-tab Streamlit render(df, window)
identity.py   device_id → (petname, color)
```

`metrics/` and `charts/` re-export flat from their `__init__`, so
`import metrics; metrics.dau_today(df)` and `charts.score_hist(...)`
still work — the split is per-tab for editing, not for the namespace.

## Local development

The fast loop uses a bundled fixture (no Supabase credentials needed):

```bash
cd analytics
pip install -r requirements.txt
STREAMLIT_USE_FIXTURE=1 streamlit run app.py
```

To run against the live database locally, copy
`.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`, paste
the project's service-role key, and drop the env var:

```bash
streamlit run app.py
```

`secrets.toml` is gitignored.

## Tests

```bash
cd analytics
pip install pytest
pytest
```

## Deployment (Streamlit Community Cloud)

1. Sign in at <https://share.streamlit.io> with the GitHub account
   that owns `ytocker/skybit`.
2. New app → branch `v5_analytics`, main file `analytics/app.py`.
   (Pointing Cloud at a new branch is a manual step in the app's
   Settings → General; do it once when promoting this revision.)
3. Settings → Secrets, paste:
   ```toml
   [supabase]
   url = "https://<project-ref>.supabase.co"
   service_role_key = "..."
   ```
4. Save. Streamlit Cloud builds and serves. Future pushes to the
   configured branch auto-redeploy.

## Why the service-role key (and why not GitHub Pages)

`public.plays` deliberately has no `anon` SELECT policy — only the
service-role key can read it. That key bypasses RLS, so it must stay
server-side. Streamlit Community Cloud server-renders the Python and
injects the key via encrypted environment, so it never reaches the
browser. A static-only host like GitHub Pages would have to either
ship the key in the bundle (instant full DB compromise) or open up
RLS (telemetry table becomes public-readable). Neither is acceptable.

## What's on the dashboard

**Overview / Live-ops** — DAU & plays with day-over-day and 7d deltas,
data freshness, cheat/rejection rate (`submit_error`); plays + uniques
per day, rejected-submit reasons, a daily-volume anomaly band, and the
weekday × hour heatmap.

**Players & Retention** — new players, returning rate, D1/D7 retention,
bounce; the pooled retention curve, a cohort retention triangle,
new-vs-returning per day, session-depth histogram, engagement segments,
and the top-50 active-player roster (petname + color).

**Gameplay & Balance** — median/p90 score, median survival, coins-per-
run; score & survival histograms, score percentiles per day, skill over
time, power-up pickup mix, **power-up efficacy** (score lift with vs
without each power-up), and the coin economy trend.

All charts apply the same plausibility ceiling the game itself accepts
(`score ≤ 100,000`). Retention always runs over a wide ≥120-day frame so
cohorts are settled, independent of the sidebar window.

## Refresh strategy

`streamlit-autorefresh` ticks every 60 seconds. Data fetchers are
cached with `st.cache_data(ttl=60)` so the autorefresh hits cache for
concurrent viewers — only one viewer per minute actually queries
Supabase. The sidebar "Refresh now" button clears the cache.
