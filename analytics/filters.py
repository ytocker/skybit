"""
Row filters applied before any aggregation.

The dashboard mirrors the in-game leaderboard's plausibility ceiling —
anything above MAX_PLAUSIBLE_SCORE is dropped silently. User chose
"always hidden", no toggle, so this is unconditional.

Date filtering lives here too so the sidebar widget has one place to
call.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pandas as pd

from constants import MAX_PLAUSIBLE_SCORE


def plausible(df: pd.DataFrame) -> pd.DataFrame:
    """Drop rows that fail the score ceiling. Empty frame -> empty frame
    (no copy, no error). Operates on a copy so callers can hold a
    reference to the unfiltered raw pull."""
    if df.empty:
        return df
    return df[df["score"] <= MAX_PLAUSIBLE_SCORE].copy()


def within_days(df: pd.DataFrame, days: int) -> pd.DataFrame:
    """Last N days of plays, inclusive of "today" in UTC. df is expected
    to have a tz-aware played_at column (Supabase returns timestamptz)."""
    if df.empty:
        return df
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    return df[df["played_at"] >= cutoff].copy()


def today_utc_start() -> datetime:
    """Midnight UTC of the current day. Used for 'today' KPI buckets."""
    now = datetime.now(timezone.utc)
    return datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
