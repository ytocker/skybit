"""Aggregation correctness — drive each function with a controlled
frame and assert against hand-computed expected values. Date columns
are pegged to `now` so tests are stable regardless of when run."""
from __future__ import annotations

import pandas as pd
import pytest

import metrics
from filters import plausible
from constants import MAX_PLAUSIBLE_SCORE, POWERUP_KEYS_ACTIVE


# ── Helpers ──────────────────────────────────────────────────────────────────

NOW = pd.Timestamp.now(tz="UTC")
TODAY = NOW.normalize()


def _row(*, id_, device_id, offset, score=50, duration_s=40, coins=10,
         pillars=5, near_misses=1, powerups=None) -> dict:
    """Build a synthetic play row. `offset` is a Timedelta from now."""
    return {
        "id":          id_,
        "device_id":   device_id,
        "played_at":   NOW - offset,
        "score":       score,
        "duration_s":  duration_s,
        "coins":       coins,
        "pillars":     pillars,
        "near_misses": near_misses,
        "powerups":    powerups or {k: 0 for k in POWERUP_KEYS_ACTIVE},
    }


def _empty_df() -> pd.DataFrame:
    return pd.DataFrame(columns=[
        "id", "device_id", "played_at", "score", "duration_s",
        "coins", "pillars", "near_misses", "powerups",
    ])


def _frame(rows: list[dict]) -> pd.DataFrame:
    """Construct a tz-aware frame in the same shape data.fetch_plays does."""
    df = pd.DataFrame(rows)
    df["played_at"] = pd.to_datetime(df["played_at"], utc=True)
    return df


# ── Filters ──────────────────────────────────────────────────────────────────


def test_plausible_drops_over_ceiling():
    df = _frame([
        _row(id_=1, device_id="a", offset=pd.Timedelta(hours=1), score=100),
        _row(id_=2, device_id="b", offset=pd.Timedelta(hours=1), score=MAX_PLAUSIBLE_SCORE + 1),
        _row(id_=3, device_id="c", offset=pd.Timedelta(hours=1), score=MAX_PLAUSIBLE_SCORE),
    ])
    out = plausible(df)
    assert set(out["id"]) == {1, 3}


def test_plausible_empty_in_empty_out():
    assert plausible(_empty_df()).empty


# ── Today KPIs ───────────────────────────────────────────────────────────────


def test_dau_today_counts_unique_devices_since_midnight():
    df = _frame([
        _row(id_=1, device_id="a", offset=pd.Timedelta(hours=1)),
        _row(id_=2, device_id="a", offset=pd.Timedelta(hours=2)),
        _row(id_=3, device_id="b", offset=pd.Timedelta(hours=3)),
        # Yesterday — must NOT count.
        _row(id_=4, device_id="c", offset=pd.Timedelta(days=1, hours=1)),
    ])
    # When tests run near 00:00 UTC the "yesterday" offset can land in
    # today's window. Re-derive expectation from played_at vs midnight.
    expected = df[df["played_at"] >= TODAY]["device_id"].nunique()
    assert metrics.dau_today(df) == expected


def test_plays_today_counts_rows_since_midnight():
    df = _frame([
        _row(id_=1, device_id="a", offset=pd.Timedelta(hours=1)),
        _row(id_=2, device_id="a", offset=pd.Timedelta(hours=2)),
        _row(id_=3, device_id="b", offset=pd.Timedelta(days=2)),
    ])
    expected = int((df["played_at"] >= TODAY).sum())
    assert metrics.plays_today(df) == expected


def test_today_kpis_on_empty():
    df = _empty_df()
    assert metrics.dau_today(df) == 0
    assert metrics.plays_today(df) == 0
    assert metrics.dau_yesterday(df) == 0
    assert metrics.plays_yesterday(df) == 0
    assert metrics.returning_rate_7d(df) == 0.0


# ── Time series ──────────────────────────────────────────────────────────────


def test_by_day_returns_continuous_index_even_when_empty():
    out = metrics.by_day(_empty_df(), days=14)
    assert len(out) == 14
    assert set(out.columns) == {"date", "plays", "uniques", "avg_duration_s"}
    assert (out["plays"] == 0).all()


def test_by_day_aggregates_correctly():
    df = _frame([
        _row(id_=1, device_id="a", offset=pd.Timedelta(hours=2), duration_s=30),
        _row(id_=2, device_id="a", offset=pd.Timedelta(hours=3), duration_s=50),
        _row(id_=3, device_id="b", offset=pd.Timedelta(hours=4), duration_s=70),
    ])
    out = metrics.by_day(df, days=7)
    today_row = out[out["date"] == TODAY]
    assert len(today_row) == 1
    assert int(today_row["plays"].iloc[0]) == 3
    assert int(today_row["uniques"].iloc[0]) == 2
    assert today_row["avg_duration_s"].iloc[0] == pytest.approx(50.0)


