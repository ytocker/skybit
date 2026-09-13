"""
Gameplay & balance metrics — difficulty, skill, power-up balance, economy.

Answers the questions the old dashboard couldn't: how hard is the game
right now (score & survival distributions), is skill drifting over time,
and — the marquee addition — does each power-up actually help (efficacy),
not just how often it's picked. Pure pandas, stateless.
"""
from __future__ import annotations

import pandas as pd

from constants import POWERUP_KEYS_ACTIVE
from metrics.common import day_floor_cutoff, in_window

# Below this many picked-runs an efficacy bar is a coin-flip, not a
# balance signal — flagged so the chart can grey it out and the team
# doesn't re-tune a power-up off three noisy runs.
MIN_EFFICACY_N = 10


# ── Score & survival summaries ───────────────────────────────────────────────


def score_distribution(df: pd.DataFrame, days: int = 7) -> pd.Series:
    """Scores from the last `days` days for a histogram."""
    if df.empty:
        return pd.Series([], dtype=int)
    return in_window(df, days)["score"].astype(int)


def duration_distribution(df: pd.DataFrame, days: int = 7) -> pd.Series:
    """Survival times (seconds) from the last `days` days for a histogram.
    A spike near zero is the immediate-flame-out / rage-quit signal."""
    if df.empty:
        return pd.Series([], dtype=int)
    return in_window(df, days)["duration_s"].astype(int)


def _summary(series: pd.Series) -> dict[str, float]:
    if series.empty:
        return {"median": 0.0, "p90": 0.0, "max": 0.0}
    return {
        "median": float(series.median()),
        "p90": float(series.quantile(0.9)),
        "max": float(series.max()),
    }


def score_summary(df: pd.DataFrame, days: int = 7) -> dict[str, float]:
    """median / p90 / max score over the window for the KPI cards."""
    return _summary(score_distribution(df, days))


def duration_summary(df: pd.DataFrame, days: int = 7) -> dict[str, float]:
    """median / p90 / max survival seconds over the window."""
    return _summary(duration_distribution(df, days))


def coins_per_run(df: pd.DataFrame, days: int = 7) -> float:
    """Mean coins collected per run — the economy's top-line throughput."""
    if df.empty:
        return 0.0
    recent = in_window(df, days)
    if recent.empty:
        return 0.0
    return float(recent["coins"].mean())


def score_quantiles_by_day(df: pd.DataFrame, days: int = 30) -> pd.DataFrame:
    """Median / p90 score per UTC day, with the per-day run count `n` and a
    `low_n` flag. Empty days are dropped (the chart will simply not draw a
    point there).

    `low_n` marks days under MIN_EFFICACY_N runs: on a thin day a single
    near-ceiling run drags p90 into the tens of thousands and owns the log
    axis. The chart de-emphasises those days so a 6-run day's whale-driven
    p90 isn't read as a difficulty signal. (`max` is no longer returned —
    it was only ever a whale/cheater line, never a tuning read.)"""
    cols = ["date", "median", "p90", "n", "low_n"]
    if df.empty:
        return pd.DataFrame(columns=cols)
    sub = df.copy()
    sub["date"] = sub["played_at"].dt.floor("D")
    sub = sub[sub["date"] >= day_floor_cutoff(days)]
    if sub.empty:
        return pd.DataFrame(columns=cols)
    out = sub.groupby("date")["score"].agg(
        median="median",
        p90=lambda s: float(s.quantile(0.9)),
        n="size",
    ).reset_index()
    out["low_n"] = out["n"] < MIN_EFFICACY_N
    return out[cols]


