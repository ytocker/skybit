"""Regenerate the before/after warmup-ramp curve plots under
``docs/difficulty_curves/``. Run from the repo root:

    python tools/plot_difficulty_curves.py

Plots compare the previous linear ``_ramp_t()`` against the current
plateau-then-ease-out shape (commit 09ca431) for gap, scroll, and
pillar spacing. Numbers are pulled live from ``game.config`` so the
plots stay in sync with whatever the constants currently are.
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

from game.config import (
    GAP_NEWBIE_START, GAP_START,
    SCROLL_NEWBIE_BASE, SCROLL_BASE,
    PIPE_SPACING_NEWBIE, PIPE_SPACING,
    RAMP_PIPES, PLATEAU_PIPES,
)


def t_old(pp: int) -> float:
    return min(1.0, pp / RAMP_PIPES)


def t_new(pp: int) -> float:
    if pp < PLATEAU_PIPES:
        return 0.0
    x = min(1.0, (pp - PLATEAU_PIPES) / (RAMP_PIPES - PLATEAU_PIPES))
    return 1.0 - (1.0 - x) ** 2


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


OUT_DIR = os.path.join(ROOT, "docs", "difficulty_curves")

PANELS = [
    ("Pipe gap",       "gap (px)",
     GAP_NEWBIE_START, GAP_START,
     "wider = easier",
     "skybit_gap.png"),
    ("Scroll speed",   "scroll (px/s)",
     SCROLL_NEWBIE_BASE, SCROLL_BASE,
     "faster = harder",
     "skybit_scroll.png"),
    ("Pillar spacing", "spacing (px)",
     PIPE_SPACING_NEWBIE, PIPE_SPACING,
     "wider = easier",
     "skybit_spacing.png"),
]


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    xs = list(range(0, 31))
    for title, ylabel, newbie, regular, sense, fname in PANELS:
        ys_old = [lerp(newbie, regular, t_old(x)) for x in xs]
        ys_new = [lerp(newbie, regular, t_new(x)) for x in xs]
        fig, ax = plt.subplots(figsize=(8, 4.5), dpi=120)
        ax.plot(xs, ys_old, color="#888", linestyle="--", linewidth=2,
                label="before (linear)", marker="o", markersize=4)
        ax.plot(xs, ys_new, color="#c8344a", linewidth=2.5,
                label="after (plateau + ease-out)", marker="o", markersize=4)
        ax.axhline(newbie,  color="#bbb", linestyle=":", linewidth=1)
        ax.axhline(regular, color="#bbb", linestyle=":", linewidth=1)
        ax.axvspan(0, PLATEAU_PIPES, color="#fce8ec", alpha=0.6,
                   label=f"plateau ({PLATEAU_PIPES} pillars)")
        ax.axvline(RAMP_PIPES, color="#bbb", linestyle=":", linewidth=1)
        ax.text(RAMP_PIPES + 0.3, regular, "  regular", va="center",
                fontsize=9, color="#666")
        ax.text(0.3, newbie, "  newbie", va="center", fontsize=9, color="#666")
        ax.set_title(f"{title}   ({sense})", fontsize=13)
        ax.set_xlabel("pillars passed")
        ax.set_ylabel(ylabel)
        ax.set_xlim(0, 30)
        ax.grid(True, alpha=0.3)
        ax.legend(loc="best", framealpha=0.9)
        fig.tight_layout()
        out_path = os.path.join(OUT_DIR, fname)
        fig.savefig(out_path)
        plt.close(fig)
        print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
