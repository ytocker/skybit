"""
Supabase REST fetch + cache.

Uses stdlib urllib — matches the auth pattern in tools/diagnose_supabase.py
(apikey + Bearer headers). No need for supabase-py: we only do two
unfiltered SELECTs and the SDK would be dead weight.

Service-role key is required (the plays table has no anon SELECT policy
by design). On Streamlit Community Cloud the key lives in encrypted
secrets — never reaches the browser. Locally it lives in
.streamlit/secrets.toml which is gitignored.

Offline iteration: set STREAMLIT_USE_FIXTURE=1 and the loader returns
the JSON fixture under tests/fixtures/ instead of hitting Supabase.
Lets the UI be built without credentials.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from urllib import error, parse, request

import pandas as pd
import streamlit as st

_TIMEOUT_S = 15
_FIXTURE_ENV = "STREAMLIT_USE_FIXTURE"
_FIXTURE_PATH = Path(__file__).parent / "tests" / "fixtures" / "plays_sample.json"

# PostgREST returns at most this many rows per request. Surfaced as a
# constant (not a magic literal) so the cap is visible and the app can
# warn when a fetch saturates it rather than silently truncating history.
ROW_CAP = 50_000


def _use_fixture() -> bool:
    return os.environ.get(_FIXTURE_ENV) == "1"


def _rebase_to_now(df: pd.DataFrame) -> pd.DataFrame:
    """Shift the (statically authored) fixture so its newest row lands at
    'now', preserving all relative spacing. Keeps the offline demo looking
    live — today's KPIs populate and retention cohorts stay settled —
    regardless of when the dashboard is run. No-op on live data."""
    if df.empty:
        return df
    shift = pd.Timestamp.now(tz="UTC") - df["played_at"].max()
    df = df.copy()
    df["played_at"] = df["played_at"] + shift
    return df


def _creds() -> tuple[str, str]:
    """Pull (url, service_role_key) from Streamlit secrets. Raises a
    user-visible error in the UI rather than KeyError if missing."""
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["service_role_key"]
    except (KeyError, FileNotFoundError) as e:
        raise RuntimeError(
            "Supabase credentials missing. Set [supabase].url and "
            "[supabase].service_role_key in .streamlit/secrets.toml "
            "(local) or the Streamlit Cloud Secrets UI (deployed). "
            "Or set STREAMLIT_USE_FIXTURE=1 to run against the bundled "
            "sample data."
        ) from e
    return url, key


def _get_json(path: str) -> list[dict]:
    """GET /rest/v1/<path>, decode JSON, return list. The PostgREST
    endpoint returns an array for table queries; non-2xx raises so
    Streamlit shows a clear error rather than a silent empty chart."""
    url, key = _creds()
    target = url.rstrip("/") + "/rest/v1/" + path.lstrip("/")
    req = request.Request(
        target,
        headers={
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Accept": "application/json",
        },
    )
    try:
        with request.urlopen(req, timeout=_TIMEOUT_S) as resp:
            body = resp.read().decode("utf-8")
    except error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:300]
        raise RuntimeError(f"Supabase HTTP {e.code}: {body}") from e
    return json.loads(body)


def _normalise_plays(rows: list[dict]) -> pd.DataFrame:
    """Coerce the raw JSON rows into a typed pandas frame.

    Keeps the powerups dict as a column so charts.py can sum across the
    JSONB keys without re-parsing. played_at is parsed to a tz-aware
    Timestamp so date filters and groupby(date) work cleanly."""
    if not rows:
        return pd.DataFrame(
            columns=[
                "id", "device_id", "played_at", "score",
                "duration_s", "coins", "pillars", "near_misses", "powerups",
                "submit_error",
            ]
        )
    df = pd.DataFrame(rows)
    df["played_at"] = pd.to_datetime(df["played_at"], utc=True)
    int_cols = ["score", "duration_s", "coins", "pillars", "near_misses"]
    for c in int_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0).astype(int)
    if "powerups" not in df.columns:
        df["powerups"] = [{} for _ in range(len(df))]
    # submit_error is null on the overwhelming majority of rows (only set
    # when a top-10 submit was rejected). Default-fill so older fixtures
    # and any pre-column rows still load, and keep it as nullable text —
    # never coerce to a number.
    if "submit_error" not in df.columns:
        df["submit_error"] = None
    df["submit_error"] = df["submit_error"].where(df["submit_error"].notna(), None)
    return df


# ── Public, cached fetchers ──────────────────────────────────────────────────


@st.cache_data(ttl=60, show_spinner="Loading plays…")
def fetch_plays(days: int = 90) -> pd.DataFrame:
    """Up to `days` of telemetry rows. Cached for 60s so the 1-minute
    autorefresh tick hits cache from each new viewer. Cap to 90 days by
    default to keep first-page load under ~2s for reasonable volumes."""
    if _use_fixture():
        with open(_FIXTURE_PATH, "r", encoding="utf-8") as f:
            df = _normalise_plays(json.load(f))
        return _rebase_to_now(df)
    cutoff_iso = (pd.Timestamp.now(tz="UTC") - pd.Timedelta(days=days)).isoformat()
    qs = parse.urlencode({
        "select": "id,device_id,played_at,score,duration_s,coins,"
                  "pillars,near_misses,powerups,submit_error",
        "played_at": f"gte.{cutoff_iso}",
        "order": "played_at.desc",
        "limit": ROW_CAP,
    })
    return _normalise_plays(_get_json(f"plays?{qs}"))


def hit_row_cap(df: pd.DataFrame) -> bool:
    """True when a fetch came back exactly at the cap, i.e. history was
    likely truncated. The app surfaces a warning so the silent-drop the
    bare 50k literal used to cause is now visible."""
    return len(df) >= ROW_CAP


@st.cache_data(ttl=60, show_spinner="Loading leaderboard…")
def fetch_scores() -> pd.DataFrame:
    """Top-N scores from public.scores (the named leaderboard). Used to
    cross-check that the dashboard's top scores agree with the in-game
    view."""
    if _use_fixture():
        # The fixture lives only on plays; build a stand-in from it.
        df = fetch_plays(days=365)
        if df.empty:
            return pd.DataFrame(columns=["name", "score"])
        top = df.nlargest(10, "score")[["device_id", "score"]].rename(
            columns={"device_id": "name"}
        )
        return top.reset_index(drop=True)
    qs = parse.urlencode({
        "select": "name,score",
        "order":  "score.desc",
        "limit":  100,
    })
    rows = _get_json(f"scores?{qs}")
    return pd.DataFrame(rows) if rows else pd.DataFrame(columns=["name", "score"])
