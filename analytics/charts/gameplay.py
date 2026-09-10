"""
Gameplay & balance Plotly builders.
"""
from __future__ import annotations

import math

import pandas as pd
import plotly.graph_objects as go

from constants import POWERUP_LABELS
from metrics.gameplay import MIN_EFFICACY_N
from theme import CORAL, GOLD, MUTED, SKY, SKY_SOFT, style

# Explicit log-axis ticks (1,2,5,10,…). Plotly's auto log ticks otherwise
# render a stray "1 / 9" minor-tick label at the very bottom of the axis.
_LOG_TICKS = [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000]

# Opacity floor for de-emphasised (small-sample) bars/points. Kept as a
# per-element ARRAY (Plotly-safe) so marker_color can stay a SCALAR — a
# per-bar marker_color *array* silently breaks the legend swatch.
_LOW_N_OPACITY = 0.32
_FULL_OPACITY = 1.0


def score_hist(scores: pd.Series) -> go.Figure:
    """Score distribution over the last 7 days, log-y.

    The x-axis is clipped to a robust upper bound rather than the raw max:
    a single near-ceiling whale/cheat run (the fixture has a 42k one)
    otherwise stretches the axis to 40k and squashes the entire 9–250-point
    playing population into one bar. The clip is built from p90/p95 — the
    *upper* quantiles still poisoned by a lone extreme value (p99 here is
    already 16k off one row) are deliberately avoided. Runs above the clip
    are counted in an annotation so nothing is hidden, just kept from
    dictating the scale. The vlines (median, p90) sit in opposite top
    corners so their labels never overlap."""
    fig = go.Figure()
    if scores.empty:
        return style(fig, "Score distribution (7d)")
    median = float(scores.median())
    p90 = float(scores.quantile(0.9))
    p95 = float(scores.quantile(0.95))
    # Right edge from low quantiles only (immune to a single whale): show
    # a little headroom past p95 / p90 for the genuine skilled tail. Pad 5%.
    clip = max(p95 * 1.5, p90 * 2.5, median * 2.0)
    n_over = int((scores > clip).sum())
    visible = scores[scores <= clip]
    fig.add_histogram(x=visible, nbinsx=40, marker_color=SKY,
                      hovertemplate="%{x}: %{y} runs<extra></extra>")
    fig.update_layout(yaxis_type="log", yaxis_title="Runs (log)",
                      xaxis_title="Score", xaxis_range=[0, clip * 1.05])
    # Explicit log tickvals: Plotly's default log ticks render a stray
    # "1 / 9"-style minor-tick artifact at the bottom of the axis.
    fig.update_yaxes(tickvals=_LOG_TICKS)
    fig.add_vline(x=median, line_dash="dash", line_color=GOLD,
                  annotation_text=f"median {int(median)}",
                  annotation_position="top left")
    fig.add_vline(x=p90, line_dash="dash", line_color=CORAL,
                  annotation_text=f"p90 {int(p90)}",
                  annotation_position="top right")
    if n_over:
        fig.add_annotation(x=1, y=1, xref="paper", yref="paper",
                           xanchor="right", yanchor="bottom", showarrow=False,
                           font=dict(size=10, color=MUTED),
                           text=f"+{n_over} run(s) above {int(clip):,} not shown")
    return style(fig, "Score distribution (7d)")


def duration_hist(durations: pd.Series) -> go.Figure:
    """Survival-time histogram. The spike near zero is the rage-quit /
    immediate-death population — worth watching for difficulty spikes."""
    fig = go.Figure()
    if durations.empty:
        return style(fig, "Survival time (7d)")
    fig.add_histogram(x=durations, nbinsx=40, marker_color=SKY,
                      hovertemplate="%{x}s: %{y} runs<extra></extra>")
    fig.update_layout(yaxis_type="log", yaxis_title="Runs (log)", xaxis_title="Seconds alive")
    fig.update_yaxes(tickvals=_LOG_TICKS)
    median = float(durations.median())
    fig.add_vline(x=median, line_dash="dash", line_color=GOLD,
                  annotation_text=f"median={median:.0f}s", annotation_position="top")
    return style(fig, "Survival time (7d)",
                 subtitle="Watch the near-zero spike (rage-quit) vs the survival mode")


