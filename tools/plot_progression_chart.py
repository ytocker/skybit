"""Run-progression cheatsheet — pillars × biome × weather × power-ups.

Output: ``docs/progression/run_progression.png``. Sister tool to
``tools/plot_biome_timeline_by_pillars.py`` — same time-for-pillar
math, same biome-strip-on-top + weather-curves-on-bottom layout, same
matplotlib idiom — extended with:

  * a teal UMBRELLA spawn band shaded over every pillar range where
    rain intensity ≥ ``UMBRELLA_SPAWN_RAIN`` (the umbrella spawns once
    per storm while raining — RAIN-tied, not pillar-tied)
  * the production GENIE one-shot marker at pillar
    ``weather.GENIE_PILLAR`` (anchored to the geyser event)
  * the cycle-finale celebration band at the right edge — chest +
    day-complete banner + parrot crowd + bunting + balloons fire when
    ``biome_phase`` wraps past ``CYCLE_FINALE_PHASE_HI``
  * a first-geyser marker — the 9th pillar where thermal intensity
    crosses ``ROCK_SPAWN_THRESHOLD`` (= the 8-pillar rocks-only
    telegraph followed by the guaranteed first geyser)
  * a row of thin grey ticks at the bottom marking pillar-score gates
    (``POWERUP_SCORE_GATES`` + ``POWERUP_REPLACED_AT``) so the rail /
    grow / lottery / megamagnet milestones land in context.

Run from the repo root:

    python tools/plot_progression_chart.py
"""
from __future__ import annotations

import bisect
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from game import biome, weather, config

CYCLE = biome.CYCLE_SECONDS
N = 1800                                         # sample resolution
GENIE_PILLAR = weather.GENIE_PILLAR
# UMBRELLA spawn pillars (the umbrella fires at exactly these scored
# pillars; see config.UMBRELLA_SPAWN_PILLARS).

# Match the canopy palette of the in-game umbrella so the spawn band is
# obviously the umbrella's window (and not just "another weather thing").
UMBRELLA_BAND = "#54B9C4"

# Lightning fires in-game from the inline `storming` gate in
# Weather.update, which reads the module-level constants
# `weather.LIGHTNING_PHASE_MIN/MAX`. Those constants are derived from
# config.RAIN_START_PILLAR via the shared dwell formula, so the chart
# auto-tracks any shift of the rain block — no separate literals here.
def _lightning_active_real(phase: float) -> bool:
    """Wraps the in-game lightning gate so the chart stays in sync with
    Weather.update no matter how the rain block is anchored."""
    return weather.LIGHTNING_PHASE_MIN <= phase <= weather.LIGHTNING_PHASE_MAX

PHASE_LABELS = [
    (0.00000, "DAY"),
    (0.23125, "GOLDEN\nHOUR"),
    (0.36250, "SUNSET"),
    (0.51250, "DUSK"),
    (0.64375, "NIGHT"),
    (0.79375, "PREDAWN"),
    (0.90625, "SUNRISE"),
]


def _hex(rgb):
    return "#%02x%02x%02x" % tuple(int(c) for c in rgb[:3])


# Only curves that are actually consumed by live gameplay code. The
# `_mist_intensity` sketch from the reference plotter is dropped here
# because no in-game system reads it — the chart is meant to mirror
# what really happens in a run.
CURVES = [
    ("Morning thermal (geysers)",     weather.thermal_intensity, "#e0663a"),
    ("Calm breeze (leaves)",          weather.calm_breeze,       "#d68a2e"),
    ("Rain",                          weather.rain_intensity,    "#2f6fb0"),
    ("Snow squall (tailwind)",        weather.storm_intensity,   "#8a6fc0"),
]


