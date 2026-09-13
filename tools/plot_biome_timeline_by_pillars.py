"""Render the FULL Skybit game-schedule timeline keyed to PILLARS PASSED
under ``docs/screenshots/biome_event_timeline_by_pillars.png``. Run from
the repo root:

    python tools/plot_biome_timeline_by_pillars.py

The x-axis is pillars (Pip's score) across ONE biome cycle. Pillars are
strictly monotonic in time, so each event lands at a precise pillar count.
The mapping uses the SAME onboarding-ramp dwell math the game uses
(``build_time_for_pillar``), identical to ``weather._phase_for_pillar`` which
anchors rain at ``RAIN_START_PILLAR`` and snow at ``SNOW_START_PILLAR``.

Five stacked panels share the pillar axis, and every track is computed from
the REAL game code (not hand-drawn) so the chart tracks config edits:

  1. Biome sky strip          — ``biome.palette_for_time``
  2. Weather events           — ``weather.*_intensity`` curves + lightning
                                 window + the full-day-completion marker
  3. Sidewalk crowd / day-arc — ``foreground_promenade._roster_for`` bands +
                                 ``_population`` × ``_weather_crowd_factor``
  4. Sidewalk state rows      — dressing windows + weather-reactive states
  5. Object count             — MEASURED far/near sidewalk objects, read from
                                 the live depth-buffer selection pass
"""
from __future__ import annotations

import bisect
import os
import sys

# Headless before pygame is pulled in (the object-count panel runs the real
# foreground selection, which needs a Surface).
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

import pygame

from game import biome, weather, config
from game import foreground_promenade as _prom
from game import foreground_near_lane as _near
from game import foreground_zbuffer as _zbuf

CYCLE = biome.CYCLE_SECONDS
N = 1800                   # sample resolution across the cycle

GENIE_PILLAR = weather.GENIE_PILLAR


def _hex(rgb):
    return "#%02x%02x%02x" % tuple(int(c) for c in rgb[:3])


PHASE_LABELS = [
    (0.00000, "DAY"),
    (0.23125, "GOLDEN\nHOUR"),
    (0.36250, "SUNSET"),
    (0.51250, "DUSK"),
    (0.64375, "NIGHT"),
    (0.79375, "PREDAWN"),
    (0.90625, "SUNRISE"),
]

# Real weather curves (the deferred cosmetic "mist" of the old plotter is
# dropped — it has no in-game implementation, and this chart shows only what
# actually happens in gameplay).
CURVES = [
    ("Morning thermal (geysers)", weather.thermal_intensity, "#e0663a"),
    ("Calm breeze (leaves)",      weather.calm_breeze,      "#d68a2e"),
    ("Rain",                       weather.rain_intensity,   "#2f6fb0"),
    ("Snow squall (tailwind)",     weather.storm_intensity,  "#8a6fc0"),
]

# Day-arc bands straight from foreground_promenade._roster_for's phase windows.
ROSTER_BANDS = [
    (0.00, 0.14, "FOOD-MARKET\nRUSH",  "#e8b54a"),
    (0.14, 0.25, "CALM\nMORNING",      "#cfe0a0"),
    (0.25, 0.40, "GOLDEN\nSTROLL",     "#e6c98a"),
    (0.40, 0.58, "DUSK\nLAMPS",        "#b9a6d6"),
    (0.58, 0.80, "NIGHT\nFESTIVAL",    "#8a6fc0"),
    (0.80, 0.85, "TEAR-\nDOWN",        "#7a8290"),
    (0.85, 1.00, "SUNRISE\nVENDORS",   "#f0b48a"),
]


def build_time_for_pillar(max_pillars: int) -> list:
    """Cumulative wall-clock seconds to reach each pillar, walking the same
    onboarding-ramp dwell math World uses (spacing/scroll per pillar, both
    interpolated on the _ramp_t() quadratic ease)."""
    T = [0.0]
    for pp in range(1, max_pillars + 1):
        pp_in = pp - 1
        if pp_in < config.PLATEAU_PIPES:
            t = 0.0
        else:
            denom = max(1, config.RAMP_PIPES - config.PLATEAU_PIPES)
            x = min(1.0, (pp_in - config.PLATEAU_PIPES) / denom)
            t = 1.0 - (1.0 - x) ** 2
        spacing = (config.PIPE_SPACING_NEWBIE
                   + (config.PIPE_SPACING - config.PIPE_SPACING_NEWBIE) * t)
        scroll = (config.SCROLL_NEWBIE_BASE
                  + (config.SCROLL_BASE - config.SCROLL_NEWBIE_BASE) * t)
        T.append(T[-1] + spacing / scroll)
    return T


