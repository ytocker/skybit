"""
Charts package — split by tab, re-exported flat so existing callers keep
the `import charts; charts.score_hist(...)` surface. Visual identity is
centralised in theme.py; builders here only assemble traces.
"""
from __future__ import annotations

from charts.overview import (  # noqa: F401
    avg_duration,
    daily_activity,
    hourly_heatmap,
    rejection_reasons,
)
from charts.players import (  # noqa: F401
    engagement_segments,
    new_vs_returning,
    retention_curve,
    retention_matrix,
    sessions_histogram,
)
from charts.gameplay import (  # noqa: F401
    coin_economy,
    duration_hist,
    powerup_efficacy,
    powerup_mix,
    powerups_per_run,
    score_hist,
    score_quantiles,
    skill_over_time,
)
