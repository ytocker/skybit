"""
Player & retention metrics.

The retention story the old dashboard never told: cohort curves, a
retention triangle, and a new-vs-returning split — plus the engagement
segments and roster it already had. Pure pandas, stateless.

Retention definitions (held constant so tests have known answers):
  • install day  = a device's FIRST played_at UTC date *within the
    fetched frame*. The app feeds a wide (~120d) frame here so the
    install day is real for cohorts at least `max_day` days old.
  • Dn retained  = two flavours, both supported:
      - EXACT (default, "classic Dn"): the device was active on precisely
        install+n. This is the textbook same-day-n definition every
        hyper-casual benchmark (D1 25–35%, D7 6–12%) is quoted against,
        so it is the ONLY basis that may sit next to those benchmarks.
        It drives the KPI cards AND the default curve. Bumpy on small N
        (a player who skips a week then returns on D7 lifts that single
        point) — banded with a Wilson CI so the eye reads the noise.
      - UNBOUNDED ("rolling": active by day ≥ n): the device was active
        on install+n OR ANY later day. Monotone non-increasing by
        construction, so D7 ≤ D1 always holds — but it OVERSTATES classic
        Dn and is NOT comparable to the benchmarks. Shown only as a
        clearly-labelled secondary line on the curve, never on a card.
  • censoring    = a (cohort, offset) is only counted once enough wall
    time has passed (install + offset ≤ today); younger cells are
    omitted rather than counted as 0, so a fresh cohort doesn't drag
    the curve down.

The definitional inequality unbounded(n) ≥ exact(n) holds at every
offset (active-on-day-n implies active-by-day-≥-n), which is exactly why
the two are not interchangeable and must never share a card. Pinned by
test_unbounded_dominates_exact.

Windowed-telemetry caveat: a device whose true first play predates the
frame looks "new" the day it re-enters. Exact fix needs a server-side
first_seen; out of scope. Surfaced in chart subtitles AND on the cards.

Small-N honesty: cohort sizes are tiny here (most are 1–2 devices), so a
single returning player swings a per-cohort cell by 50–100%. The settled
denominator (N) is carried on every curve row, the exact curve is banded
with a Wilson CI, and the triangle suppresses cohorts below n≥3 so the
visible cells aren't n=1 noise.
"""
from __future__ import annotations

import math

import pandas as pd

# Below this cohort size a per-cohort retention row is one or two devices —
# a single returner swings it 50–100%. The triangle suppresses smaller
# cohorts so the heatmap shows signal, not sampling jitter.
MIN_COHORT_SIZE = 3

from metrics.common import day_floor_cutoff, in_window, window_cutoff


# ── Shared internals ─────────────────────────────────────────────────────────


def _first_seen(df: pd.DataFrame) -> pd.Series:
    """device_id -> first observed UTC day (floored)."""
    return df.groupby("device_id")["played_at"].min().dt.floor("D")


def _active_device_days(df: pd.DataFrame) -> pd.DataFrame:
    """Distinct (device_id, day) pairs — one row per day a device was active."""
    sub = df[["device_id"]].copy()
    sub["day"] = df["played_at"].dt.floor("D")
    return sub.drop_duplicates()


# ── Headline scalars ─────────────────────────────────────────────────────────


def returning_rate_7d(df: pd.DataFrame) -> float:
    """Fraction of last-7d players with plays on >=2 distinct UTC days.
    Returns 0.0 if there are no players in the window so the metric
    card shows 0% rather than NaN."""
    if df.empty:
        return 0.0
    recent = df[df["played_at"] >= window_cutoff(7)]
    if recent.empty:
        return 0.0
    days_per_player = (
        recent.assign(d=recent["played_at"].dt.date)
              .groupby("device_id")["d"].nunique()
    )
    total = len(days_per_player)
    repeated = int((days_per_player >= 2).sum())
    return repeated / total if total else 0.0


def one_shot_count(df: pd.DataFrame, days: int = 7) -> int:
    """Number of devices in the window with exactly one play. The "bounce"
    signal for a casual game — high values mean the first-run experience
    isn't converting curious clicks into a second attempt. Hyper-casual
    benchmarks expect 60–75% of players to be one-shots."""
    if df.empty:
        return 0
    recent = in_window(df, days)
    if recent.empty:
        return 0
    plays_per_device = recent.groupby("device_id").size()
    return int((plays_per_device == 1).sum())