def skill_proxy_by_day(df: pd.DataFrame, days: int = 30) -> pd.DataFrame:
    """Median score-per-second-alive + near-miss-rate-per-pillar by day.
    Filters out trivially-short runs (<2s) so a wave of immediate
    flame-outs doesn't dominate the curve.

    Pillars/sec was dropped: scroll speed is fixed-step, so pillars/sec is
    near-constant by design (a ±3% band a twin axis turns into a fake
    story). The two signals kept actually move with play:
      • `score_per_s` — points earned per second alive. Survival rate
        can't move with skill the way efficiency can; a player threading
        coin rushes scores faster per second even at equal survival.
      • `near_miss_rate` — near-misses per pillar passed, the half-real
        risk signal. Both render on a SINGLE axis (comparable units of
        per-second / per-pillar are not, so the chart leads with
        score-per-second and offers near-miss as a secondary line)."""
    cols = ["date", "score_per_s", "near_miss_rate"]
    if df.empty:
        return pd.DataFrame(columns=cols)
    sub = df[df["duration_s"] >= 2].copy()
    if sub.empty:
        return pd.DataFrame(columns=cols)
    sub["date"] = sub["played_at"].dt.floor("D")
    sub["sps"] = sub["score"] / sub["duration_s"].clip(lower=1)
    sub = sub[sub["date"] >= day_floor_cutoff(days)]
    if sub.empty:
        return pd.DataFrame(columns=cols)
    grouped = sub.groupby("date").apply(
        lambda g: pd.Series({
            "score_per_s": float(g["sps"].median()),
            "near_miss_rate": float(g["near_misses"].sum() / max(g["pillars"].sum(), 1)),
        }),
        include_groups=False,
    ).reset_index()
    return grouped[cols]


def coin_economy_by_day(df: pd.DataFrame, days: int = 30) -> pd.DataFrame:
    """Coins-per-pillar per UTC day — economy density, robust to how long
    runs last. A drift up/down flags a coin-spawn or rush-rate regression.
    Columns: [date, coins, pillars, coins_per_pillar]."""
    cols = ["date", "coins", "pillars", "coins_per_pillar"]
    if df.empty:
        return pd.DataFrame(columns=cols)
    sub = df.copy()
    sub["date"] = sub["played_at"].dt.floor("D")
    sub = sub[sub["date"] >= day_floor_cutoff(days)]
    if sub.empty:
        return pd.DataFrame(columns=cols)
    g = sub.groupby("date").agg(coins=("coins", "sum"), pillars=("pillars", "sum")).reset_index()
    g["coins_per_pillar"] = g["coins"] / g["pillars"].where(g["pillars"] > 0, 1)
    return g[cols]


# ── Power-ups ────────────────────────────────────────────────────────────────


def powerup_totals(df: pd.DataFrame, days: int = 7) -> pd.DataFrame:
    """Sum each active power-up key across the last `days` days. Returns
    a long frame (name, count) ready for a horizontal bar chart.

    Reverse is excluded because it's disabled in the game and would
    contribute zero noise. Surprise is included; it counts the pickup
    of a Surprise Box, not the rerolled outcome (the rerolled outcome
    increments its own key)."""
    if df.empty:
        return pd.DataFrame({"name": list(POWERUP_KEYS_ACTIVE),
                             "count": [0] * len(POWERUP_KEYS_ACTIVE)})
    sub = in_window(df, days)
    totals = {k: 0 for k in POWERUP_KEYS_ACTIVE}
    for entry in sub["powerups"]:
        if not isinstance(entry, dict):
            continue
        for k in POWERUP_KEYS_ACTIVE:
            totals[k] += int(entry.get(k, 0) or 0)
    return pd.DataFrame({"name": list(totals.keys()), "count": list(totals.values())})


def powerups_per_run_by_day(df: pd.DataFrame, days: int = 30) -> pd.DataFrame:
    """Avg total power-ups picked per run, per day. Useful for spotting
    spawn-rate regressions."""
    if df.empty:
        return pd.DataFrame(columns=["date", "per_run"])
    sub = df.copy()
    sub["total_pu"] = sub["powerups"].apply(_total_powerups)
    sub["date"] = sub["played_at"].dt.floor("D")
    sub = sub[sub["date"] >= day_floor_cutoff(days)]
    if sub.empty:
        return pd.DataFrame(columns=["date", "per_run"])
    out = sub.groupby("date")["total_pu"].mean().reset_index().rename(
        columns={"total_pu": "per_run"}
    )
    return out


