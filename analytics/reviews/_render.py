"""Render representative dashboard charts from the fixture to PNGs for
the analytics-director review. Dark background baked in (the live charts
are transparent over the Streamlit dark theme)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import data  # noqa: E402
import charts  # noqa: E402
import metrics  # noqa: E402
from filters import plausible  # noqa: E402

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "reviews" / "v5-redesign" / "round_1"
OUT.mkdir(parents=True, exist_ok=True)

df = plausible(data._rebase_to_now(
    data._normalise_plays(json.load(open(ROOT / "tests/fixtures/plays_sample.json")))))

W = 30


def save(fig, name, w=760, h=360):
    fig.update_layout(paper_bgcolor="#0F1B2D", plot_bgcolor="#0F1B2D",
                      font=dict(color="#E8EEF7"))
    fig.write_image(str(OUT / name), width=w, height=h, scale=2)
    print("wrote", name)


# Overview
save(charts.plays_and_uniques(metrics.by_day(df, days=W), days=W), "ov_plays_uniques.png")
save(charts.plays_anomaly_band(metrics.daily_plays_with_band(df, days=W), days=W), "ov_anomaly.png")
save(charts.rejection_reasons(metrics.rejection_reasons(df, days=90), days=90), "ov_rejections.png")
save(charts.hourly_heatmap(metrics.hourly_heatmap(df)), "ov_heatmap.png")
# Players
save(charts.retention_curve(metrics.retention_curve(df, max_day=7)), "pl_retention_curve.png")
save(charts.retention_matrix(metrics.retention_matrix(df, max_day=7)), "pl_retention_matrix.png")
save(charts.new_vs_returning(metrics.new_vs_returning_by_day(df, days=W), days=W), "pl_new_vs_returning.png")
save(charts.sessions_histogram(metrics.sessions_per_active_day(df, days=W), days=W), "pl_sessions.png")
save(charts.engagement_segments(metrics.engagement_segments(df, days=W), days=W), "pl_segments.png")
# Gameplay
save(charts.score_hist(metrics.score_distribution(df, days=90)), "gp_score_hist.png")
save(charts.duration_hist(metrics.duration_distribution(df, days=90)), "gp_duration_hist.png")
save(charts.skill_over_time(metrics.skill_proxy_by_day(df, days=W)), "gp_skill.png")
save(charts.powerup_efficacy(metrics.powerup_efficacy(df, days=90)), "gp_efficacy.png")
save(charts.coin_economy(metrics.coin_economy_by_day(df, days=W)), "gp_coin_economy.png")
print("done →", OUT)
