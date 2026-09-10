"""
Shared helpers for the metric modules.

Kept tiny and dependency-light on purpose: the per-tab modules
(overview / players / gameplay) own their own aggregations; this is only
for the few primitives they all reach for (window cutoffs, day flooring)
so the cutoff arithmetic isn't re-implemented — and re-bugged — in a
dozen places.
"""
from __future__ import annotations

import pandas as pd


def window_cutoff(days: int) -> pd.Timestamp:
    """tz-aware UTC timestamp `days` ago. Use for rolling-window slices
    that include partial 'today'."""
    return pd.Timestamp.now(tz="UTC") - pd.Timedelta(days=days)


def day_floor_cutoff(days: int) -> pd.Timestamp:
    """UTC midnight `days` ago — for slices bucketed by calendar day so
    the boundary lands on a day edge rather than the current clock time."""
    return pd.Timestamp.now(tz="UTC").normalize() - pd.Timedelta(days=days)


def in_window(df: pd.DataFrame, days: int) -> pd.DataFrame:
    """Rows whose played_at falls in the last `days` days."""
    if df.empty:
        return df
    return df[df["played_at"] >= window_cutoff(days)]