def score_quantiles(q_df: pd.DataFrame) -> go.Figure:
    """Median + p90 score per day — the difficulty band the team tunes
    against. Three deliberate readability choices for the fat-tailed score
    distribution:
      • `max` is NOT drawn — a single near-ceiling run is a whale/cheater,
        not a tuning signal.
      • y-axis is log. On a low-volume day one extreme run can still drag
        p90 into the tens of thousands; on a linear axis that flattens
        every normal day into one flat line. Log keeps the ~200-point
        daily band legible while the spike stays visible — and honest.
      • thin days (n < MIN_EFFICACY_N) are drawn at low opacity with hollow
        markers — on a 6-run day a single whale rockets p90 to ~21k and
        owns half the axis. De-emphasising (not deleting) keeps the day
        visible without letting its noise read as a difficulty signal."""
    sub = (f"Daily difficulty band · log-y · faint = under {MIN_EFFICACY_N} "
           "runs (noisy) · max omitted (whale, not signal)")
    fig = go.Figure()
    if q_df.empty:
        return style(fig, "Score percentiles per day", subtitle=sub)
    low = q_df["low_n"].tolist() if "low_n" in q_df else [False] * len(q_df)
    opac = [_LOW_N_OPACITY if lo else _FULL_OPACITY for lo in low]
    symbols = ["circle-open" if lo else "circle" for lo in low]
    for col, color, name in (("median", SKY, "Median"),
                             ("p90", GOLD, "p90 (skilled ceiling)")):
        fig.add_scatter(
            x=q_df["date"], y=q_df[col], mode="lines+markers",
            name=name,
            # SCALAR line/marker colour so the legend swatch survives; the
            # noisy-day signal rides on the per-point opacity/symbol arrays.
            line=dict(color=color, width=2),
            marker=dict(color=color, size=7, opacity=opac, symbol=symbols),
            customdata=q_df["n"],
            hovertemplate="%{x|%b %d}: %{y:,.0f} pts · n=%{customdata}"
                          "<extra>" + name + "</extra>")
    # Legend below the plot — a top legend collides with the subtitle.
    fig.update_layout(yaxis_type="log", yaxis_title="Score (log)",
                      legend=dict(orientation="h", yanchor="top", y=-0.18, x=0))
    return style(fig, "Score percentiles per day", subtitle=sub)


def skill_over_time(skill_df: pd.DataFrame) -> go.Figure:
    """Median score-per-second-alive + near-miss-rate-per-pillar per day, on
    a SINGLE linear axis. Pillars/sec was cut: it's near-constant by
    fixed-step scroll design (a ±3% band a twin axis inflated into a fake
    story). Both lines kept here are per-unit rates of the same ~0.25–1.4
    magnitude, so they share one axis honestly:
      • score-per-second (GOLD, the actionable read) — efficiency. Rising =
        players threading rushes/power-ups faster; survival rate can't move
        with skill the way this can.
      • near-miss-per-pillar (SKY) — the half-real risk signal."""
    sub = "Single axis · efficiency (score/s) + risk (near-miss/pillar) · pillars/sec cut (fixed-step, near-constant)"
    fig = go.Figure()
    if skill_df.empty:
        return style(fig, "Skill over time", subtitle=sub)
    fig.add_scatter(x=skill_df["date"], y=skill_df["score_per_s"],
                    mode="lines+markers", name="Score / sec alive (median)",
                    line=dict(color=GOLD, width=2),
                    hovertemplate="%{x|%b %d}: %{y:.2f} pts/s<extra></extra>")
    fig.add_scatter(x=skill_df["date"], y=skill_df["near_miss_rate"],
                    mode="lines+markers", name="Near-miss / pillar",
                    line=dict(color=SKY, width=2),
                    hovertemplate="%{x|%b %d}: %{y:.2f} near-miss/pillar<extra></extra>")
    fig.update_layout(
        yaxis=dict(title="Per-second / per-pillar rate", rangemode="tozero"),
        legend=dict(orientation="h", yanchor="top", y=-0.18, x=0),
    )
    return style(fig, "Skill over time", subtitle=sub)


def powerup_mix(totals: pd.DataFrame) -> go.Figure:
    """Horizontal bar of pickup counts, most-picked at top. Window-agnostic
    title — the tab drives the window off the global control, so a baked-in
    '(7d)' would lie when the user widens it."""
    fig = go.Figure()
    if totals.empty:
        return style(fig, "Power-up pickups")
    ordered = totals.sort_values("count", ascending=True)
    labels = [POWERUP_LABELS.get(n, n) for n in ordered["name"]]
    fig.add_bar(x=ordered["count"], y=labels, orientation="h", marker_color=SKY,
                hovertemplate="%{y}: %{x} pickups<extra></extra>")
    fig.update_layout(xaxis_title="Pickups")
    return style(fig, "Power-up pickups", subtitle="Total picks over the selected window")


