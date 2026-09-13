"""Smoke coverage the old dashboard never had: every chart builder must
survive an empty frame, and the whole app must run end-to-end on the
fixture without raising. Cheap insurance for the redesign."""
from __future__ import annotations

import os

import pandas as pd
import plotly.graph_objects as go
import pytest

import charts
import metrics


def _empty_plays() -> pd.DataFrame:
    return pd.DataFrame(columns=[
        "id", "device_id", "played_at", "score", "duration_s",
        "coins", "pillars", "near_misses", "powerups", "submit_error",
    ])


def test_every_chart_builder_handles_empty():
    empty_df = pd.DataFrame()
    empty_series = pd.Series([], dtype=float)
    grid = metrics.hourly_heatmap(_empty_plays())  # 7×24 zero grid

    figures = [
        charts.daily_activity(empty_df, empty_df),
        charts.rejection_reasons(empty_df),
        charts.avg_duration(empty_df),
        charts.hourly_heatmap(grid),
        charts.retention_curve(empty_df),
        charts.retention_matrix(empty_df),
        charts.new_vs_returning(empty_df),
        charts.sessions_histogram(empty_series),
        charts.engagement_segments(empty_df, days=30),
        charts.score_hist(empty_series),
        charts.duration_hist(empty_series),
        charts.score_quantiles(empty_df),
        charts.skill_over_time(empty_df),
        charts.powerup_mix(empty_df),
        charts.powerup_efficacy(empty_df),
        charts.coin_economy(empty_df),
        charts.powerups_per_run(empty_df),
    ]
    assert all(isinstance(f, go.Figure) for f in figures)


def test_app_runs_end_to_end_on_fixture():
    pytest.importorskip("streamlit.testing.v1")
    from streamlit.testing.v1 import AppTest

    os.environ["STREAMLIT_USE_FIXTURE"] = "1"
    app_path = os.path.join(os.path.dirname(__file__), os.pardir, "app.py")
    at = AppTest.from_file(app_path, default_timeout=60).run()

    assert at.exception is None or len(at.exception) == 0
    assert len(at.tabs) == 3
    # Five KPI cards on each of the three tabs.
    assert len(at.metric) == 15
    assert len(at.error) == 0
