"""Overlay the three GENIE-PLACEMENT candidate pillars (plus the current
position) onto the canonical run-content map, written to
``docs/screenshots/genie_placement_candidates.png``. Run from the repo root:

    python tools/plot_genie_placement_candidates.py

This is a DESIGN-PROPOSAL figure, not a shipped artifact: it reuses
``compute_axis`` / ``draw_map`` from ``plot_event_pagoda_map`` so the base map
(sky strip, weather curves, clown band @ CLOWN_START_PILLAR, newbie ramp,
treasure-box finale, and the CURRENT genie lamp @ weather.GENIE_PILLAR) is byte-
for-byte the same chart we always reason on — then draws the candidate genie
pillars on top so the move can be judged against the live event landscape.

The candidate pillars are proposals (knight-wish/clown-gauntlet reasoning), so
they're hardcoded here rather than read from config — nothing in the game moves.
The canonical ``event_pagoda_map_clown_v6.png`` is left untouched.
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

from game import weather
from tools.plot_event_pagoda_map import compute_axis, draw_map

# All candidates share ONE colour so the eye groups them as "the proposals" and
# reads them apart from the CURRENT genie (purple, drawn by draw_map) and the
# live event bands. #1 is the recommendation — same colour, just a star marker.
CAND_COLOR = "#111111"
# (rank, pillar, one-line thesis).
CANDIDATES = [
    (1, 55, "foreshadow (wish covers the gauntlet)"),
    (2, 130, "post-storm reward"),
    (3, 61, "ambush (inside the lead-in)"),
]


def main() -> None:
    out_dir = os.path.join(ROOT, "docs", "screenshots")
    os.makedirs(out_dir, exist_ok=True)

    pillars, phases, day_end = compute_axis()

    fig, (ax_sky, ax) = plt.subplots(
        2, 1, figsize=(13, 6.4), dpi=130,
        gridspec_kw=dict(height_ratios=[1, 6], hspace=0.08),
        sharex=True,
    )
    draw_map(
        ax_sky, ax, pillars, phases, day_end,
        sky_title=("Skybit — GENIE placement candidates vs the live event map  "
                   "(proposal overlay; no game constant moved)"),
    )

    # Flag the CURRENT genie pillar (already drawn by draw_map as "Genie lamp")
    # so it reads as the baseline the candidates are measured against.
    cur = weather.GENIE_PILLAR
    ax.annotate(f"CURRENT\ngenie @ {cur}", (cur, 0.5),
                textcoords="offset points", xytext=(-8, 0), rotation=90,
                ha="right", va="center", fontsize=7.5, fontweight="bold",
                color="#7a2a7c", zorder=9)

    # Candidate pillars — all ONE colour; the recommendation gets a star (same
    # colour) so it stands out without adding a second hue to decode.
    for rank, x, thesis in CANDIDATES:
        is_pick = rank == 1
        ax.axvline(x, color=CAND_COLOR, linewidth=2.4,
                   linestyle="-" if is_pick else (0, (5, 3)),
                   alpha=0.95 if is_pick else 0.8, zorder=5)
        ax.plot([x], [1.065],
                marker="*" if is_pick else "o",
                color=CAND_COLOR, markersize=18 if is_pick else 10,
                markeredgecolor="white", markeredgewidth=0.9,
                clip_on=False, zorder=9,
                label=(f"#{rank} candidate genie @ {x}"
                       + ("  ★ recommended" if is_pick else "")))
        ax.annotate(f"#{rank} @ {x}\n{thesis}", (x, 0.5),
                    textcoords="offset points", xytext=(6, 0), rotation=90,
                    ha="left", va="center",
                    fontsize=7.5 if is_pick else 7,
                    fontweight="bold" if is_pick else "normal",
                    color=CAND_COLOR, zorder=9)

    fig.tight_layout()
    out_path = os.path.join(out_dir, "genie_placement_candidates.png")
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {out_path}")
    print(f"current genie @ {cur}; candidates: "
          + ", ".join(f"#{r} {p}" for r, p, _ in CANDIDATES))


if __name__ == "__main__":
    main()
