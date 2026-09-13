"""BEFORE/AFTER content-map on ONE shared pillar axis.

Renders the original pre-clown-event timeline (top) and the current one (bottom)
as stacked subplots that SHARE a single x-axis, so the same pagoda number sits at
the same column in both — the shift the clown event caused (rain 70→100, snow
139→169, day ≈186→≈207, clown inserted ~65) reads straight down a vertical line.

The OLD curves are produced in-process: the weather intensity fns are pure
functions of phase + a few import-time shift constants derived from
RAIN_START_PILLAR / SNOW_START_PILLAR / CYCLE_SECONDS, and biome palettes are
unchanged (only keyframe fractions were remapped, gated on DAY_EXTRA_SECONDS). So
we override those config knobs to their pre-event values, reload biome+weather,
gather the OLD panel data, then restore and reload for the CURRENT panel.

    python tools/plot_timeline_before_after.py
"""
from __future__ import annotations

import importlib
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from game import config
import game.biome
import game.weather

# Pre-clown-event values (commit 18089a1f).
OLD_RAIN_PILLAR = 70
OLD_SNOW_PILLAR = 139
# Pre-clown umbrella offsets relative to the rain start (the historical
# placement the BEFORE panel snapshots); the AFTER panel reads live config.
OLD_UMBRELLA_OFFSETS = (5, 17)

CURVES = [
    ("Morning thermal (geysers)", "thermal_intensity", "#e0663a"),
    ("Rain / thunderstorm", "rain_intensity", "#2f6fb0"),
    ("Snow squall (tailwind)", "storm_intensity", "#8a6fc0"),
]
PHASE_NAME_NL = {"GOLDEN HOUR": "GOLDEN\nHOUR"}


def _hex(rgb):
    return "#%02x%02x%02x" % tuple(int(c) for c in rgb[:3])


def _pillar_for_phase(phase, phases):
    for p in range(1, len(phases)):
        if phases[p] >= phase:
            lo, hi = phases[p - 1], phases[p]
            f = (phase - lo) / (hi - lo) if hi > lo else 0.0
            return (p - 1) + f
    return float(len(phases) - 1)


def _gather(biome, weather, umbrellas):
    """Collect everything needed to draw one panel from the CURRENTLY-loaded
    biome/weather modules into a plain dict (decoupled from module state)."""
    pillars, phases, p, day_end = [0], [0.0], 1, None
    while True:
        ph = weather._phase_for_pillar(p)
        pillars.append(p)
        phases.append(ph)
        if day_end is None and ph >= 1.0:
            day_end = p
        if day_end is not None and p >= day_end + config.CYCLE_FINALE_RUSH_PILLARS + 2:
            break
        p += 1
        if p > 500:
            break
    fns = {name: getattr(weather, name) for _, name, _ in CURVES}
    rain_pillar = config.RAIN_START_PILLAR
    return dict(
        pillars=pillars, phases=phases, day_end=day_end,
        sky=[_hex(biome.palette_for_phase(ph)["sky_mid"]) for ph in phases],
        curves={name: [fns[name](ph) for ph in phases] for name in fns},
        lightning=[pillars[i] for i, ph in enumerate(phases)
                   if weather.LIGHTNING_PHASE_MIN <= ph <= weather.LIGHTNING_PHASE_MAX],
        bounds=[(_pillar_for_phase(f, phases), PHASE_NAME_NL.get(n, n))
                for f, n in biome.PHASE_BOUNDARIES],
        genie=weather.GENIE_PILLAR,
        umbrellas=list(umbrellas),
        rain_start=rain_pillar,
    )