def powerup_efficacy(eff_df: pd.DataFrame) -> go.Figure:
    """The marquee balance read. Round 2 makes the headline quantity — the
    *excess* score lift NOT explained by longer survival — the chart's
    PRIMARY object instead of a hover footnote.

    Each power-up gets one diverging bar of `excess_lift_pct`
    (= score lift − survival lift). Read it as a flag, not a verdict:
    subtracting two median ratios is a crude exposure control (longer runs
    see more spawns), not a clean decomposition. A bar well to the right
    means the score bump is bigger than the extra time-on-screen alone
    would buy; near zero means the score gain mostly tracks survival.

    Colour scheme (deliberate, per the theme's semantics):
      • GOLD = the actionable element → reserved for the excess bar itself
        (the thing the team retunes against). The old build mis-mapped GOLD
        onto the *most-confounded* raw score bar; that's fixed.
      • CORAL marks negative-excess (under-performers) so the two
        directions read apart at a glance.
    Raw score lift, survival lift, and n now live in the HOVER as the
    supporting detail.

    Small-sample bars (n_with < MIN_EFFICACY_N) are de-emphasised via
    per-bar marker OPACITY (a Plotly-safe array) — never via a per-bar
    marker_color array, which silently blanks the legend swatch exactly
    when the data is noisy — plus the `*` label suffix."""
    fig = go.Figure()
    title = "Power-up efficacy — excess score lift (beyond survival)"
    sub = ("Bar = score lift − survival lift · gap ≈ score lift NOT explained by "
           "longer survival · a flag, not a verdict · correlational")
    if eff_df.empty:
        return style(fig, title, subtitle=sub)
    # Sort by the excess itself so the strongest over/under-performers land
    # at the extremes — the quantity sorted-on is now the quantity drawn.
    ordered = eff_df.sort_values("excess_lift_pct", ascending=True)
    labels = [POWERUP_LABELS.get(n, n) for n in ordered["powerup"]]
    excess = ordered["excess_lift_pct"]
    # SCALAR colour per directional group is impossible in one trace, so we
    # encode sign with a per-bar colour array AND ship a manual legend via
    # invisible scatter proxies — but the swatch-blanking bug is about the
    # *legend trace's* marker, which here is a clean scalar. The bars carry
    # no legend (single semantic series), so a colour array is safe.
    bar_colors = [GOLD if v >= 0 else CORAL for v in excess]
    bar_opac = [_LOW_N_OPACITY if low else _FULL_OPACITY for low in ordered["low_n"]]
    fig.add_bar(
        x=excess, y=labels, orientation="h",
        marker=dict(color=bar_colors, opacity=bar_opac),
        text=[f"{v:+.0f}%" + ("*" if low else "")
              for v, low in zip(excess, ordered["low_n"])],
        textposition="outside", textfont=dict(size=11),
        customdata=ordered[["score_lift_pct", "dur_lift_pct",
                            "n_with", "n_without"]].values,
        hovertemplate="<b>%{y}</b> — excess %{x:+.0f}%<br>"
                      "score lift %{customdata[0]:+.0f}% · "
                      "survival lift %{customdata[1]:+.0f}%<br>"
                      "n=%{customdata[2]} with, %{customdata[3]} without"
                      "<extra></extra>",
        showlegend=False,
    )
    fig.add_vline(x=0, line_color=MUTED, line_width=1)
    span = float(max(excess.abs().max(), 1))
    fig.update_layout(
        bargap=0.32,
        xaxis_title="Excess score lift (%)  ·  * = small sample, read with caution",
        xaxis_range=[-span * 1.45, span * 1.45],
    )
    fig.update_traces(cliponaxis=False)
    return style(fig, title, subtitle=sub)