def build_time_for_pillar(max_pillars: int) -> list:
    """Cumulative wall-clock seconds to reach each pillar, mirroring what
    the live game does. Pillar 1 is special: it's seeded at
    `W + 60 + SPAWN_GRACE * SCROLL_BASE` and has to scroll all the way
    to `BIRD_X − PIPE_W` before scoring fires (~1.14 s longer than a
    normal inter-pillar dwell). Pillars 2..N use the inter-pillar dwell
    `(spacing + 60) / scroll` with `_ramp_t()` evaluated at the score
    just after the previous pillar — same indexing the World uses. The
    +60 is the W+60 spawn-clamp at world.py:~1528 — every new pipe
    lands at `max(prev.x + spacing, W+60)`, and the clamp ALWAYS fires
    (spawn trigger fires when prev.x < W - spacing, so prev.x + spacing
    < W < W + 60). Effective inter-pillar world-x gap = spacing + 60."""
    seeded_x = config.W + 60 + int(config.SPAWN_GRACE * config.SCROLL_BASE)
    travel = seeded_x - config.BIRD_X - config.PIPE_W
    T = [0.0, travel / config.SCROLL_NEWBIE_BASE]
    for pp in range(1, max_pillars):
        if pp < config.PLATEAU_PIPES:
            t = 0.0
        else:
            denom = max(1, config.RAMP_PIPES - config.PLATEAU_PIPES)
            x = min(1.0, (pp - config.PLATEAU_PIPES) / denom)
            t = 1.0 - (1.0 - x) ** 2
        spacing = (config.PIPE_SPACING_NEWBIE
                   + (config.PIPE_SPACING - config.PIPE_SPACING_NEWBIE) * t)
        scroll = (config.SCROLL_NEWBIE_BASE
                  + (config.SCROLL_BASE - config.SCROLL_NEWBIE_BASE) * t)
        T.append(T[-1] + (spacing + 60) / scroll)
    return T


