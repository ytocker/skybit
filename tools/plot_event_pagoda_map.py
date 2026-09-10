"""Render the run's content map on a PAGODAS-PASSED axis under
``docs/screenshots/event_pagoda_map_clown_v6.png`` (now also showing the clown
event's clear-sky relief empties). Run from the repo root:

    python tools/plot_event_pagoda_map.py

Companion to ``plot_biome_timeline.py``: same biome + weather content, but
plotted against the pillars the player actually scores rather than wall-clock
seconds — the axis you reason about when deciding *where* in a run a new event
(here: the clown event) should slot in. Pillar→phase uses the authoritative
``weather._phase_for_pillar`` (the same dwell math the live game integrates,
including the first-pillar seeded travel and the onboarding ramp), so every
landmark lands on the real gameplay axis.

Shows the three GAMEPLAY weather events (morning-thermal geysers, rain /
thunderstorm, snow squall), the two fixed-pillar power-up pickups (the genie
lamp milestone + the rain umbrellas), the end-of-day treasure-box finale, and
the newbie plateau + ramp. Cosmetic-only phenomena (calm breeze, dawn mist) are
omitted.

``draw_map`` / ``compute_axis`` / ``phase_labels_for`` are factored out so other
tools (e.g. the before/after sky-timing comparison) can reuse the full map.
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

from game import biome, weather, config

# Biome named phase boundaries, read from the LIVE keyframes (via biome) so the
# labels/gridlines track the real day length — incl. the extended DAY + its
# solid-day hold absorbed for the clown event.
PHASE_LABELS = [(f, n.replace("GOLDEN HOUR", "GOLDEN\nHOUR"))
                for f, n in biome.PHASE_BOUNDARIES]

# The three gameplay weather events: (label, intensity-fn, colour).
CURVES = [
    ("Morning thermal (geysers)", weather.thermal_intensity, "#e0663a"),
    ("Rain / thunderstorm", weather.rain_intensity, "#2f6fb0"),
    ("Snow squall (tailwind)", weather.storm_intensity, "#8a6fc0"),
]


def _hex(rgb):
    return "#%02x%02x%02x" % tuple(int(c) for c in rgb[:3])


def phase_labels_for(keyframes, names):
    """Named phase boundaries (fraction, label) for a keyframe set — excludes
    the unnamed DAY-hold and the wrap, mirroring biome.PHASE_BOUNDARIES."""
    out = []
    for (frac, _), name in zip(keyframes, names):
        if name and 0.0 < frac < 1.0:
            out.append((frac, name.replace("GOLDEN HOUR", "GOLDEN\nHOUR")))
    return out


def compute_axis():
    """Walk pillars for one full day plus the finale rush. Pillar→phase is the
    live time-warp, independent of biome keyframe timing."""
    pillars, phases = [0], [0.0]
    p, day_end = 1, None
    while True:
        ph = weather._phase_for_pillar(p)
        pillars.append(p)
        phases.append(ph)
        if day_end is None and ph >= 1.0:
            day_end = p
        if day_end is not None and p >= day_end + config.CYCLE_FINALE_RUSH_PILLARS + 2:
            break
        p += 1
        if p > 400:  # safety net
            break
    return pillars, phases, day_end


def _pillar_for_phase(phase, phases):
    """First pillar index whose cumulative phase reaches `phase` (linear
    interp between the bracketing samples for a smooth label position)."""
    for p in range(1, len(phases)):
        if phases[p] >= phase:
            lo, hi = phases[p - 1], phases[p]
            frac = (phase - lo) / (hi - lo) if hi > lo else 0.0
            return (p - 1) + frac
    return float(len(phases) - 1)


def draw_map(ax_sky, ax, pillars, phases, day_end, phase_labels=None,
             sky_title=None, show_xlabel=True, show_legend=True):
    """Draw the sky banner (top) + the event/graph panel (bottom) onto the two
    provided axes, sampling sky colour from the LIVE biome keyframes."""
    if phase_labels is None:
        phase_labels = PHASE_LABELS

    # ── top strip: sky colour sampled from the real palette per pillar ───────
    for i in range(len(pillars) - 1):
        col = _hex(biome.palette_for_phase(phases[i])["sky_mid"])
        ax_sky.axvspan(pillars[i], pillars[i + 1], color=col, linewidth=0)
    ax_sky.set_yticks([])
    ax_sky.set_ylabel("sky", rotation=0, ha="right", va="center", fontsize=9)
    for phase, label in phase_labels:
        x = _pillar_for_phase(phase, phases)
        ax_sky.axvline(x, color="white", alpha=0.55, linewidth=1)
        ax_sky.text(x + 1, 0.5, label, color="white", fontsize=7.5,
                    va="center", ha="left", fontweight="bold")
    if sky_title is None:
        sky_title = (
            f"Skybit — game content map by pagodas passed  "
            f"(one full day ≈ {day_end} pagodas)   ·   live status; "
            f"pillars are nominal — live counts run slightly lower")
    ax_sky.set_title(sky_title, fontsize=12, pad=8)

    # ── lower panel: the three gameplay weather events vs pillar ─────────────
    # Lightning window (shaded) — a state, not an intensity curve.
    lt = [pillars[i] for i in range(len(pillars))
          if weather.lightning_active(phases[i])]
    if lt:
        ax.axvspan(min(lt), max(lt), color="#f2d94e", alpha=0.30, linewidth=0,
                   label="Lightning / thunder window")

    for label, fn, color in CURVES:
        ys = [fn(ph) for ph in phases]
        ax.plot(pillars, ys, color=color, linewidth=2.4, label=label)
        ax.fill_between(pillars, ys, color=color, alpha=0.12)
        # Peak marker annotated with its pillar number.
        pk_i = max(range(len(ys)), key=lambda i: ys[i])
        ax.plot([pillars[pk_i]], [ys[pk_i]], marker="v", color=color,
                markersize=9, markeredgecolor="white", markeredgewidth=0.8,
                zorder=5)
        ax.annotate(f"≈ pillar {pillars[pk_i]}", (pillars[pk_i], ys[pk_i]),
                    textcoords="offset points", xytext=(0, 10), ha="center",
                    fontsize=8, color=color, fontweight="bold")

    # Rain sub-peak labels (drizzle vs storm) at their anchored pillars.
    rx_drizzle = _pillar_for_phase(weather.RAIN_DRIZZLE_PEAK, phases)
    rx_storm = _pillar_for_phase(weather.RAIN_STORM_PEAK, phases)
    ax.annotate("drizzle",
                (rx_drizzle, weather.rain_intensity(weather.RAIN_DRIZZLE_PEAK)),
                textcoords="offset points", xytext=(-18, 26),
                ha="center", fontsize=7.5, color="#2f6fb0")
    ax.annotate("storm peak",
                (rx_storm, weather.rain_intensity(weather.RAIN_STORM_PEAK)),
                textcoords="offset points", xytext=(6, 26),
                ha="center", fontsize=7.5, color="#2f6fb0", fontweight="bold")

    # ── storm-jolt strike zone — the bolt that actually HITS Pip and docks
    # score (distinct from the cosmetic flash window above). Armed only where
    # rain ≥ STORM_JOLT_RAIN_MIN, so the strike can land anywhere in this band;
    # the exact pillar is random. Marked at the band centre. ─────────────────
    jolt = [pillars[i] for i in range(len(pillars))
            if weather.rain_intensity(phases[i]) >= config.STORM_JOLT_RAIN_MIN]
    if jolt:
        jlo, jhi = min(jolt), max(jolt)
        ax.axvspan(jlo, jhi, facecolor="#d62828", alpha=0.16, linewidth=0,
                   hatch="xx", edgecolor="#d62828",
                   label="Lightning strikes Pip (storm jolt, −score)")
        jmid = (jlo + jhi) / 2
        ax.plot([jmid], [1.0], marker=r"$⚡$", color="#d62828",
                markersize=16, zorder=7, clip_on=False)
        ax.annotate(f"⚡ strikes Pip\npillars {jlo}–{jhi}", (jmid, 1.0),
                    textcoords="offset points", xytext=(0, 12), ha="center",
                    fontsize=7.5, color="#a31515", fontweight="bold",
                    clip_on=False)

    # ── newbie onboarding band — plateau then ramp, in pillars ───────────────
    ax.axvspan(0, config.PLATEAU_PIPES, color="#3ca34d", alpha=0.22,
               linewidth=0, label="Newbie plateau / ramp", zorder=0)
    ax.axvspan(config.PLATEAU_PIPES, config.RAMP_PIPES, color="#3ca34d",
               alpha=0.11, linewidth=0, zorder=0)
    ax.annotate(f"plateau\n0–{config.PLATEAU_PIPES}",
                (config.PLATEAU_PIPES, 0.93), textcoords="offset points",
                xytext=(-3, 0), ha="right", va="top", fontsize=7.5,
                color="#1f6e2b", fontweight="bold")
    ax.annotate(f"ramp settles\npillar {config.RAMP_PIPES}",
                (config.RAMP_PIPES, 0.93), textcoords="offset points",
                xytext=(4, 0), ha="left", va="top", fontsize=7.5,
                color="#1f6e2b", fontweight="bold")

    # ── end-of-day event — treasure-box finale at the phase-wrap pillar ──────
    if day_end is not None:
        box_pillar = day_end + config.CYCLE_FINALE_BOX_INDEX
        ax.axvspan(day_end, day_end + config.CYCLE_FINALE_RUSH_PILLARS,
                   color="#caa23a", alpha=0.30, linewidth=0,
                   label="End of day — treasure-box finale")
        ax.axvline(day_end, color="#8a6b1f", linewidth=2)
        ax.annotate(
            f"END OF DAY\n+{config.TREASURE_BOX_GRANT} box @ pillar {box_pillar}",
            (day_end, 0.5), textcoords="offset points", xytext=(6, 0),
            rotation=90, fontsize=8, fontweight="bold", color="#6b520f",
            va="center", ha="left")

    # ── anchored power-ups — pickups placed at FIXED pillars (not the random
    # spawn roll): the genie lamp milestone and the two rain umbrellas. ───────
    POWERUP_ANCHORS = [
        ("Genie lamp", [weather.GENIE_PILLAR], "#b83dba", "D"),
        ("Umbrella", list(config.UMBRELLA_SPAWN_PILLARS), "#0f9090", "P"),
    ]
    for label, xs, color, mk in POWERUP_ANCHORS:
        for j, x in enumerate(xs):
            ax.axvline(x, color=color, linestyle=(0, (4, 3)), linewidth=1.6,
                       alpha=0.85, zorder=4)
            ax.plot([x], [1.04], marker=mk, color=color, markersize=11,
                    markeredgecolor="white", markeredgewidth=0.8,
                    clip_on=False, zorder=6,
                    label=(label if j == 0 else None))
        mid = sum(xs) / len(xs)
        tag = f"{label} @ {', '.join(str(x) for x in xs)}"
        ax.annotate(tag, (mid, 1.04), textcoords="offset points",
                    xytext=(0, 9), ha="center", fontsize=7.5, color=color,
                    fontweight="bold", clip_on=False)

    # ── clown event — the now-shipped interactive cinematic ──────────────────
    # HONEST status: at the clown phase (~CLOWN_START_PILLAR) the clown strolls in
    # with a floating die; on the die roll (a ~1s grab+spin beat, so the gauntlet
    # actually begins a few pillars LATER) a held CLOWN_SLOT_PILLARS-wide slot is
    # reserved — N=ROLL_MIN..ROLL_MAX warren towers + regular fill, with a small
    # GHOST chance. Then ~CLOWN_TO_RAIN_BUFFER pillars before rain (soft: warren
    # density + grab timing shift it). Bands are nominal _phase_for_pillar pillars.
    CLOWN_COLOR = "#c1121f"
    c0 = config.CLOWN_START_PILLAR
    c1 = c0 + config.CLOWN_SLOT_PILLARS
    ax.axvspan(c0, c1, color=CLOWN_COLOR, alpha=0.16, linewidth=0,
               label="Clown event — die roll → warren gauntlet (held 25)")
    ax.axvspan(c1, config.RAIN_START_PILLAR, color=CLOWN_COLOR, alpha=0.06,
               linewidth=0)  # soft buffer to rain
    ax.axvline(c0, color=CLOWN_COLOR, linewidth=2.4, zorder=4)
    ax.annotate(
        f"CLOWN enters ~{c0}\ndie roll → warren gauntlet\n"
        f"N={config.CLOWN_ROLL_MIN}-{config.CLOWN_ROLL_MAX} of held "
        f"{config.CLOWN_SLOT_PILLARS} (+ghost)\n"
        f"clear sky {config.CLOWN_PRECLEAR_PILLARS} before / "
        f"{config.CLOWN_LEADIN_PILLARS} pre-tunnel / "
        f"{config.CLOWN_OUTRO_PILLARS} after",
        (c0, 0.5), textcoords="offset points", xytext=(6, 0),
        rotation=90, fontsize=7.5, fontweight="bold", color="#8a0d17",
        va="center", ha="left", zorder=7)
    ax.annotate(f"~{config.CLOWN_TO_RAIN_BUFFER} → rain (soft)",
                ((c1 + config.RAIN_START_PILLAR) / 2, 0.06),
                textcoords="offset points", xytext=(0, 0), rotation=90,
                fontsize=6.5, color="#8a0d17", va="bottom", ha="center", zorder=6)

    # ── clear-sky RELIEF empties around the gauntlet: a pre-clear runway so the
    # clown enters an empty sky, a short pre-tunnel gap after the die settles,
    # and a breather right after the warren. They're phantom → UNSCORED, so they
    # don't advance this pagodas-passed axis (they hide existing pillars, don't
    # add any, and don't shift rain) — drawn as edge notches. ─────────────────
    RELIEF_COLOR = "#3a8fd6"
    for x, n, tag in ((c0 - config.CLOWN_PRECLEAR_PILLARS,
                       config.CLOWN_PRECLEAR_PILLARS, "pre-clear\n(before clown)"),
                      (c0, config.CLOWN_LEADIN_PILLARS, "lead-in\n(before tunnel)"),
                      (c1, config.CLOWN_OUTRO_PILLARS, "outro")):
        ax.plot([x], [1.0], marker="v", color=RELIEF_COLOR, markersize=9,
                markeredgecolor="white", markeredgewidth=0.8, zorder=8,
                clip_on=False,
                label=("Clown relief — clear-sky empties (unscored)"
                       if tag.startswith("pre-clear") else None))
        ax.annotate(f"+{n} clear sky\n({tag})", (x, 1.0),
                    textcoords="offset points", xytext=(0, 12), ha="center",
                    fontsize=6.5, color=RELIEF_COLOR, fontweight="bold",
                    clip_on=False, zorder=8)

    # Run-start marker + biome gridlines carried into the lower panel.
    ax.axvline(0, color="#222", linewidth=2)
    ax.annotate("RUN START", (0, 0.5), xytext=(6, 0),
                textcoords="offset points", rotation=90, fontsize=8.5,
                fontweight="bold", color="#222", va="center", ha="left")
    for phase, _ in phase_labels:
        ax.axvline(_pillar_for_phase(phase, phases), color="#bbb",
                   linestyle=":", linewidth=1, zorder=0)

    ax.set_xlim(0, pillars[-1])
    ax.set_ylim(0, 1.08)
    if show_xlabel:
        ax.set_xlabel("pagodas passed (pillars scored)")
    ax.set_ylabel("event intensity (0–1)")
    ax.grid(True, axis="y", alpha=0.25)
    ax.set_xticks(range(0, pillars[-1] + 1, 10))

    if show_legend:
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles, labels, loc="upper center",
                  bbox_to_anchor=(0.5, -0.13), ncol=4, framealpha=0.92,
                  fontsize=8.5)


def print_summary(pillars, phases, day_end):
    print(f"day boundary pillar = {day_end}")
    for label, fn, _ in CURVES:
        ys = [fn(ph) for ph in phases]
        pk_i = max(range(len(ys)), key=lambda i: ys[i])
        print(f"  {label}: peak at pillar {pillars[pk_i]} (intensity {ys[pk_i]:.2f})")
    print(f"  Genie lamp: pillar {weather.GENIE_PILLAR} "
          f"(geyser peak + {config.GENIE_PILLARS_AFTER_GEYSER_PEAK})")
    _umb_off = "/".join(f"+{u - config.RAIN_START_PILLAR}"
                        for u in config.UMBRELLA_SPAWN_PILLARS)
    print(f"  Umbrella: pillars {config.UMBRELLA_SPAWN_PILLARS} "
          f"(rain start {config.RAIN_START_PILLAR} {_umb_off})")
    print(f"  Clown event: held slot {config.CLOWN_START_PILLAR}"
          f"–{config.CLOWN_START_PILLAR + config.CLOWN_SLOT_PILLARS}, "
          f"then {config.CLOWN_TO_RAIN_BUFFER} regular → rain")
    print(f"  Clown relief: +{config.CLOWN_PRECLEAR_PILLARS} pre-clear (before "
          f"clown) / +{config.CLOWN_LEADIN_PILLARS} lead-in (before tunnel) / "
          f"+{config.CLOWN_OUTRO_PILLARS} outro clear-sky empties (unscored)")
    _jolt = [pillars[i] for i in range(len(pillars))
             if weather.rain_intensity(phases[i]) >= config.STORM_JOLT_RAIN_MIN]
    if _jolt:
        print(f"  Lightning strikes Pip (storm jolt): pillars {min(_jolt)}"
              f"–{max(_jolt)} (rain ≥ {config.STORM_JOLT_RAIN_MIN})")


def main() -> None:
    out_dir = os.path.join(ROOT, "docs", "screenshots")
    os.makedirs(out_dir, exist_ok=True)

    pillars, phases, day_end = compute_axis()

    fig, (ax_sky, ax) = plt.subplots(
        2, 1, figsize=(13, 6.2), dpi=130,
        gridspec_kw=dict(height_ratios=[1, 6], hspace=0.08),
        sharex=True,
    )
    draw_map(ax_sky, ax, pillars, phases, day_end)

    fig.tight_layout()
    out_path = os.path.join(out_dir, "event_pagoda_map_clown_v6.png")
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {out_path}")
    print_summary(pillars, phases, day_end)


if __name__ == "__main__":
    main()