def _draw_panel(ax_sky, ax, D, title, show_clown, xmax):
    pillars = D["pillars"]
    # sky strip
    for i in range(len(pillars) - 1):
        ax_sky.axvspan(pillars[i], pillars[i + 1], color=D["sky"][i], linewidth=0)
    ax_sky.set_yticks([])
    ax_sky.set_ylabel("sky", rotation=0, ha="right", va="center", fontsize=8)
    for x, name in D["bounds"]:
        ax_sky.axvline(x, color="white", alpha=0.55, linewidth=1)
        ax_sky.text(x + 1, 0.5, name, color="white", fontsize=6.5,
                    va="center", ha="left", fontweight="bold")
    ax_sky.set_title(title, fontsize=11, pad=5, loc="left")

    # lightning window
    if D["lightning"]:
        ax.axvspan(min(D["lightning"]), max(D["lightning"]), color="#f2d94e",
                   alpha=0.30, linewidth=0, label="Lightning / thunder")
    # weather curves + peak markers
    for label, name, color in CURVES:
        ys = D["curves"][name]
        ax.plot(pillars, ys, color=color, linewidth=2.2, label=label)
        ax.fill_between(pillars, ys, color=color, alpha=0.12)
        pk = max(range(len(ys)), key=lambda i: ys[i])
        ax.plot([pillars[pk]], [ys[pk]], marker="v", color=color, markersize=8,
                markeredgecolor="white", markeredgewidth=0.7, zorder=5)
        ax.annotate(f"{pillars[pk]}", (pillars[pk], ys[pk]),
                    textcoords="offset points", xytext=(0, 8), ha="center",
                    fontsize=7.5, color=color, fontweight="bold")
    # newbie band
    ax.axvspan(0, config.PLATEAU_PIPES, color="#3ca34d", alpha=0.22, linewidth=0,
               label="Newbie plateau / ramp", zorder=0)
    ax.axvspan(config.PLATEAU_PIPES, config.RAMP_PIPES, color="#3ca34d",
               alpha=0.11, linewidth=0, zorder=0)
    # end-of-day finale
    de = D["day_end"]
    ax.axvspan(de, de + config.CYCLE_FINALE_RUSH_PILLARS, color="#caa23a",
               alpha=0.30, linewidth=0, label="End of day — finale")
    ax.axvline(de, color="#8a6b1f", linewidth=2)
    ax.annotate(f"END OF DAY\n@ {de}", (de, 0.5), textcoords="offset points",
                xytext=(6, 0), rotation=90, fontsize=7.5, fontweight="bold",
                color="#6b520f", va="center", ha="left")
    # power-up anchors
    for label, xs, color, mk in (("Genie", [D["genie"]], "#b83dba", "D"),
                                 ("Umbrella", D["umbrellas"], "#0f9090", "P")):
        for j, x in enumerate(xs):
            ax.axvline(x, color=color, linestyle=(0, (4, 3)), linewidth=1.4,
                       alpha=0.85, zorder=4)
            ax.plot([x], [1.04], marker=mk, color=color, markersize=9,
                    markeredgecolor="white", markeredgewidth=0.7, clip_on=False,
                    zorder=6, label=(label if j == 0 else None))
    # clown (AFTER only)
    if show_clown:
        c0 = config.CLOWN_START_PILLAR
        c1 = c0 + config.CLOWN_SLOT_PILLARS
        ax.axvspan(c0, c1, color="#c1121f", alpha=0.16, linewidth=0,
                   label="Clown event → warren gauntlet")
        ax.axvspan(c1, config.RAIN_START_PILLAR, color="#c1121f", alpha=0.06,
                   linewidth=0)
        ax.axvline(c0, color="#c1121f", linewidth=2.2, zorder=4)
        ax.annotate(f"CLOWN ~{c0}\ndie roll → gauntlet", (c0, 0.5),
                    textcoords="offset points", xytext=(6, 0), rotation=90,
                    fontsize=7, fontweight="bold", color="#8a0d17",
                    va="center", ha="left", zorder=7)

    ax.set_xlim(0, xmax)
    ax.set_ylim(0, 1.10)
    ax.set_ylabel("intensity (0–1)", fontsize=8)
    ax.grid(True, axis="y", alpha=0.22)
    ax.grid(True, axis="x", alpha=0.30, linestyle=":")
    ax.set_xticks(range(0, int(xmax) + 1, 10))