def powerup_efficacy(df: pd.DataFrame, days: int = 30) -> pd.DataFrame:
    """For each active power-up, compare runs that picked it ≥1× against
    runs that didn't, on median score and median survival. `lift` is the
    percentage difference (with vs without).

    Correlational, not causal — a power-up may be picked *because* a run
    is already going well (longer runs see more spawns). The chart says
    so. Still the fastest read on whether a power-up is pulling its
    weight or is dead weight / overpowered.

    To partly net out the confound we also report `excess_lift_pct` =
    score_lift_pct − dur_lift_pct: how much the score lift *exceeds* what
    the longer survival alone would explain. Positive excess is the
    closest honest read to "this power-up adds value per second alive";
    near-zero excess means the score bump is just more time on screen.
    Still not causal — read it as a flag, not a verdict.

    `low_n` marks power-ups whose picked-group is below MIN_EFFICACY_N
    so the chart can de-emphasise noisy small-sample bars.

    Columns: [powerup, n_with, n_without, score_with, score_without,
    score_lift_pct, dur_with, dur_without, dur_lift_pct, excess_lift_pct,
    low_n]. Power-ups never picked in the window are omitted (no signal)."""
    cols = ["powerup", "n_with", "n_without",
            "score_with", "score_without", "score_lift_pct",
            "dur_with", "dur_without", "dur_lift_pct",
            "excess_lift_pct", "low_n"]
    if df.empty:
        return pd.DataFrame(columns=cols)
    sub = in_window(df, days).copy()
    if sub.empty:
        return pd.DataFrame(columns=cols)
    rows = []
    for k in POWERUP_KEYS_ACTIVE:
        picked = sub["powerups"].apply(
            lambda d, key=k: isinstance(d, dict) and int(d.get(key, 0) or 0) > 0
        )
        n_with = int(picked.sum())
        n_without = int((~picked).sum())
        if n_with == 0:
            continue  # never picked in window → nothing to compare
        with_grp = sub[picked]
        without_grp = sub[~picked]
        score_with = float(with_grp["score"].median())
        dur_with = float(with_grp["duration_s"].median())
        score_without = float(without_grp["score"].median()) if n_without else float("nan")
        dur_without = float(without_grp["duration_s"].median()) if n_without else float("nan")
        score_lift = _lift(score_with, score_without)
        dur_lift = _lift(dur_with, dur_without)
        rows.append({
            "powerup": k,
            "n_with": n_with,
            "n_without": n_without,
            "score_with": score_with,
            "score_without": score_without,
            "score_lift_pct": score_lift,
            "dur_with": dur_with,
            "dur_without": dur_without,
            "dur_lift_pct": dur_lift,
            "excess_lift_pct": score_lift - dur_lift,
            "low_n": n_with < MIN_EFFICACY_N,
        })
    return pd.DataFrame(rows, columns=cols)


def score_vs_survival(df: pd.DataFrame, powerup: str = "magnet",
                      days: int = 30) -> pd.DataFrame:
    """One row per run: survival seconds, score, and whether the run picked
    `powerup` at least once. The raw difficulty-shape view the histograms
    can't give — and the picture the efficacy chart only *summarises*: you
    see directly that picked-runs cluster up-and-right (longer AND
    higher-scoring), i.e. the exposure confound, rather than taking the
    excess-lift number on faith.

    Columns: [duration_s, score, picked]. Empty/zero-duration runs are
    kept (a flame-out at t≈0 is itself a difficulty signal); the chart
    clips the score axis, not the row set."""
    cols = ["duration_s", "score", "picked"]
    if df.empty:
        return pd.DataFrame(columns=cols)
    sub = in_window(df, days).copy()
    if sub.empty:
        return pd.DataFrame(columns=cols)
    sub["picked"] = sub["powerups"].apply(
        lambda d, key=powerup: isinstance(d, dict) and int(d.get(key, 0) or 0) > 0
    )
    out = sub[["duration_s", "score", "picked"]].copy()
    out["duration_s"] = out["duration_s"].astype(float)
    out["score"] = out["score"].astype(float)
    return out.reset_index(drop=True)


# ── Helpers ──────────────────────────────────────────────────────────────────


def _total_powerups(d) -> int:
    if not isinstance(d, dict):
        return 0
    return sum(int(d.get(k, 0) or 0) for k in POWERUP_KEYS_ACTIVE)


def _lift(with_val: float, without_val: float) -> float:
    """Percentage lift of `with` over `without`, guarding the zero/NaN
    baseline (returns 0.0 — undefined lift reads as 'no signal')."""
    if without_val is None or pd.isna(without_val) or without_val == 0:
        return 0.0
    return (with_val - without_val) / without_val * 100.0
