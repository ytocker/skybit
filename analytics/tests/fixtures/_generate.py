"""
Deterministic generator for plays_sample.json — the offline demo dataset
used by `STREAMLIT_USE_FIXTURE=1`.

The unit tests assert correctness against in-code frames (see the
test_metrics_* modules), so this fixture's job is only to be *believable*:
enough devices, days, retention shapes, power-up signal, and a few
rejected submits that every tab renders something real-looking. Re-run
with `python tests/fixtures/_generate.py` after changing the archetypes.

Timestamps are authored relative to END below; data.py rebases the newest
row to "now" in fixture mode so the demo always looks live.
"""
from __future__ import annotations

import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

POWERUPS = ("triple", "magnet", "slowmo", "kfc", "ghost", "grow", "reverse", "surprise")
END = datetime(2026, 6, 15, 21, 0, tzinfo=timezone.utc)
OUT = Path(__file__).with_name("plays_sample.json")

rng = random.Random(20260615)


def _pu(**overrides) -> dict:
    d = {k: 0 for k in POWERUPS}
    d.update(overrides)
    return d


def _run(dev: str, day_offset: int, *, skill: float, magnet: bool,
         grow: bool, submit_error=None) -> dict:
    """One play. `skill` ∈ [0,1] scales score/duration/pillars. magnet
    runs trend long+high (creates positive efficacy); grow runs trend
    short (negative), so powerup_efficacy has a real signal."""
    when = END - timedelta(days=day_offset,
                           hours=rng.randint(0, 12), minutes=rng.randint(0, 59))
    base = 8 + skill * 220 + (40 if magnet else 0) - (25 if grow else 0)
    score = max(1, int(base + rng.gauss(0, 12)))
    duration = max(4, int(6 + skill * 170 + (30 if magnet else 0) - (18 if grow else 0)
                          + rng.gauss(0, 8)))
    pillars = max(0, int(duration / 6 + rng.gauss(0, 1)))
    near = max(0, int(pillars * 0.3 + rng.gauss(0, 1)))
    coins = max(0, int(pillars * 2.2 + (8 if magnet else 0) + rng.gauss(0, 3)))
    pu = _pu()
    if magnet:
        pu["magnet"] = rng.randint(1, 3)
    if grow:
        pu["grow"] = rng.randint(1, 2)
    for k in ("triple", "slowmo", "kfc", "ghost", "surprise"):
        if rng.random() < 0.18 + skill * 0.2:
            pu[k] = rng.randint(1, 2)
    return {
        "device_id": dev,
        "played_at": when.isoformat(),
        "score": score,
        "duration_s": duration,
        "coins": coins,
        "pillars": pillars,
        "near_misses": near,
        "powerups": pu,
        "submit_error": submit_error,
    }


def build() -> list[dict]:
    rows: list[dict] = []

    def dev(prefix, n):
        return f"{prefix}{n:02d}-0000-0000-0000-000000000000"

    # Whales: near-daily, multiple sessions, skilled, magnet users.
    for i in range(3):
        d = dev("a", i)
        for off in range(0, 44, rng.choice((1, 1, 2))):
            for _ in range(rng.randint(1, 4)):
                rows.append(_run(d, off, skill=rng.uniform(0.6, 0.95),
                                 magnet=True, grow=False))

    # Regulars: a few days/week, mid skill, sometimes magnet.
    for i in range(8):
        d = dev("b", i)
        start = rng.randint(0, 30)
        for off in range(start, min(start + 20, 44), rng.choice((2, 3, 4))):
            for _ in range(rng.randint(1, 2)):
                rows.append(_run(d, off, skill=rng.uniform(0.3, 0.7),
                                 magnet=rng.random() < 0.5, grow=rng.random() < 0.2))

    # D1 returners: install day + next day.
    for i in range(5):
        d = dev("c", i)
        install = rng.randint(2, 40)
        rows.append(_run(d, install, skill=rng.uniform(0.2, 0.5), magnet=False, grow=True))
        rows.append(_run(d, install - 1, skill=rng.uniform(0.2, 0.5), magnet=False, grow=False))

    # D7 returners: install day + day 7.
    for i in range(4):
        d = dev("d", i)
        install = rng.randint(8, 40)
        rows.append(_run(d, install, skill=rng.uniform(0.2, 0.6), magnet=False, grow=False))
        rows.append(_run(d, install - 7, skill=rng.uniform(0.3, 0.7), magnet=True, grow=False))

    # One-shots: single low-skill, grow-heavy run (the bounce population).
    for i in range(12):
        d = dev("e", i)
        rows.append(_run(d, rng.randint(0, 43), skill=rng.uniform(0.0, 0.3),
                         magnet=False, grow=rng.random() < 0.6))

    # A handful of rejected submits across the window (cheat/bug signal).
    reasons = ["score: exceeds MAX_PLAUSIBLE_SCORE", "chain: hash mismatch",
               "coins: volume exceeds rush ceiling", "time: too short for pillars"]
    for i, reason in enumerate(reasons):
        rows.append(_run(dev("f", i), rng.randint(0, 20), skill=0.5,
                         magnet=False, grow=False, submit_error=reason))

    # One legit high score in the 10k–100k band (proves the ceiling bump
    # keeps it) and one above 100k (proves plausible() still drops it).
    keep = _run(dev("g", 0), 3, skill=0.9, magnet=True, grow=False)
    keep["score"] = 42_000
    rows.append(keep)
    drop = _run(dev("g", 1), 2, skill=0.9, magnet=False, grow=False)
    drop["score"] = 250_000
    rows.append(drop)

    rows.sort(key=lambda r: r["played_at"], reverse=True)
    for n, r in enumerate(rows, 1):
        r["id"] = n
    return rows


if __name__ == "__main__":
    data = build()
    OUT.write_text(json.dumps(data, indent=0), encoding="utf-8")
    print(f"wrote {len(data)} rows → {OUT}")