def build_scroll_for_pillar(max_pillars: int) -> list:
    """Cumulative world-x (bg_scroll) to reach each pillar — the sum of
    inter-pillar spacings, since over each dwell bg_scroll advances by exactly
    one spacing. Used to sample the foreground at the right world window."""
    S = [0.0]
    for pp in range(1, max_pillars + 1):
        pp_in = pp - 1
        if pp_in < config.PLATEAU_PIPES:
            t = 0.0
        else:
            denom = max(1, config.RAMP_PIPES - config.PLATEAU_PIPES)
            x = min(1.0, (pp_in - config.PLATEAU_PIPES) / denom)
            t = 1.0 - (1.0 - x) ** 2
        spacing = (config.PIPE_SPACING_NEWBIE
                   + (config.PIPE_SPACING - config.PIPE_SPACING_NEWBIE) * t)
        S.append(S[-1] + spacing)
    return S


def _measure_sidewalk(surf, phase, t, scroll):
    """Genuine on-screen sidewalk object count at (phase, t, scroll): run the
    REAL far + near selection passes and read the depth-buffer queue. Far-lane
    feet sit at GROUND_Y-1 (594); near-lane at NEAR_GROUND_Y (638) — split on
    base_y. Scene vignettes enqueue each sub-object separately, so this is a
    true per-object count. Nothing is flushed (closures never run)."""
    pal = biome.palette_for_phase(phase)
    _zbuf.reset()
    _prom.draw_promenade(surf, scroll, pal, phase, t)
    far = sum(1 for e in _zbuf._QUEUE if e[0] <= config.GROUND_Y)
    _near.draw_near_lane(surf, scroll, pal, phase, t)
    total = len(_zbuf._QUEUE)
    _zbuf.reset()
    return far, total - far


def _segments(pillars, mask):
    """Contiguous [x0, x1] pillar runs where mask[i] is True."""
    segs = []
    start = None
    for i, m in enumerate(mask):
        if m and start is None:
            start = pillars[i]
        elif not m and start is not None:
            segs.append((start, pillars[i]))
            start = None
    if start is not None:
        segs.append((start, pillars[-1]))
    return segs


