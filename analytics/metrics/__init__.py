"""
Metrics package — split by dashboard tab (overview / players / gameplay)
but re-exported flat so callers and tests keep the original
`import metrics; metrics.dau_today(df)` surface. The split is for the
humans editing one tab at a time; the namespace stays single.
"""
from __future__ import annotations

from metrics.overview import (  # noqa: F401
    by_day,
    daily_plays_with_band,
    dau_today,
    dau_yesterday,
    hourly_heatmap,
    minutes_since_last_play,
    plays_today,
    plays_window_delta,
    plays_yesterday,
    rejection_rate,
    rejection_reasons,
)
from metrics.players import (  # noqa: F401
    active_players,
    cohort_retention,
    engagement_segments,
    new_players_today,
    new_vs_returning_by_day,
    one_shot_count,
    retention_curve,
    retention_matrix,
    retention_summary,
    returning_rate_7d,
    roster,
    sessions_per_active_day,
)
from metrics.gameplay import (  # noqa: F401
    coin_economy_by_day,
    coins_per_run,
    duration_distribution,
    duration_summary,
    powerup_efficacy,
    powerup_totals,
    powerups_per_run_by_day,
    score_distribution,
    score_quantiles_by_day,
    score_summary,
    skill_proxy_by_day,
)