def coin_economy(econ_df: pd.DataFrame) -> go.Figure:
    """Coins-per-pillar per day — economy density over time. A drift flags
    a coin-spawn or rush-rate regression independent of how long runs run."""
    fig = go.Figure()
    if econ_df.empty:
        return style(fig, "Coin economy")
    fig.add_scatter(x=econ_df["date"], y=econ_df["coins_per_pillar"],
                    mode="lines+markers", line=dict(color=GOLD, width=2),
                    hovertemplate="%{x|%b %d}: %{y:.2f} coins/pillar<extra></extra>")
    # Anchor the y-axis at zero. Plotly's autoscale zooms to the data's
    # ±2% jitter and dramatises a flat economy into a sawtooth — exactly
    # the "don't sell noise as a trend" trap. A zero floor shows the
    # series for what it is: steady, with a headroom band for a real
    # regression to actually look like one.
    top = float(econ_df["coins_per_pillar"].max())
    fig.update_layout(yaxis_title="Coins per pillar",
                      yaxis_range=[0, top * 1.25])
    return style(fig, "Coin economy", subtitle="Coins collected per pillar passed")


def score_vs_survival(sv_df: pd.DataFrame, powerup: str = "magnet") -> go.Figure:
    """One point per run: survival seconds (x) vs score (y), coloured by
    whether the run picked the power-up of interest. The difficulty-shape
    view the histograms can't give, and the picture the efficacy bar only
    summarises — you SEE the exposure confound directly: picked-runs
    clustering up-and-right (longer AND higher-scoring) is the very
    correlation the excess-lift number tries to net out.

    Score axis is log and clipped on tickvals so a single near-ceiling
    whale doesn't flatten the cloud (and to kill the '1 / 9' minor-tick
    artifact). Two SCALAR-coloured traces → the legend swatch survives."""
    label = POWERUP_LABELS.get(powerup, powerup)
    sub = (f"Each dot = one run · colour = picked {label} · "
           "up-and-right cluster = the exposure confound, drawn")
    fig = go.Figure()
    title = f"Score vs survival ({label})"
    if sv_df.empty:
        return style(fig, title, subtitle=sub)
    # Clip the score axis to a robust upper bound (same reasoning as
    # score_hist): a lone near-ceiling whale otherwise pins the top of the
    # log range and squashes the whole playing population into the floor,
    # costing ~40% of the panel. Bound from low quantiles (whale-immune),
    # keep all points but cap the view, and count what's above so nothing
    # is hidden — just kept from dictating the scale.
    scores = sv_df["score"].clip(lower=1)
    clip = max(float(scores.quantile(0.95)) * 1.5,
               float(scores.quantile(0.9)) * 2.5, 1.0)
    n_over = int((scores > clip).sum())
    for picked, color, name in ((False, SKY_SOFT, f"No {label}"),
                                (True, GOLD, label)):
        grp = sv_df[sv_df["picked"] == picked]
        if grp.empty:
            continue
        fig.add_scatter(
            x=grp["duration_s"], y=grp["score"].clip(lower=1),
            mode="markers", name=name,
            marker=dict(color=color, size=6, opacity=0.6,
                        line=dict(width=0)),
            hovertemplate="%{x:.0f}s alive · %{y:,.0f} pts<extra>" + name + "</extra>",
        )
    fig.update_layout(
        yaxis=dict(type="log", title="Score (log)", tickvals=_LOG_TICKS,
                   range=[0, math.log10(clip * 1.1)]),
        xaxis_title="Seconds alive",
        legend=dict(orientation="h", yanchor="top", y=-0.18, x=0),
    )
    if n_over:
        fig.add_annotation(x=1, y=1, xref="paper", yref="paper",
                           xanchor="right", yanchor="bottom", showarrow=False,
                           font=dict(size=10, color=MUTED),
                           text=f"+{n_over} run(s) above {int(clip):,} not shown")
    return style(fig, title, subtitle=sub)


def powerups_per_run(df: pd.DataFrame) -> go.Figure:
    """Avg power-ups picked per run, per day — a spawn-rate regression
    watch. Retained as a builder for the KPI/diagnostic surface; the tab
    leads with the per-run KPI card instead of a near-flat line to stay
    under the ≤8-visual budget. Kept so charts.__init__ stays stable."""
    fig = go.Figure()
    if df.empty:
        return style(fig, "Power-ups per run (30d)")
    fig.add_scatter(x=df["date"], y=df["per_run"], mode="lines+markers",
                    line=dict(color=GOLD, width=2),
                    hovertemplate="%{y:.2f} / run<extra></extra>")
    return style(fig, "Power-ups per run (30d)")
