"""Render a BEFORE/AFTER comparison of the day→night sky-timing swap as two
FULL content maps (sky banner + the whole event/graph panel) stacked, under
``docs/screenshots/sky_earlier_before_after_v5.png``.

    python tools/plot_sky_earlier_before_after.py

"Before" = the previous biome timing (full DAY_EXTRA on every evening keyframe,
solid-day hold at 0.60 → sky frozen on solid day until ~pillar 42). "After" =
the current biome (GOLDEN..NIGHT pulled earlier by NIGHT_BORROW_SECONDS, hold at
0.51 → sky leaves daytime by ~pillar 27, night ~15 pillars longer). The event
graph is pillar-anchored and identical in both panels — only the sky banner (and
its phase gridlines) differs, which is the point of the comparison. The "before"
keyframes are reconstructed from the live palettes paired with their old phase
positions, so the only thing that changes between the two maps is the timing.
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from game import biome, config
from tools.plot_event_pagoda_map import (
    compute_axis, draw_map, phase_labels_for, print_summary,
)

_BASE = biome._BASE_CYCLE_SECONDS
_DE = config.DAY_EXTRA_SECONDS
_CYCLE = biome.CYCLE_SECONDS

# Base (pre-remap) phase fractions, in palette order. The DAY-hold (index 1) and
# the wrap (last) are derived, not base keyframes.
_BASE_FRACS = [0.0, None, 0.23125, 0.36250, 0.51250, 0.64375, 0.79375, 0.90625, 1.0]
_NAMES = ["DAY", "", "GOLDEN HOUR", "SUNSET", "DUSK", "NIGHT", "PREDAWN", "SUNRISE", ""]
_PREV_HOLD_FRAC = 0.60   # the previous DAY_HOLD_FRAC, before the swap


def _old_phase(frac):
    return (frac * _BASE + _DE) / _CYCLE


def _before_keyframes():
    """Old phases (full DAY_EXTRA shift, hold 0.60) paired with the live
    palettes (palettes are identical before/after — only timing changed)."""
    pals = [dict(p) for _, p in biome._KEYFRAMES]
    golden_old = _old_phase(0.23125)
    phases = []
    for i, frac in enumerate(_BASE_FRACS):
        if i == 1:
            phases.append(golden_old * _PREV_HOLD_FRAC)
        else:
            phases.append(0.0 if frac == 0.0 else 1.0 if frac == 1.0 else _old_phase(frac))
    return list(zip(phases, pals))


def main() -> None:
    out_dir = os.path.join(ROOT, "docs", "screenshots")
    os.makedirs(out_dir, exist_ok=True)

    pillars, phases, day_end = compute_axis()
    after_kf = list(biome._KEYFRAMES)
    before_kf = _before_keyframes()

    after_labels = phase_labels_for(after_kf, _NAMES)
    before_labels = phase_labels_for(before_kf, _NAMES)

    fig, axes = plt.subplots(
        4, 1, figsize=(13, 12.6), dpi=130,
        gridspec_kw=dict(height_ratios=[1, 6, 1, 6], hspace=0.08),
        sharex=True,
    )
    fig.subplots_adjust(hspace=0.6)

    # ── BEFORE map (top two rows) ────────────────────────────────────────────
    biome._KEYFRAMES[:] = before_kf
    draw_map(axes[0], axes[1], pillars, phases, day_end,
             phase_labels=before_labels, show_xlabel=False, show_legend=False,
             sky_title="BEFORE  ·  sky held solid day until ~pillar 42 "
                       "(evening crammed into the back half)")

    # ── AFTER map (bottom two rows, keeps the shared legend) ──────────────────
    biome._KEYFRAMES[:] = after_kf
    draw_map(axes[2], axes[3], pillars, phases, day_end,
             phase_labels=after_labels, show_xlabel=True, show_legend=True,
             sky_title="AFTER  ·  sky starts changing by ~pillar 27, "
                       "night ~15 pillars longer (total day unchanged)")

    fig.suptitle("Skybit — day→night sky timing: trim the day, lengthen the "
                 "night (events are pillar-anchored & unchanged)",
                 fontsize=13, y=0.995)

    out = os.path.join(out_dir, "sky_earlier_before_after_v5.png")
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {out}")
    print_summary(pillars, phases, day_end)


if __name__ == "__main__":
    main()
