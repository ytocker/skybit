# v5 analytics redesign — Round 1 (all three tabs)

## Goal
Ground-up rebuild of the Skybit analytics dashboard into three polished
tabs (Overview / Live-ops, Players & Retention, Gameplay & Balance),
replacing the flat single-page layout. Surface previously-wasted signal
(`submit_error`), add real cohort retention and power-up efficacy,
resurrect the dead skill curve, and unify the visual identity.

## Files changed
- `app.py` — rewritten to a thin `st.tabs` orchestrator; one wide
  (≥120d) cached fetch feeds all tabs; row-cap warning.
- `theme.py` (new) — single Plotly identity (palette + `style()` with
  native title/subtitle + axis `automargin`).
- `metrics/` package — `overview.py`, `players.py`, `gameplay.py`,
  `common.py`, flat `__init__` re-exports. New: `plays_window_delta`,
  `minutes_since_last_play`, `rejection_rate/_reasons`,
  `daily_plays_with_band`, `cohort_retention`, `retention_curve`
  (consistent settled-cohort denominator), `retention_matrix`,
  `retention_summary`, `new_vs_returning_by_day`,
  `sessions_per_active_day`, `new_players_today`, `active_players`,
  `score/duration_summary`, `coins_per_run`, `duration_distribution`,
  `powerup_efficacy`, `coin_economy_by_day`. Resurrected
  `skill_proxy_by_day`.
- `charts/` package — split the same way; new builders for anomaly band,
  rejection reasons, retention curve/triangle, new-vs-returning, session
  depth, survival histogram, skill-over-time, efficacy, coin economy.
- `tabs/{overview,players,gameplay}.py` (new) — `render(df, window)`.
- `data.py` — added `submit_error` to select; named `ROW_CAP` +
  `hit_row_cap`; nullable default-fill; fixture-mode `_rebase_to_now`.
- `constants.py` — `MAX_PLAUSIBLE_SCORE` 10_000 → 100_000 (matches game).
- Fixture rebuilt via `tests/fixtures/_generate.py` (437 rows, 37
  devices, ~44-day span, designed cohorts + efficacy signal + rejections).
- Tests: `test_metrics_{overview,players,gameplay}.py`,
  `test_render_smoke.py` (AppTest end-to-end + empty-frame chart smoke);
  `test_metrics.py` → `test_metrics_core.py`.

## Fixture numbers (demo dataset)
- 437 plausible rows, 37 unique devices.
- Retention (consistent settled-cohort denominator): D1 = 23.5%,
  D7 = 20.6%.
- Rejection rate (90d) = 0.9% (4 designed rejected submits).
- Power-up score lift: magnet **+155%**, slowmo +8%, triple/kfc/surprise
  +5%, ghost −4%, grow **−67%** (designed signal — magnet runs authored
  long/high, grow runs short/low).
- One legit 42,000 score retained; one 250,000 dropped by `plausible()`.

## Charts (rendered from fixture)
`reviews/v5-redesign/round_1/`:
- Overview: `ov_plays_uniques.png`, `ov_anomaly.png`, `ov_rejections.png`,
  `ov_heatmap.png`
- Players: `pl_retention_curve.png`, `pl_retention_matrix.png`,
  `pl_new_vs_returning.png`, `pl_sessions.png`, `pl_segments.png`
- Gameplay: `gp_score_hist.png`, `gp_duration_hist.png`, `gp_skill.png`,
  `gp_efficacy.png`, `gp_coin_economy.png`

## Methodology notes / known caveats
- **Retention denominator**: `retention_curve` pools only cohorts old
  enough to be fully observed through D`max_day` (install ≤ today−7) and
  divides every offset by that same device set — avoids the misleading
  non-monotone curve you get from per-offset-eligible pooling. The
  triangle (`retention_matrix`) keeps per-cohort censoring (blank cells).
- **Windowed install**: "install" = first play *in the fetched frame*; a
  device returning after a >120d gap reads as new. Stated in subtitles;
  exact fix needs a server-side `first_seen` (out of scope).
- **Efficacy is correlational** (longer runs see more spawns) — labelled
  on the chart.
- Curve bumps at D3/D6 in the demo are fixture artifacts (synthetic
  returners), not a method bug — the denominator is now consistent.

## Tests
```
54 passed in 1.50s
```
(was 25 before the redesign; AppTest renders all 3 tabs / 15 KPI cards
with no exception.)