def main():
    out_dir = os.path.join(ROOT, "docs", "screenshots")
    os.makedirs(out_dir, exist_ok=True)

    orig = (config.RAIN_START_PILLAR, config.SNOW_START_PILLAR,
            config.DAY_EXTRA_SECONDS)

    # OLD pass — pre-event knobs, reload so biome/weather recompute.
    config.RAIN_START_PILLAR = OLD_RAIN_PILLAR
    config.SNOW_START_PILLAR = OLD_SNOW_PILLAR
    config.DAY_EXTRA_SECONDS = 0.0
    importlib.reload(game.biome)
    importlib.reload(game.weather)
    D_old = _gather(game.biome, game.weather,
                    [OLD_RAIN_PILLAR + o for o in OLD_UMBRELLA_OFFSETS])

    # CURRENT pass — restore, reload.
    config.RAIN_START_PILLAR, config.SNOW_START_PILLAR, config.DAY_EXTRA_SECONDS = orig
    importlib.reload(game.biome)
    importlib.reload(game.weather)
    D_new = _gather(game.biome, game.weather,
                    list(config.UMBRELLA_SPAWN_PILLARS))

    xmax = D_new["day_end"] + config.CYCLE_FINALE_RUSH_PILLARS + 4

    # 5-row grid with an empty SPACER row (index 2) between the BEFORE block
    # (sky+curves) and the AFTER block, so the BEFORE panel's x-axis labels have
    # dedicated room and never collide with the AFTER title/sky strip.
    fig = plt.figure(figsize=(14, 10), dpi=130)
    gs = fig.add_gridspec(5, 1, height_ratios=[1, 5, 1.1, 1, 5], hspace=0.16)
    axs_o = fig.add_subplot(gs[0])
    axc_o = fig.add_subplot(gs[1], sharex=axs_o)
    axs_n = fig.add_subplot(gs[3], sharex=axs_o)
    axc_n = fig.add_subplot(gs[4], sharex=axs_o)

    _draw_panel(axs_o, axc_o, D_old,
                f"BEFORE — pre-clown-event: 320 s day · rain @{OLD_RAIN_PILLAR} · "
                f"snow @{OLD_SNOW_PILLAR} · day ≈{D_old['day_end']} pagodas",
                show_clown=False, xmax=xmax)
    _draw_panel(axs_n, axc_n, D_new,
                f"AFTER — clown event added: day ≈{D_new['day_end']} · clown ~"
                f"{config.CLOWN_START_PILLAR} → gauntlet · rain @{D_new['rain_start']} · "
                f"snow @{config.SNOW_START_PILLAR}",
                show_clown=True, xmax=xmax)

    # Repeat the pagoda axis under the BEFORE panel too (sharex hides it by
    # default) so the scale is readable in the gap between the two graphs.
    axc_o.tick_params(axis="x", labelbottom=True)
    axc_o.set_xlabel("pagodas passed (pillars scored)", fontsize=8)
    axc_n.set_xlabel("pagodas passed (pillars scored) — SAME axis on both panels")
    for ax in (axc_o, axc_n):
        h, l = ax.get_legend_handles_labels()
        ax.legend(h, l, loc="upper right", ncol=2, framealpha=0.92, fontsize=7.5)

    fig.suptitle("Skybit timeline — BEFORE vs AFTER the clown event "
                 "(shared pagoda axis)", fontsize=13, y=0.995)
    fig.tight_layout(rect=(0, 0, 1, 0.99))
    out_path = os.path.join(out_dir, "timeline_before_after_aligned_v5.png")
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {out_path}")
    print(f"  BEFORE day_end = {D_old['day_end']}  rain_start = {D_old['rain_start']} "
          f"genie = {D_old['genie']} umbrellas = {D_old['umbrellas']}")
    print(f"  AFTER  day_end = {D_new['day_end']}  rain_start = {D_new['rain_start']} "
          f"genie = {D_new['genie']} umbrellas = {D_new['umbrellas']}")
    print(f"  shared xlim = [0, {xmax}]")


if __name__ == "__main__":
    main()