def active_players(df: pd.DataFrame, days: int = 7) -> int:
    """Distinct devices active in the window — the denominator for the
    one-shot/bounce percentage card."""
    if df.empty:
        return 0
    recent = in_window(df, days)
    return int(recent["device_id"].nunique())


def new_players_today(df: pd.DataFrame) -> int:
    """Devices whose first observed play (within the frame) is today.
    Subject to the windowed-telemetry caveat above."""
    if df.empty:
        return 0
    today = pd.Timestamp.now(tz="UTC").normalize()
    return int((_first_seen(df) == today).sum())


def wilson_interval(retained: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """95% Wilson score interval for a binomial proportion retained/n.
    Chosen over the normal approximation because it behaves at the tiny n
    and the 0%/100% extremes this tab lives at (it never runs past [0,1]
    and isn't degenerate when retained is 0 or n). Returns (lo, hi) as
    fractions; (0.0, 0.0) when n == 0."""
    if n <= 0:
        return 0.0, 0.0
    p = retained / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = (z / denom) * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return max(0.0, centre - half), min(1.0, centre + half)


def retention_summary(df: pd.DataFrame) -> dict[str, float]:
    """The two headline retention KPIs, pooled across the settled cohort.
    Uses the EXACT (classic Dn) curve — the same basis the hyper-casual
    benchmarks (D1 25–35%, D7 6–12%) are quoted against, so the cards are
    benchmark-comparable and equal the default curve's points. Each Dn
    carries its Wilson 95% CI bounds (d1_lo/d1_hi/…) and the settled n so
    a card can state its own uncertainty without the chart. 0.0 when no
    cohort is old enough."""
    curve = retention_curve(df, max_day=7, mode="exact")
    out = {
        "d1": 0.0, "d7": 0.0,
        "d1_lo": 0.0, "d1_hi": 0.0, "d7_lo": 0.0, "d7_hi": 0.0,
        "n": 0,
    }
    if curve.empty:
        return out
    n = int(curve["cohort_devices"].iloc[0])
    out["n"] = n
    for off, key in ((1, "d1"), (7, "d7")):
        row = curve[curve["day_offset"] == off]
        if not row.empty and n > 0:
            retained = int(row["retained"].iloc[0])
            out[key] = float(row["retained_frac"].iloc[0])
            lo, hi = wilson_interval(retained, n)
            out[f"{key}_lo"], out[f"{key}_hi"] = lo, hi
    return out


def settled_cohort_size(df: pd.DataFrame, max_day: int = 7) -> int:
    """Number of devices in the settled denominator behind the pooled
    curve (installs ≤ today − max_day). Surfaced in the curve subtitle so
    the small-N noise floor is explicit rather than implied."""
    if df.empty:
        return 0
    first = _first_seen(df)
    today = pd.Timestamp.now(tz="UTC").normalize()
    return int((first <= today - pd.Timedelta(days=max_day)).sum())


# ── Cohort retention ─────────────────────────────────────────────────────────


def cohort_retention(df: pd.DataFrame, max_day: int = 7) -> pd.DataFrame:
    """Per-cohort retention, long form. One row per (cohort_date,
    day_offset) with the cohort size, retained-device count, and fraction.
    Censored cells (install + offset in the future) are omitted."""
    cols = ["cohort_date", "day_offset", "cohort_size", "retained", "retained_frac"]
    if df.empty:
        return pd.DataFrame(columns=cols)
    first = _first_seen(df)
    active = _active_device_days(df).merge(
        first.rename("cohort_date"), left_on="device_id", right_index=True,
    )
    active["day_offset"] = (active["day"] - active["cohort_date"]).dt.days
    sizes = first.value_counts()  # cohort_date -> size
    today = pd.Timestamp.now(tz="UTC").normalize()
    rows = []
    for cohort_date, size in sizes.items():
        for off in range(0, max_day + 1):
            if cohort_date + pd.Timedelta(days=off) > today:
                continue  # censored — not enough wall time yet
            retained = int(active[
                (active["cohort_date"] == cohort_date)
                & (active["day_offset"] == off)
            ]["device_id"].nunique())
            rows.append({
                "cohort_date": cohort_date,
                "day_offset": off,
                "cohort_size": int(size),
                "retained": retained,
                "retained_frac": retained / int(size),
            })
    return pd.DataFrame(rows, columns=cols)


def retention_curve(
    df: pd.DataFrame, max_day: int = 7, mode: str = "exact",
) -> pd.DataFrame:
    """Single pooled D0..Dn curve over a CONSISTENT denominator: only
    cohorts old enough to be fully observed through `max_day`
    (install ≤ today − max_day) are counted, and every offset divides by
    that same settled device set. Fixing the population (vs. a different
    per-offset-eligible denominator per point) is half of the honest
    read; the other half is the retention *flavour*:

      • mode="exact" (default): device active on precisely day install+n.
        Classic Dn — the basis the benchmarks are quoted against, so it
        drives the KPI cards and the default curve. Banded with a Wilson
        CI (frac_lo/frac_hi columns) because it's bumpy on small N.
      • mode="unbounded" ("rolling"): retained at offset n = device active
        on day install+n OR any LATER observed day. Monotone
        non-increasing, but it overstates classic Dn — shown only as a
        labelled secondary curve line, never on a card.

    Columns: [day_offset, cohort_devices, retained, retained_frac,
    frac_lo, frac_hi]. The constant cohort_devices column is the small-N
    denominator, kept on every row so callers can label the curve with N;
    frac_lo/frac_hi are the Wilson 95% bounds for the band."""
    cols = ["day_offset", "cohort_devices", "retained", "retained_frac",
            "frac_lo", "frac_hi"]
    if df.empty:
        return pd.DataFrame(columns=cols)
    if mode not in ("unbounded", "exact"):
        raise ValueError(f"mode must be 'unbounded' or 'exact', got {mode!r}")
    first = _first_seen(df)
    today = pd.Timestamp.now(tz="UTC").normalize()
    settled = first[first <= today - pd.Timedelta(days=max_day)]
    total = len(settled)
    if total == 0:
        return pd.DataFrame(columns=cols)
    sub = df[df["device_id"].isin(set(settled.index))]
    active = _active_device_days(sub).merge(
        settled.rename("cohort_date"), left_on="device_id", right_index=True,
    )
    active["day_offset"] = (active["day"] - active["cohort_date"]).dt.days
    # For unbounded, a device "survives to offset n" iff its LAST observed
    # offset ≥ n; compare that per-device max against each offset.
    max_offset = active.groupby("device_id")["day_offset"].max()
    rows = []
    for off in range(0, max_day + 1):
        if mode == "exact":
            retained = int(
                active[active["day_offset"] == off]["device_id"].nunique()
            )
        else:
            retained = int((max_offset >= off).sum())
        lo, hi = wilson_interval(retained, total)
        rows.append({
            "day_offset": off,
            "cohort_devices": total,
            "retained": retained,
            "retained_frac": retained / total,
            "frac_lo": lo,
            "frac_hi": hi,
        })
    return pd.DataFrame(rows, columns=cols)


def retention_matrix(
    df: pd.DataFrame, max_day: int = 7, min_cohort: int = MIN_COHORT_SIZE,
) -> pd.DataFrame:
    """Wide cohort × day-offset matrix of retained_frac — the classic
    retention triangle. Rows = cohort_date, cols = 0..max_day. Censored
    cells are NaN so the heatmap leaves them blank.

    Cohorts smaller than `min_cohort` devices are suppressed: at the live
    ~120d span most cohorts are a single device, where each cell is one
    returner's coin-flip and ~25 such rows render as illegible noise.
    Keeping only n≥`min_cohort` rows leaves the cells that carry signal."""
    cr = cohort_retention(df, max_day=max_day)
    if cr.empty:
        return pd.DataFrame()
    cr = cr[cr["cohort_size"] >= min_cohort]
    if cr.empty:
        return pd.DataFrame()
    mat = cr.pivot(index="cohort_date", columns="day_offset", values="retained_frac")
    return mat.reindex(columns=range(0, max_day + 1))


def new_vs_returning_by_day(df: pd.DataFrame, days: int = 30) -> pd.DataFrame:
    """Per UTC day: count of NEW devices (first-ever-seen that day) vs
    RETURNING (seen before). Continuous day index, zero-filled. Columns:
    [date, new, returning]."""
    end = pd.Timestamp.now(tz="UTC").normalize()
    full_idx = pd.date_range(end=end, periods=days, freq="D", tz="UTC")
    if df.empty:
        return pd.DataFrame({"date": full_idx, "new": 0, "returning": 0})
    first = _first_seen(df)
    dd = _active_device_days(df).merge(
        first.rename("first_day"), left_on="device_id", right_index=True,
    )
    dd["is_new"] = dd["day"] == dd["first_day"]
    dd = dd[dd["day"] >= day_floor_cutoff(days)]
    g = dd.groupby("day")["is_new"].agg(new="sum", total="count")
    g["returning"] = g["total"] - g["new"]
    g = g.reindex(full_idx, fill_value=0)
    out = g.reset_index().rename(columns={"index": "date"})
    return out[["date", "new", "returning"]].astype({"new": int, "returning": int})


def sessions_per_active_day(df: pd.DataFrame, days: int = 30) -> pd.Series:
    """Plays-per-active-day for every (device, day) in the window — the
    raw material for a session-depth histogram. A long right tail means a
    few players binge; a wall at 1 means most sessions are single runs."""
    if df.empty:
        return pd.Series([], dtype=int, name="plays")
    sub = in_window(df, days).copy()
    if sub.empty:
        return pd.Series([], dtype=int, name="plays")
    sub["day"] = sub["played_at"].dt.floor("D")
    return sub.groupby(["device_id", "day"]).size().reset_index(name="plays")["plays"]


# ── Engagement segments + roster ─────────────────────────────────────────────


def engagement_segments(df: pd.DataFrame, days: int = 30) -> pd.DataFrame:
    """Count of players in each play-count bucket: 1 / 2–5 / 6–20 / 21+.
    Returned as a long frame with stable ordering so the bar chart
    renders the segments top-to-bottom in increasing engagement."""
    buckets = [
        ("1 play",     1, 1),
        ("2–5 plays",  2, 5),
        ("6–20 plays", 6, 20),
        ("21+ plays",  21, 10**9),
    ]
    empty = pd.DataFrame({
        "segment": [b[0] for b in buckets],
        "players": [0] * len(buckets),
    })
    if df.empty:
        return empty
    recent = in_window(df, days)
    if recent.empty:
        return empty
    plays_per_device = recent.groupby("device_id").size()
    rows = []
    for label, lo, hi in buckets:
        rows.append({
            "segment": label,
            "players": int(((plays_per_device >= lo) & (plays_per_device <= hi)).sum()),
        })
    return pd.DataFrame(rows)


def roster(df: pd.DataFrame, days: int = 30, top_n: int = 50) -> pd.DataFrame:
    """One row per active player in the last `days` days. Sorted by
    plays desc, capped at top_n. Used by the bottom table in app.py;
    nickname + color are joined on at render time so this stays
    library-free."""
    empty_cols = [
        "device_id", "plays", "days_active",
        "best_score", "avg_duration_s", "last_seen",
    ]
    if df.empty:
        return pd.DataFrame(columns=empty_cols)
    sub = in_window(df, days).copy()
    if sub.empty:
        return pd.DataFrame(columns=empty_cols)
    sub["day"] = sub["played_at"].dt.date
    grouped = sub.groupby("device_id").agg(
        plays=("id", "count"),
        days_active=("day", "nunique"),
        best_score=("score", "max"),
        avg_duration_s=("duration_s", "mean"),
        last_seen=("played_at", "max"),
    ).reset_index()
    # Single-play devices are kept — they're the bounce signal for the
    # game's first-run experience and previously got hidden, which made
    # the dashboard pretend they didn't exist. Sort by plays desc, then
    # by last_seen desc so the most recent one-shots still appear near
    # the top when there's a tie.
    return (
        grouped.sort_values(["plays", "last_seen"], ascending=[False, False])
               .head(top_n)
               .reset_index(drop=True)
    )