def main() -> None:
    out_dir = os.path.join(ROOT, "docs", "progression")
    os.makedirs(out_dir, exist_ok=True)

    time_for_pillar = build_time_for_pillar(800)

    def pillar_for_time(t: float) -> float:
        i = bisect.bisect_left(time_for_pillar, t)
        if i <= 0:
            return 0.0
        if i >= len(time_for_pillar):
            return float(len(time_for_pillar) - 1)
        t0, t1 = time_for_pillar[i - 1], time_for_pillar[i]
        if t1 == t0:
            return float(i - 1)
        return (i - 1) + (t - t0) / (t1 - t0)

    max_pillars = int(round(pillar_for_time(CYCLE))) + 1
    t_max = CYCLE

    t_at_genie = time_for_pillar[GENIE_PILLAR]
    genie_phase_t = t_at_genie % CYCLE
    genie_equiv_pillar = pillar_for_time(genie_phase_t)
    genie_cycle = int(t_at_genie // CYCLE) + 1

    ts = [i * t_max / (N - 1) for i in range(N)]
    pillars = [pillar_for_time(t) for t in ts]
    phases = [biome.phase_for_time(t) for t in ts]

    fig, (ax_sky, ax) = plt.subplots(
        2, 1, figsize=(15, 7.4), dpi=130,
        gridspec_kw=dict(height_ratios=[1, 6], hspace=0.10),
        sharex=True,
    )

    # ── top strip: sky colour (biome conditions) vs pillars ─────────────
    for i in range(N - 1):
        col = _hex(biome.palette_for_time(ts[i])["sky_mid"])
        ax_sky.axvspan(pillars[i], pillars[i + 1], color=col, linewidth=0)
    ax_sky.set_yticks([])
    ax_sky.set_ylabel("biome", rotation=0, ha="right", va="center",
                       fontsize=9)

    for phase, label in PHASE_LABELS:
        t = phase * CYCLE
        if t > t_max:
            continue
        p = pillar_for_time(t)
        ax_sky.axvline(p, color="white", alpha=0.55, linewidth=1.0)
        ax_sky.text(p + 1.5, 0.5, label, color="white", fontsize=7.5,
                    va="center", ha="left", fontweight="bold")

    ax_sky.set_title(
        f"Skybit — run progression: biome + weather + power-up "
        f"milestones + cycle-finale celebration vs pillars passed   "
        f"(1 biome cycle = {CYCLE:.0f} s ≈ {max_pillars} pillars "
        f"including the newbie ramp)",
        fontsize=12, pad=8)

    # ── bottom panel: weather curves vs pillars ─────────────────────────
    # Lightning windows (yellow shading) — uses the REAL in-game gate
    # (0.49..0.58) from Weather.update, not the stale lightning_active()
    # helper. This overlaps the rain peak at 0.50, so the band correctly
    # falls on top of the rain crest.
    in_window = False
    win_start = None
    legend_lightning = False
    for i, p in enumerate(phases):
        active = _lightning_active_real(p)
        if active and not in_window:
            win_start = pillars[i]
            in_window = True
        elif not active and in_window:
            ax.axvspan(win_start, pillars[i], color="#f2d94e", alpha=0.30,
                       linewidth=0,
                       label=("Lightning / thunder window (in-game gate)"
                              if not legend_lightning else None))
            legend_lightning = True
            in_window = False
    if in_window:
        ax.axvspan(win_start, pillars[-1], color="#f2d94e", alpha=0.30,
                   linewidth=0,
                   label=("Lightning / thunder window (in-game gate)"
                          if not legend_lightning else None))

    # UMBRELLA spawn band — every pillar range where rain ≥ threshold is
    # spawned at the exact pillars in config.UMBRELLA_SPAWN_PILLARS,
    # which the game fires from the scoring path. Both pillars sit
    # inside the dusk rain block by design.
    for idx, up in enumerate(config.UMBRELLA_SPAWN_PILLARS):
        ax.axvline(up, color=UMBRELLA_BAND, linewidth=2.0,
                   alpha=0.85, linestyle="--", zorder=4,
                   label=("UMBRELLA spawn (fixed pillars)"
                          if idx == 0 else None))
        ax.annotate(f"UMB\np{up}", (up, 0.86),
                    textcoords="offset points", xytext=(0, 2),
                    ha="center", fontsize=8, fontweight="bold",
                    color="#1a8f9a")

    for label, fn, color in CURVES:
        ys = [fn(p) for p in phases]
        ax.plot(pillars, ys, color=color, linewidth=2.0, label=label,
                zorder=3)
        ax.fill_between(pillars, ys, color=color, alpha=0.10, zorder=2)

    # ── Genie milestone marker ─────────────────────────────────────────
    ax.axvline(genie_equiv_pillar, color="#d12f2f", linewidth=2.3,
               alpha=0.9, linestyle="-", zorder=4)
    if genie_cycle == 1:
        gen_label = f"GENIE LAMP @ p{GENIE_PILLAR}"
    else:
        gen_label = (f"GENIE LAMP @ p{GENIE_PILLAR} (cycle {genie_cycle})\n"
                     f"phase ≡ p{int(round(genie_equiv_pillar))} in cycle 1")
    ax.annotate(gen_label, (genie_equiv_pillar, 1.02),
                textcoords="offset points", xytext=(0, 2),
                ha="center", fontsize=9.5,
                fontweight="bold", color="#d12f2f")

    # ── Newbie ramp band ───────────────────────────────────────────────
    ax.axvspan(0, config.PLATEAU_PIPES, color="#3ca34d", alpha=0.22,
               linewidth=0, label="Newbie plateau / ramp", zorder=0)
    ax.axvspan(config.PLATEAU_PIPES, config.RAMP_PIPES, color="#3ca34d",
               alpha=0.10, linewidth=0, zorder=0)
    ax.annotate(f"ramp settles\n@ pillar {config.RAMP_PIPES}",
                (config.RAMP_PIPES, 0.94),
                textcoords="offset points", xytext=(3, 0),
                ha="left", va="top", fontsize=7.5, color="#1f6e2b",
                fontweight="bold")

    # ── Storm peak marker ──────────────────────────────────────────────
    # Read the peak phase from the live weather module so the marker
    # tracks the shifted rain block automatically.
    storm_peak_phase = weather.RAIN_STORM_PEAK
    p_storm = pillar_for_time(storm_peak_phase * CYCLE)
    y_storm = weather.rain_intensity(storm_peak_phase)
    ax.plot([p_storm], [y_storm], marker="v", color="#2f6fb0", markersize=9,
            markeredgecolor="white", markeredgewidth=0.8, zorder=5)
    ax.annotate(f"storm peak\n@ p{int(p_storm)}", (p_storm, y_storm),
                textcoords="offset points", xytext=(0, 9),
                ha="center", fontsize=7.5, color="#2f6fb0",
                fontweight="bold")

    # ── First geyser marker ────────────────────────────────────────────
    # Geysers don't fire until 8 pillars of thermal warm-up rocks have
    # telegraphed the event (GEYSER_RAMP_PILLARS). Walk the pillar
    # samples in order, counting how many cross ROCK_SPAWN_THRESHOLD;
    # the (GEYSER_RAMP_PILLARS+1)th carries the forced first geyser.
    rock_threshold = config.ROCK_SPAWN_THRESHOLD
    ramp_target = config.GEYSER_RAMP_PILLARS + 1
    thermal_pillars = 0
    first_geyser_pillar = None
    for k in range(max_pillars):
        phase_k = biome.phase_for_time(time_for_pillar[k] % CYCLE)
        if weather.thermal_intensity(phase_k) > rock_threshold:
            thermal_pillars += 1
            if thermal_pillars >= ramp_target:
                first_geyser_pillar = k
                break
    if first_geyser_pillar is not None:
        ax.plot([first_geyser_pillar], [0.0], marker="D",
                color="#e0663a", markersize=9, markeredgecolor="white",
                markeredgewidth=0.8, zorder=5,
                label="First geyser (after 8-pillar rocks ramp)")
        ax.annotate(f"first geyser\n@ p{first_geyser_pillar}",
                    (first_geyser_pillar, 0.0),
                    textcoords="offset points", xytext=(0, 12),
                    ha="center", fontsize=7.5, color="#e0663a",
                    fontweight="bold")

    # ── Cycle-finale celebration band ──────────────────────────────────
    # The day/night phase climbs past CYCLE_FINALE_PHASE_HI = 0.95 and
    # rolls through ~1.0 → ~0.0; the wrap fires inside world.update,
    # spawning the chest + day-complete banner + parrot crowd + bunting
    # + balloon cluster. Find the first pillar whose phase is in the
    # HI..1.0 window — everything from there to the end of the chart
    # is the celebration tail.
    finale_hi = config.CYCLE_FINALE_PHASE_HI
    finale_pillar = None
    for k, p in enumerate(phases):
        if p > finale_hi:
            finale_pillar = pillars[k]
            break
    if finale_pillar is not None:
        ax.axvspan(finale_pillar, max_pillars, color="#f5c33b",
                   alpha=0.30, linewidth=0, zorder=1,
                   label="Cycle-finale celebration (chest + parrots + bunting)")
        ax.axvline(finale_pillar, color="#b8860b", linewidth=2.3,
                   alpha=0.9, zorder=4)
        ax.annotate("DAY COMPLETE\nchest + parrots + bunting",
                    (finale_pillar, 0.55),
                    textcoords="offset points", xytext=(4, 0),
                    ha="left", va="center", fontsize=8.5,
                    fontweight="bold", color="#8a5a00")

    # ── Power-up score gates (thin grey ticks at the bottom) ───────────
    gates = sorted({
        **{k: ("gate-in", v) for k, v in config.POWERUP_SCORE_GATES.items()},
        **{f"{k}→megamagnet": ("replaced", v)
           for k, v in config.POWERUP_REPLACED_AT.items()},
    }.items(), key=lambda kv: kv[1][1])
    for kind, (_why, gate) in gates:
        if gate > max_pillars - 1:
            continue
        ax.plot([gate], [0.0], marker="|", color="#666", markersize=14,
                markeredgewidth=1.6, zorder=4)
        ax.annotate(f"{kind}\np{gate}", (gate, 0.0),
                    textcoords="offset points", xytext=(0, -22),
                    ha="center", va="top", fontsize=7,
                    color="#555")

    ax.set_xlim(0, max_pillars)
    ax.set_ylim(0, 1.08)
    ax.set_xlabel("pillars passed within one biome cycle "
                  "(= player's in-cycle score)")
    ax.set_ylabel("event intensity (0–1)")
    ax.grid(True, axis="y", alpha=0.25)
    xticks = list(range(0, max_pillars + 1, 10))
    eq = int(round(genie_equiv_pillar))
    if eq not in xticks:
        xticks.append(eq)
        xticks.sort()
    ax.set_xticks(xticks)

    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels, loc="upper center",
              bbox_to_anchor=(0.5, -0.18), ncol=3, framealpha=0.92,
              fontsize=9)
    # Honest footer about residual pillar-vs-phase variance: the chart's
    # math now matches the live game in normal play (and under slowmo, since
    # biome_time scales with the world). The only remaining variance comes
    # from boosts that scale scroll without scaling sdt (rail / skateboard
    # slide / snow tailwind) — they pass pillars faster than biome ticks, so
    # weather events land at LATER pillars during sustained boosts.
    fig.text(0.5, -0.035,
             "Pillar↔phase is exact for normal play and slowmo. "
             "Rail / skateboard / snow tailwind boost scroll without "
             "scaling the biome clock, so weather may land 1–3 pillars "
             "LATER than shown while those buffs are sustained.",
             ha="center", va="top", fontsize=8.5, color="#666",
             style="italic")

    fig.tight_layout()
    out_path = os.path.join(out_dir, "run_progression.png")
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {out_path}")
    print(f"1 biome cycle = {max_pillars} pillars (incl. newbie ramp)")
    print(f"genie @ p{GENIE_PILLAR} -> cycle {genie_cycle}, "
          f"phase equiv. to pillar {int(round(genie_equiv_pillar))} "
          f"in cycle 1")
    print(f"umbrella spawn pillars = {tuple(config.UMBRELLA_SPAWN_PILLARS)}")


if __name__ == "__main__":
    main()