def test_hourly_heatmap_is_7x24():
    df = _frame([
        _row(id_=1, device_id="a", offset=pd.Timedelta(hours=2)),
    ])
    grid = metrics.hourly_heatmap(df)
    assert grid.shape == (7, 24)
    assert int(grid.values.sum()) == 1


def test_hourly_heatmap_empty():
    grid = metrics.hourly_heatmap(_empty_df())
    assert grid.shape == (7, 24)
    assert int(grid.values.sum()) == 0


# ── Power-ups ────────────────────────────────────────────────────────────────


def test_powerup_totals_excludes_reverse():
    df = _frame([
        _row(id_=1, device_id="a", offset=pd.Timedelta(hours=1),
             powerups={**{k: 1 for k in POWERUP_KEYS_ACTIVE}, "reverse": 5}),
    ])
    totals = metrics.powerup_totals(df, days=7)
    assert "reverse" not in totals["name"].values
    for k in POWERUP_KEYS_ACTIVE:
        assert int(totals[totals["name"] == k]["count"].iloc[0]) == 1


def test_powerup_totals_sums_across_rows():
    df = _frame([
        _row(id_=1, device_id="a", offset=pd.Timedelta(hours=1),
             powerups={"triple": 2, "magnet": 0, "slowmo": 0, "kfc": 0,
                       "ghost": 0, "grow": 0, "reverse": 0, "surprise": 0}),
        _row(id_=2, device_id="b", offset=pd.Timedelta(hours=2),
             powerups={"triple": 3, "magnet": 1, "slowmo": 0, "kfc": 0,
                       "ghost": 0, "grow": 0, "reverse": 0, "surprise": 0}),
    ])
    totals = metrics.powerup_totals(df, days=7)
    triple = int(totals[totals["name"] == "triple"]["count"].iloc[0])
    magnet = int(totals[totals["name"] == "magnet"]["count"].iloc[0])
    assert triple == 5
    assert magnet == 1


# ── Roster ───────────────────────────────────────────────────────────────────


def test_roster_includes_single_play_devices():
    """One-shot players used to be filtered out — that hid the most
    important churn signal for a casual game. They're now included."""
    df = _frame([
        _row(id_=1, device_id="loyal", offset=pd.Timedelta(hours=1)),
        _row(id_=2, device_id="loyal", offset=pd.Timedelta(hours=2)),
        _row(id_=3, device_id="oneshot", offset=pd.Timedelta(hours=3)),
    ])
    out = metrics.roster(df, days=30, top_n=50)
    assert set(out["device_id"]) == {"loyal", "oneshot"}
    # Loyal (2 plays) should sort above oneshot (1 play).
    assert list(out["device_id"]) == ["loyal", "oneshot"]


def test_roster_empty():
    out = metrics.roster(_empty_df(), days=30)
    assert out.empty


# ── One-shot players ─────────────────────────────────────────────────────────


def test_one_shot_count_counts_devices_with_exactly_one_play():
    df = _frame([
        _row(id_=1, device_id="loyal", offset=pd.Timedelta(hours=1)),
        _row(id_=2, device_id="loyal", offset=pd.Timedelta(hours=2)),
        _row(id_=3, device_id="oneshot_a", offset=pd.Timedelta(hours=3)),
        _row(id_=4, device_id="oneshot_b", offset=pd.Timedelta(days=2)),
    ])
    assert metrics.one_shot_count(df, days=7) == 2


def test_one_shot_count_respects_window():
    df = _frame([
        _row(id_=1, device_id="old", offset=pd.Timedelta(days=10)),
        _row(id_=2, device_id="recent", offset=pd.Timedelta(days=1)),
    ])
    assert metrics.one_shot_count(df, days=7) == 1


def test_one_shot_count_empty():
    assert metrics.one_shot_count(_empty_df(), days=7) == 0


# ── Engagement segments ──────────────────────────────────────────────────────


def test_engagement_segments_buckets_correctly():
    rows = []
    # 3 one-shot players
    for i, dev in enumerate(("a", "b", "c")):
        rows.append(_row(id_=i, device_id=dev, offset=pd.Timedelta(hours=1)))
    # 1 player with 3 plays (falls in 2-5 bucket)
    rows += [_row(id_=10 + i, device_id="d", offset=pd.Timedelta(hours=i + 1))
             for i in range(3)]
    # 1 player with 10 plays (falls in 6-20 bucket)
    rows += [_row(id_=20 + i, device_id="e", offset=pd.Timedelta(hours=i + 1))
             for i in range(10)]
    df = _frame(rows)
    seg = metrics.engagement_segments(df, days=30)
    counts = dict(zip(seg["segment"], seg["players"]))
    assert counts["1 play"] == 3
    assert counts["2–5 plays"] == 1
    assert counts["6–20 plays"] == 1
    assert counts["21+ plays"] == 0


def test_engagement_segments_empty_returns_zeroed_buckets():
    seg = metrics.engagement_segments(_empty_df(), days=30)
    assert list(seg["segment"]) == ["1 play", "2–5 plays", "6–20 plays", "21+ plays"]
    assert (seg["players"] == 0).all()