def main() -> None:
    out_dir = os.path.join(ROOT, "docs", "screenshots")
    os.makedirs(out_dir, exist_ok=True)

    time_for_pillar = build_time_for_pillar(800)
    scroll_for_pillar = build_scroll_for_pillar(800)

    def pillar_for_time(tt: float) -> float:
        i = bisect.bisect_left(time_for_pillar, tt)
        if i <= 0:
            return 0.0
        if i >= len(time_for_pillar):
            return float(len(time_for_pillar) - 1)
        t0, t1 = time_for_pillar[i - 1], time_for_pillar[i]
        if t1 == t0:
            return float(i - 1)
        return (i - 1) + (tt - t0) / (t1 - t0)

    max_pillars = int(round(pillar_for_time(CYCLE))) + 1
    t_max = CYCLE

    # Genie milestone (may sit in cycle 1 directly).
    t_at_genie = time_for_pillar[GENIE_PILLAR]
    genie_equiv_pillar = pillar_for_time(t_at_genie % CYCLE)
    genie_cycle = int(t_at_genie // CYCLE) + 1

    # ── fine timeline sampling (one cycle) ───────────────────────────────────
    ts = [i * t_max / (N - 1) for i in range(N)]
    pillars = [pillar_for_time(t) for t in ts]
    phases = [biome.phase_for_time(t) for t in ts]

    # Genuine lagged wet/snow accumulators: step a real Weather over the cycle.
    wx = weather.Weather()
    wet_arr, snow_arr = [], []
    prev_t = 0.0
    for i, t in enumerate(ts):
        dt = max(1e-3, t - prev_t)
        prev_t = t
        wx.update(dt, phases[i])
        wet_arr.append(wx.wetness)
        snow_arr.append(wx.snow_cover)

    # ── object-count measurement (per pillar, averaged over scroll offsets) ──
    surf = pygame.Surface((config.W, config.H))
    # Average the count over many sub-pillar scroll offsets so the per-slot-hash
    # quantisation smooths into the EXPECTED on-screen object count at each pillar.
    OFFSETS = [i / 12.0 for i in range(12)]   # fractions of a spacing
    obj_pillars = list(range(0, max_pillars + 1))
    far_counts, near_counts = [], []
    for p in obj_pillars:
        t = time_for_pillar[p]
        ph = biome.phase_for_time(t)
        base_scroll = scroll_for_pillar[p]
        step = (scroll_for_pillar[min(p + 1, len(scroll_for_pillar) - 1)]
                - base_scroll) or config.PIPE_SPACING
        fs = ns = 0.0
        for off in OFFSETS:
            f, n = _measure_sidewalk(surf, ph, t, base_scroll + off * step)
            fs += f
            ns += n
        far_counts.append(fs / len(OFFSETS))
        near_counts.append(ns / len(OFFSETS))

    # ── figure ───────────────────────────────────────────────────────────────
    fig, (ax_sky, ax_w, ax_arc, ax_state, ax_obj) = plt.subplots(
        5, 1, figsize=(15, 13.5), dpi=120,
        gridspec_kw=dict(height_ratios=[0.7, 5, 3.2, 3.4, 4.2], hspace=0.12),
        sharex=True,
    )

    # 1 ── biome sky strip ────────────────────────────────────────────────────
    for i in range(N - 1):
        col = _hex(biome.palette_for_time(ts[i])["sky_mid"])
        ax_sky.axvspan(pillars[i], pillars[i + 1], color=col, linewidth=0)
    ax_sky.set_yticks([])
    ax_sky.set_ylabel("sky", rotation=0, ha="right", va="center", fontsize=9)
    for phase, label in PHASE_LABELS:
        t = phase * CYCLE
        if t > t_max:
            continue
        p = pillar_for_time(t)
        ax_sky.axvline(p, color="white", alpha=0.55, linewidth=1.0)
        ax_sky.text(p + 1.5, 0.5, label, color="white", fontsize=7,
                    va="center", ha="left", fontweight="bold")
    ax_sky.set_title(
        f"Skybit — game schedule vs pillars passed  "
        f"(1 biome cycle = {CYCLE:.0f}s ≈ {max_pillars} pillars incl. newbie ramp; "
        f"all tracks computed from the live game code)",
        fontsize=13, pad=10)

    # 2 ── weather events ─────────────────────────────────────────────────────
    win_start = None
    legend_added = False
    in_window = False
    for i, p in enumerate(phases):
        active = weather.lightning_active(p)
        if active and not in_window:
            win_start = pillars[i]; in_window = True
        elif not active and in_window:
            ax_w.axvspan(win_start, pillars[i], color="#f2d94e", alpha=0.30,
                         linewidth=0,
                         label=("Lightning / thunder window" if not legend_added else None))
            legend_added = True; in_window = False
    if in_window:
        ax_w.axvspan(win_start, pillars[-1], color="#f2d94e", alpha=0.30,
                     linewidth=0,
                     label=("Lightning / thunder window" if not legend_added else None))
    for label, fn, color in CURVES:
        ys = [fn(p) for p in phases]
        ax_w.plot(pillars, ys, color=color, linewidth=2.0, label=label)
        ax_w.fill_between(pillars, ys, color=color, alpha=0.10)
    # newbie ramp band
    ax_w.axvspan(0, config.PLATEAU_PIPES, color="#3ca34d", alpha=0.22, linewidth=0,
                 label="Newbie plateau / ramp", zorder=0)
    ax_w.axvspan(config.PLATEAU_PIPES, config.RAMP_PIPES, color="#3ca34d",
                 alpha=0.10, linewidth=0, zorder=0)
    ax_w.annotate(f"ramp settles\n@ p{config.RAMP_PIPES}", (config.RAMP_PIPES, 0.94),
                  textcoords="offset points", xytext=(3, 0), ha="left", va="top",
                  fontsize=7.5, color="#1f6e2b", fontweight="bold")
    # rain/snow pillar anchors
    for pil, col, name in ((config.RAIN_START_PILLAR, "#2f6fb0", "rain start"),
                           (config.SNOW_START_PILLAR, "#8a6fc0", "snow start")):
        ax_w.axvline(pil, color=col, linewidth=1.2, linestyle=":", alpha=0.8)
        ax_w.annotate(f"{name}\n@ p{pil}", (pil, 0.0), textcoords="offset points",
                      xytext=(2, 2), ha="left", va="bottom", fontsize=7, color=col)
    # genie milestone
    ax_w.axvline(genie_equiv_pillar, color="#d12f2f", linewidth=2.0, alpha=0.85, zorder=4)
    glabel = (f"GENIE @ p{GENIE_PILLAR}" if genie_cycle == 1
              else f"GENIE @ p{GENIE_PILLAR} (cyc {genie_cycle})")
    ax_w.annotate(glabel, (genie_equiv_pillar, 1.02), textcoords="offset points",
                  xytext=(0, 2), ha="center", fontsize=9, fontweight="bold", color="#d12f2f")
    # FULL-DAY-COMPLETION event: cycle finale at the wrap (last RUSH pillars).
    fin0 = max_pillars - config.CYCLE_FINALE_RUSH_PILLARS
    ax_w.axvspan(fin0, max_pillars, color="#d4af37", alpha=0.35, linewidth=0,
                 label="Day complete: coin rush + treasure box")
    ax_w.annotate(f"DAY COMPLETE\ntreasure +{config.TREASURE_BOX_GRANT}\n"
                  f"{config.CYCLE_FINALE_RUSH_PILLARS}-pillar coin rush",
                  (max_pillars, 0.6), textcoords="offset points", xytext=(-4, 0),
                  ha="right", va="center", fontsize=7.5, color="#9a7b1f",
                  fontweight="bold")
    ax_w.set_ylim(0, 1.08)
    ax_w.set_ylabel("event intensity (0–1)")
    ax_w.grid(True, axis="y", alpha=0.25)
    ax_w.legend(loc="upper center", bbox_to_anchor=(0.5, -0.04), ncol=4,
                framealpha=0.92, fontsize=8.5)

    # 3 ── sidewalk crowd / day-arc ───────────────────────────────────────────
    for a, b, label, col in ROSTER_BANDS:
        pa, pb = pillar_for_time(a * CYCLE), pillar_for_time(b * CYCLE)
        ax_arc.axvspan(pa, pb, color=col, alpha=0.28, linewidth=0)
        ax_arc.text((pa + pb) / 2, 1.02, label, ha="center", va="bottom",
                    fontsize=7.5, fontweight="bold", color="#333333")
    pop = [_prom._population(p) for p in phases]
    eff = [_prom._population(p) * _prom._weather_crowd_factor(p) for p in phases]
    ax_arc.plot(pillars, pop, color="#777777", linewidth=1.4, linestyle="--",
                label="crowd density (time-of-day)")
    ax_arc.plot(pillars, eff, color="#1f6e2b", linewidth=2.4,
                label="effective density (× weather thinning)")
    ax_arc.fill_between(pillars, eff, color="#1f6e2b", alpha=0.12)
    ax_arc.set_ylim(0, 1.05)
    ax_arc.set_ylabel("sidewalk\ncrowd density")
    ax_arc.grid(True, axis="y", alpha=0.25)
    ax_arc.legend(loc="upper right", fontsize=8, framealpha=0.92)

    # 4 ── sidewalk state rows (dressing + weather-reactive) ──────────────────
    rain = [weather.rain_intensity(p) for p in phases]
    storm = [weather.storm_intensity(p) for p in phases]
    ROWS = [
        ("Prayer-flag bunting", [(p >= 0.85 or p < 0.28) for p in phases], "#c25b4e"),
        ("Lantern garland",     [0.20 <= p < 0.92 for p in phases],        "#d68a2e"),
        ("Lamp posts",          [0.20 <= p < 0.93 for p in phases],        "#caa24a"),
        ("Fairy lights",        [0.40 <= p < 0.86 for p in phases],        "#e6c98a"),
        ("Banners + braziers",  [0.45 <= p < 0.86 for p in phases],        "#b07a3a"),
        ("Wet paving + puddles", [w > 0.05 for w in wet_arr],              "#2f6fb0"),
        ("Umbrellas up",        [(rain[i] >= config.WEATHER_UMBRELLA_RAIN_AT
                                  or storm[i] >= 0.35) for i in range(N)],  "#3a7fd0"),
        ("Shelter figures",     [max(rain[i], storm[i]) >= 0.45 for i in range(N)], "#6a5acd"),
        ("Snow dusting",        [s > 0.02 for s in snow_arr],              "#8a6fc0"),
    ]
    labels = [r[0] for r in ROWS]
    for idx, (label, mask, col) in enumerate(ROWS):
        y = len(ROWS) - 1 - idx
        for x0, x1 in _segments(pillars, mask):
            ax_state.broken_barh([(x0, max(0.4, x1 - x0))], (y + 0.12, 0.76),
                                 facecolors=col, edgecolor="none", alpha=0.85)
    ax_state.set_yticks([len(ROWS) - 1 - i + 0.5 for i in range(len(ROWS))])
    ax_state.set_yticklabels(labels, fontsize=8)
    ax_state.set_ylim(0, len(ROWS))
    ax_state.set_ylabel("sidewalk\nstate")
    ax_state.grid(True, axis="x", alpha=0.2)

    # 5 ── object count (measured, far + near stacked) ────────────────────────
    far0 = far_counts
    tot = [far_counts[i] + near_counts[i] for i in range(len(far_counts))]
    ax_obj.fill_between(obj_pillars, 0, far0, color="#caa24a", alpha=0.85,
                        label="far lane (props + cast)")
    ax_obj.fill_between(obj_pillars, far0, tot, color="#2f7d4f", alpha=0.85,
                        label="near lane (props + cast)")
    ax_obj.plot(obj_pillars, tot, color="#222222", linewidth=1.2, label="total")
    ax_obj.set_ylim(0, max(tot) * 1.18 + 1)
    ax_obj.set_ylabel("sidewalk objects\non screen")
    ax_obj.set_xlabel("pillars passed within one biome cycle (= player's in-cycle score)")
    ax_obj.grid(True, axis="y", alpha=0.25)
    ax_obj.legend(loc="upper left", fontsize=8, framealpha=0.92, ncol=3)

    # shared x scale + ticks
    ax_obj.set_xlim(0, max_pillars)
    xticks = list(range(0, max_pillars + 1, 20))
    for extra in (config.RAIN_START_PILLAR, config.SNOW_START_PILLAR):
        if extra not in xticks:
            xticks.append(extra)
    xticks.sort()
    ax_obj.set_xticks(xticks)

    fig.tight_layout()
    out_path = os.path.join(out_dir, "biome_event_timeline_by_pillars.png")
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {out_path}")

    # ── sanity checks ─────────────────────────────────────────────────────────
    p_25 = pillar_for_time(time_for_pillar[25])
    print(f"sanity: pillar_for_time(t at 25) = {p_25:.3f} (expected ~25)")
    # rain peaks near RAIN_START_PILLAR, snow near SNOW_START_PILLAR
    rain_peak_i = max(range(N), key=lambda i: rain[i])
    snow_peak_i = max(range(N), key=lambda i: storm[i])
    print(f"rain peak @ pillar {pillars[rain_peak_i]:.0f} "
          f"(anchor RAIN_START_PILLAR={config.RAIN_START_PILLAR})")
    print(f"snow peak @ pillar {pillars[snow_peak_i]:.0f} "
          f"(anchor SNOW_START_PILLAR={config.SNOW_START_PILLAR})")
    print(f"1 biome cycle = {max_pillars} pillars (incl. newbie ramp)")


if __name__ == "__main__":
    main()
