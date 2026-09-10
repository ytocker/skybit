"""Players & retention metrics — the highest-risk new code. Cohorts are
built at controlled day-offsets from TODAY so D1/D7 have known answers."""
from __future__ import annotations

import pandas as pd

from metrics import players as m
from constants import POWERUP_KEYS_ACTIVE

NOW = pd.Timestamp.now(tz="UTC")
TODAY = NOW.normalize()


def _row(*, id_, device_id, days_ago, score=50) -> dict:
    # Pin to mid-day so day-flooring is unambiguous regardless of run time.
    played = TODAY - pd.Timedelta(days=days_ago) + pd.Timedelta(hours=12)
    return {
        "id": id_, "device_id": device_id, "played_at": played,
        "score": score, "duration_s": 40, "coins": 10, "pillars": 5,
        "near_misses": 1, "powerups": {k: 0 for k in POWERUP_KEYS_ACTIVE},
        "submit_error": None,
    }


def _frame(rows: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    df["played_at"] = pd.to_datetime(df["played_at"], utc=True)
    return df


def _empty() -> pd.DataFrame:
    return pd.DataFrame(columns=[
        "id", "device_id", "played_at", "score", "duration_s",
        "coins", "pillars", "near_misses", "powerups", "submit_error",
    ])


# One cohort installed 10 days ago:
#   A: plays day-10 (offset0), day-9 (offset1), day-3 (offset7)
#   B: plays day-10, day-9 (offset1)
#   C: plays day-10 only (one-shot)
# Plus D: installs today (for new_players_today).
def _cohort_frame() -> pd.DataFrame:
    return _frame([
        _row(id_=1, device_id="A", days_ago=10),
        _row(id_=2, device_id="A", days_ago=9),
        _row(id_=3, device_id="A", days_ago=3),
        _row(id_=4, device_id="B", days_ago=10),
        _row(id_=5, device_id="B", days_ago=9),
        _row(id_=6, device_id="C", days_ago=10),
        _row(id_=7, device_id="D", days_ago=0),
    ])


def test_cohort_retention_known_fractions():
    cr = m.cohort_retention(_cohort_frame(), max_day=7)
    cohort = TODAY - pd.Timedelta(days=10)
    sub = cr[cr["cohort_date"] == cohort].set_index("day_offset")
    assert int(sub.loc[0, "cohort_size"]) == 3
    assert int(sub.loc[0, "retained"]) == 3      # all 3 played install day
    assert int(sub.loc[1, "retained"]) == 2      # A, B
    assert int(sub.loc[7, "retained"]) == 1      # A only
    assert sub.loc[1, "retained_frac"] == 2 / 3


def test_retention_curve_summary_is_exact_with_ci():
    # Summary now uses the EXACT (classic Dn) curve so the cards are
    # benchmark-comparable and equal the default curve's points.
    #   D1 = devices active on EXACTLY offset 1 = {A, B} = 2/3
    #   D7 = devices active on EXACTLY offset 7 = {A}    = 1/3
    # (On this frame those happen to equal the unbounded values because
    # A is active precisely at offsets 1 and 7.) The settled n is 3 and
    # each Dn carries its Wilson 95% bounds, bracketing the point estimate.
    summ = m.retention_summary(_cohort_frame())
    assert summ["d1"] == 2 / 3
    assert summ["d7"] == 1 / 3
    assert summ["n"] == 3
    assert summ["d1_lo"] < summ["d1"] < summ["d1_hi"]
    assert summ["d7_lo"] < summ["d7"] < summ["d7_hi"]
    # Bounds match the Wilson helper on (retained, n).
    assert (summ["d1_lo"], summ["d1_hi"]) == m.wilson_interval(2, 3)
    assert (summ["d7_lo"], summ["d7_hi"]) == m.wilson_interval(1, 3)


def test_wilson_interval_bounds_and_degenerate():
    # Stays inside [0,1] at the 0% and 100% extremes, and is empty at n=0.
    lo, hi = m.wilson_interval(0, 5)
    assert lo == 0.0 and 0.0 < hi < 1.0
    lo, hi = m.wilson_interval(5, 5)
    assert 0.0 < lo < 1.0 and hi == 1.0
    assert m.wilson_interval(0, 0) == (0.0, 0.0)


def test_unbounded_dominates_exact():
    # Definitional inequality: active-on-day-n ⊆ active-by-day-≥-n, so
    # unbounded(offset) ≥ exact(offset) at EVERY offset. This is exactly
    # why the two flavours are not interchangeable and must never share a
    # KPI card. Asserted on the cohort frame, which has the A skip-return
    # that drives a strict gap at offsets 2..6.
    df = _cohort_frame()
    ex = m.retention_curve(df, max_day=7, mode="exact").set_index("day_offset")
    un = m.retention_curve(df, max_day=7, mode="unbounded").set_index("day_offset")
    for off in range(0, 8):
        assert un.loc[off, "retained"] >= ex.loc[off, "retained"], off
        assert un.loc[off, "retained_frac"] >= ex.loc[off, "retained_frac"]
    # And the gap is strict somewhere (offsets 2..6: A is alive unbounded,
    # absent exact), proving they genuinely differ.
    assert any(un.loc[o, "retained"] > ex.loc[o, "retained"] for o in range(2, 7))


def test_retention_curve_unbounded_is_monotone():
    # A is active at offsets {0,1,7} — it skips offsets 2..6. Exact-day
    # retention therefore dips to 0 at D2..D6 then springs back to 1 at D7
    # (non-monotone). Unbounded keeps A alive the whole way (max offset 7),
    # so the curve is monotone non-increasing and never bumps back up.
    df = _cohort_frame()
    exact = m.retention_curve(df, max_day=7, mode="exact")
    unb = m.retention_curve(df, max_day=7, mode="unbounded")

    ex = exact.set_index("day_offset")["retained"]
    assert ex.loc[1] == 2 and ex.loc[2] == 0 and ex.loc[7] == 1  # the bump

    fr = unb["retained_frac"].tolist()
    assert fr == sorted(fr, reverse=True)          # monotone non-increasing
    un = unb.set_index("day_offset")["retained"]
    assert un.loc[0] == 3                          # D0 must be 100%
    assert un.loc[1] == 2                           # A, B reach ≥1
    assert un.loc[3] == 1 and un.loc[6] == 1        # only A survives the gap
    assert un.loc[7] == 1


def test_retention_curve_d0_is_full_population():
    for mode in ("unbounded", "exact"):
        curve = m.retention_curve(_cohort_frame(), max_day=7, mode=mode)
        d0 = curve[curve["day_offset"] == 0].iloc[0]
        assert d0["retained_frac"] == 1.0
        assert int(d0["retained"]) == int(d0["cohort_devices"]) == 3


def test_retention_curve_rejects_bad_mode():
    import pytest
    with pytest.raises(ValueError):
        m.retention_curve(_cohort_frame(), max_day=7, mode="rolling-7")


def test_settled_cohort_size_excludes_unsettled():
    # A/B/C install 10d ago (settled at max_day=7); D installs today
    # (unsettled). So n=3.
    assert m.settled_cohort_size(_cohort_frame(), max_day=7) == 3
    assert m.settled_cohort_size(_empty(), max_day=7) == 0


def test_cohort_censors_future_offsets():
    # Cohort installed 2 days ago: offsets 3..7 are in the future → omitted.
    df = _frame([
        _row(id_=1, device_id="X", days_ago=2),
        _row(id_=2, device_id="X", days_ago=1),
    ])
    cr = m.cohort_retention(df, max_day=7)
    offsets = set(cr["day_offset"])
    assert offsets == {0, 1, 2}


def test_retention_matrix_shape_and_blank_cells():
    mat = m.retention_matrix(_cohort_frame(), max_day=7)
    assert list(mat.columns) == list(range(8))
    # The n=3 cohort (A, B, C, installed 10d ago) survives the n≥3
    # suppression; today's single-device cohort (D, n=1) is dropped.
    cohort = TODAY - pd.Timedelta(days=10)
    assert cohort in mat.index
    assert TODAY not in mat.index
    # Within the kept cohort, offset 0 is fully observed (all 3 played
    # install day) and offsets 4..6 had no activity → exact-day 0%, not NaN.
    assert mat.loc[cohort, 0] == 1.0
    assert mat.loc[cohort, 1] == 2 / 3
    # Offsets beyond the observed span of this cohort (it's only 10d old,
    # so all of D0..D7 are settled) are real values, not censored here.
    assert not pd.isna(mat.loc[cohort, 7])


def test_retention_matrix_suppresses_small_cohorts():
    # A frame of only single-device cohorts → nothing clears n≥3, so the
    # triangle is empty rather than 25 rows of one-returner coin-flips.
    df = _frame([
        _row(id_=1, device_id="P", days_ago=20),
        _row(id_=2, device_id="Q", days_ago=18),
        _row(id_=3, device_id="R", days_ago=15),
    ])
    assert m.retention_matrix(df, max_day=7).empty
    # Lowering the threshold lets them back in (the knob works).
    assert not m.retention_matrix(df, max_day=7, min_cohort=1).empty


def test_new_players_today():
    assert m.new_players_today(_cohort_frame()) == 1


def test_new_vs_returning_split():
    nvr = m.new_vs_returning_by_day(_cohort_frame(), days=30).set_index("date")
    d10 = TODAY - pd.Timedelta(days=10)
    d9 = TODAY - pd.Timedelta(days=9)
    assert int(nvr.loc[d10, "new"]) == 3        # A, B, C first seen
    assert int(nvr.loc[d10, "returning"]) == 0
    assert int(nvr.loc[d9, "new"]) == 0
    assert int(nvr.loc[d9, "returning"]) == 2   # A, B back


def test_sessions_per_active_day_counts_plays():
    # A has 2 plays on the same day, B has 1.
    df = _frame([
        _row(id_=1, device_id="A", days_ago=1),
        _row(id_=2, device_id="A", days_ago=1),
        _row(id_=3, device_id="B", days_ago=1),
    ])
    s = m.sessions_per_active_day(df, days=7)
    assert sorted(s.tolist()) == [1, 2]


def test_retention_on_empty():
    assert m.retention_curve(_empty()).empty
    assert m.retention_matrix(_empty()).empty
    assert m.cohort_retention(_empty()).empty
    summ = m.retention_summary(_empty())
    assert summ["d1"] == 0.0 and summ["d7"] == 0.0 and summ["n"] == 0
    assert summ["d1_lo"] == 0.0 and summ["d7_hi"] == 0.0
    assert m.new_players_today(_empty()) == 0
