"""Overview / live-ops metrics — driven by NOW-relative frames so the
assertions are stable whenever the suite runs."""
from __future__ import annotations

import pandas as pd

import metrics
from metrics import overview as ov  # new metrics not re-exported in __init__
from constants import POWERUP_KEYS_ACTIVE

NOW = pd.Timestamp.now(tz="UTC")


def _row(*, id_, device_id, offset, score=50, duration_s=40, coins=10,
         pillars=5, near_misses=1, powerups=None, submit_error=None) -> dict:
    return {
        "id": id_, "device_id": device_id, "played_at": NOW - offset,
        "score": score, "duration_s": duration_s, "coins": coins,
        "pillars": pillars, "near_misses": near_misses,
        "powerups": powerups or {k: 0 for k in POWERUP_KEYS_ACTIVE},
        "submit_error": submit_error,
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


def test_plays_window_delta_splits_current_and_prior():
    rows = [
        _row(id_=1, device_id="a", offset=pd.Timedelta(days=1)),   # current 7d
        _row(id_=2, device_id="b", offset=pd.Timedelta(days=3)),   # current 7d
        _row(id_=3, device_id="c", offset=pd.Timedelta(days=9)),   # prior 7d
        _row(id_=4, device_id="d", offset=pd.Timedelta(days=20)),  # neither
    ]
    cur, prev = metrics.plays_window_delta(_frame(rows), days=7)
    assert cur == 2
    assert prev == 1


def test_plays_window_delta_empty():
    assert metrics.plays_window_delta(_empty(), days=7) == (0, 0)


def test_minutes_since_last_play_none_on_empty():
    assert metrics.minutes_since_last_play(_empty()) is None


def test_minutes_since_last_play_recent():
    df = _frame([_row(id_=1, device_id="a", offset=pd.Timedelta(minutes=30))])
    m = metrics.minutes_since_last_play(df)
    assert 25 <= m <= 35


def test_rejection_rate_counts_non_null_submit_error():
    rows = [
        _row(id_=1, device_id="a", offset=pd.Timedelta(hours=1)),
        _row(id_=2, device_id="b", offset=pd.Timedelta(hours=2), submit_error="chain: x"),
        _row(id_=3, device_id="c", offset=pd.Timedelta(hours=3), submit_error="score: y"),
        _row(id_=4, device_id="d", offset=pd.Timedelta(hours=4)),
    ]
    assert metrics.rejection_rate(_frame(rows), days=7) == 0.5


def test_rejection_rate_graceful_without_column():
    df = _frame([_row(id_=1, device_id="a", offset=pd.Timedelta(hours=1))]).drop(
        columns=["submit_error"])
    assert metrics.rejection_rate(df, days=7) == 0.0


def test_rejection_rate_empty():
    assert metrics.rejection_rate(_empty(), days=7) == 0.0


def test_rejection_reasons_groups_by_gate_name():
    rows = [
        _row(id_=1, device_id="a", offset=pd.Timedelta(hours=1),
             submit_error="score: exceeds MAX_PLAUSIBLE_SCORE"),
        _row(id_=2, device_id="b", offset=pd.Timedelta(hours=2),
             submit_error="score: something else"),
        _row(id_=3, device_id="c", offset=pd.Timedelta(hours=3),
             submit_error="chain: hash mismatch"),
        _row(id_=4, device_id="d", offset=pd.Timedelta(hours=4)),
    ]
    out = metrics.rejection_reasons(_frame(rows), days=7)
    counts = dict(zip(out["reason"], out["count"]))
    assert counts["score"] == 2
    assert counts["chain"] == 1


def test_rejection_reasons_empty_when_no_rejections():
    rows = [_row(id_=1, device_id="a", offset=pd.Timedelta(hours=1))]
    assert metrics.rejection_reasons(_frame(rows), days=7).empty


def _flat_then_last(per_day: int, last_count: int, span: int = 30):
    """Build a frame: `per_day` plays on each of the prior `span-1` days,
    then `last_count` plays today — one bucket per calendar day so the
    trailing Poisson band has a settled λ to judge today against."""
    rows = []
    rid = 0
    for day in range(1, span):
        for _ in range(per_day):
            rid += 1
            rows.append(_row(id_=rid, device_id="a",
                             offset=pd.Timedelta(days=day, hours=1)))
    for _ in range(last_count):
        rid += 1
        rows.append(_row(id_=rid, device_id="a", offset=pd.Timedelta(hours=1)))
    return _frame(rows)


def test_daily_plays_with_band_has_bounds_and_length():
    rows = [_row(id_=i, device_id="a", offset=pd.Timedelta(days=i % 10))
            for i in range(30)]
    band = metrics.daily_plays_with_band(_frame(rows), days=30)
    assert len(band) == 30
    assert set(band.columns) == {
        "date", "plays", "mean", "lo", "hi", "warmup", "outlier"}
    # Where the band exists (not warm-up) it is ordered and non-negative.
    settled = band[~band["warmup"]]
    assert (settled["lo"] <= settled["hi"]).all()
    assert (settled["lo"] >= 0).all()
    # The Poisson lo edge never runs negative even at low λ — the failure
    # the ±2σ Gaussian band hit and had to .clip().
    assert (band["lo"].dropna() >= 0).all()


def test_daily_plays_with_band_warmup_is_14_days():
    """The first 14 days of any window are warm-up (14d trailing λ): no
    band, flagged, and never marked an outlier (no history to judge)."""
    rows = [_row(id_=i, device_id="a", offset=pd.Timedelta(days=i % 10))
            for i in range(40)]
    band = metrics.daily_plays_with_band(_frame(rows), days=30)
    warm = band[band["warmup"]]
    assert len(warm) == 14
    assert warm["mean"].isna().all()
    assert warm["lo"].isna().all() and warm["hi"].isna().all()
    assert not warm["outlier"].any()


def test_daily_plays_with_band_flags_a_spike():
    """A clear volume spike after a flat run lands above the trailing
    Poisson band and is flagged outlier — the spike side of the alert."""
    band = metrics.daily_plays_with_band(_flat_then_last(2, 50), days=30)
    last = band.iloc[-1]
    assert last["plays"] >= 50
    assert not bool(last["warmup"])
    assert bool(last["outlier"]) is True


def test_daily_plays_with_band_flags_a_drop():
    """A sudden DROP to zero after a steady run lands below the Poisson
    band and is flagged outlier — the live-ops alert that matters most
    (an outage shows as a collapse, not a spike). With λ≈12, a day of 0
    is z = (0−12)/√12 ≈ −3.5, well past the −2 threshold."""
    band = metrics.daily_plays_with_band(_flat_then_last(12, 0), days=30)
    last = band.iloc[-1]
    assert last["plays"] == 0
    assert not bool(last["warmup"])
    assert last["mean"] > 5          # λ was healthy before the drop
    assert bool(last["outlier"]) is True


def test_daily_plays_with_band_steady_run_is_not_flagged():
    """A flat run within Poisson noise of λ must NOT flag — guards
    against the old σ-breathing band crying wolf on normal variation."""
    band = metrics.daily_plays_with_band(_flat_then_last(10, 11), days=30)
    last = band.iloc[-1]
    assert not bool(last["outlier"])


def test_rejection_count_returns_numerator_and_denominator():
    rows = [
        _row(id_=1, device_id="a", offset=pd.Timedelta(hours=1)),
        _row(id_=2, device_id="b", offset=pd.Timedelta(hours=2),
             submit_error="chain: x"),
        _row(id_=3, device_id="c", offset=pd.Timedelta(hours=3)),
        _row(id_=4, device_id="d", offset=pd.Timedelta(days=30)),  # out of 7d
    ]
    assert ov.rejection_count(_frame(rows), days=7) == (1, 3)


def test_rejection_count_empty():
    assert ov.rejection_count(_empty(), days=7) == (0, 0)


def test_health_status_empty_is_alert():
    h = ov.health_status(_empty())
    assert h["level"] == "ALERT"
    assert h["alive"]["level"] == "ALERT"


def test_health_status_keys_and_shape():
    rows = [_row(id_=i, device_id=f"d{i%5}",
                 offset=pd.Timedelta(hours=i)) for i in range(20)]
    h = ov.health_status(_frame(rows))
    assert h["level"] in {"OK", "WATCH", "ALERT"}
    assert set(h) >= {"level", "reasons", "alive", "growing", "clean"}
    assert isinstance(h["reasons"], list) and h["reasons"]


def test_health_status_clean_when_fresh_and_no_rejects():
    """A steady recent stream with no rejected submits reads OK."""
    rows = [_row(id_=i, device_id=f"d{i%4}",
                 offset=pd.Timedelta(hours=i)) for i in range(24)]
    h = ov.health_status(_frame(rows))
    assert h["alive"]["level"] == "OK"
    assert h["clean"]["level"] == "OK"


def test_health_status_single_reject_does_not_alert_clean():
    """One rejected run in a small window must not escalate 'clean' to
    ALERT — the absolute-count gate guards against small-N noise."""
    rows = [_row(id_=i, device_id="a", offset=pd.Timedelta(hours=i))
            for i in range(10)]
    rows.append(_row(id_=99, device_id="a", offset=pd.Timedelta(hours=1),
                     submit_error="score: huge"))
    h = ov.health_status(_frame(rows))
    assert h["clean"]["level"] == "OK"


def test_health_status_many_rejects_alerts_clean():
    """A high rejection rate over enough runs escalates 'clean' to ALERT."""
    rows = [_row(id_=i, device_id="a", offset=pd.Timedelta(hours=i),
                 submit_error="chain: mismatch") for i in range(5)]
    rows += [_row(id_=100 + i, device_id="a", offset=pd.Timedelta(hours=i))
             for i in range(3)]
    h = ov.health_status(_frame(rows))
    assert h["clean"]["level"] == "ALERT"
    assert h["level"] == "ALERT"
