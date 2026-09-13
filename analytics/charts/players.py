"""
Players & retention Plotly builders.
"""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from theme import CORAL, GOLD, GRID, MUTED, SKY, SKY_SOFT, style

_CAVEAT = "Install = first play seen in window; trailing cohorts are censored, not zero"


def retention_curve(
    exact_df: pd.DataFrame, rolling_df: pd.DataFrame | None = None,
) -> go.Figure:
    """Pooled D0..Dn retention curve. The single most important shape on
    the tab — how fast the game leaks players.

    The headline (solid) line is EXACT classic Dn — the same basis the
    KPI cards and the hyper-casual benchmarks use, so card, chart and
    benchmark all agree. It is shaded with its Wilson 95% band
    (frac_lo/frac_hi) so small-N points read as uncertain, not as a
    discovered floor. When `rolling_df` (the unbounded curve) is supplied
    it is drawn as a dashed secondary line, explicitly labelled as not
    comparable to standard Dn. N (settled denominator) rides the subtitle."""
    fig = go.Figure()
    note = "Exact classic Dn (benchmark-comparable) · shaded = Wilson 95% CI"
    if exact_df.empty:
        return style(fig, "Retention curve (D0–D7)", subtitle=note)
    n = int(exact_df["cohort_devices"].iloc[0])
    x = exact_df["day_offset"]

    # Wilson band first so the lines sit on top of the shading.
    if {"frac_lo", "frac_hi"}.issubset(exact_df.columns):
        fig.add_scatter(
            x=x, y=exact_df["frac_hi"] * 100, mode="lines",
            line=dict(width=0), hoverinfo="skip", showlegend=False,
        )
        fig.add_scatter(
            x=x, y=exact_df["frac_lo"] * 100, mode="lines",
            line=dict(width=0), fill="tonexty", fillcolor=SKY_SOFT,
            hoverinfo="skip", showlegend=False,
        )

    if rolling_df is not None and not rolling_df.empty:
        rpct = rolling_df["retained_frac"] * 100
        fig.add_scatter(
            x=rolling_df["day_offset"], y=rpct, mode="lines+markers",
            name="rolling: active by day ≥ n — not comparable to standard Dn",
            line=dict(color=MUTED, width=2, dash="dash"),
            marker=dict(size=6, color=MUTED),
            customdata=rolling_df["retained"],
            hovertemplate="rolling D%{x}: %{y:.1f}% (%{customdata} of "
                          + f"{n})<extra></extra>",
        )

    pct = exact_df["retained_frac"] * 100
    fig.add_scatter(
        x=x, y=pct, mode="lines+markers+text", name="exact (classic Dn)",
        line=dict(color=SKY, width=3), marker=dict(size=8, color=SKY),
        text=[f"{p:.0f}%" for p in pct], textposition="top center",
        textfont=dict(color=MUTED, size=11),
        customdata=exact_df["retained"],
        hovertemplate="exact D%{x}: %{y:.1f}% (%{customdata} of "
                      + f"{n})<extra></extra>",
    )
    fig.update_layout(
        xaxis=dict(title="Days since first play", dtick=1),
        yaxis=dict(title="Retained", ticksuffix="%", range=[0, 130]),
        # Legend inside the plot's top band (below the title+subtitle row)
        # so it never collides with the left-anchored title text.
        legend=dict(orientation="h", yanchor="top", y=0.99,
                    xanchor="right", x=1.0, font=dict(size=10),
                    bgcolor="rgba(15,27,45,0.6)"),
    )
    subtitle = f"{note} · n={n} settled installs"
    return style(fig, "Retention curve (D0–D7)", subtitle=subtitle)


# A light→dark sequential scale that STARTS light, so a 0% cell is a pale
# wash and a 100% cell is deep sky. Censored (NaN) cells are left
# transparent over a deliberate slate "no-data" plot background, so the
# three states — 0% (pale), 100% (deep), censored (slate) — never collide
# the way a dark-at-0 Blues scale did on the INK page.
_RETENTION_SCALE = [
    [0.0, "#EAF3FF"],   # 0% — pale, clearly not "no data"
    [0.5, SKY],
    [1.0, "#0B3D7A"],   # 100% — deep sky
]
_CENSORED_BG = "#243449"   # slate, distinct from both ends of the scale


def retention_matrix(matrix_df: pd.DataFrame, sizes=None) -> go.Figure:
    """Cohort × day-offset retention triangle. Only cohorts of n≥3 reach
    here (the metric suppresses smaller ones), so each cell is signal not
    a single coin-flip. Censored cells stay blank — rendered against a
    slate "no-data" background so they read as distinct from 0% (pale) and
    100% (deep). Row labels carry the cohort size (n=…) when `sizes` (a
    cohort_date → size mapping) is supplied."""
    fig = go.Figure()
    if matrix_df.empty:
        return style(fig, "Retention by cohort",
                     subtitle="No cohort with n≥3 settled yet · " + _CAVEAT)
    z = (matrix_df * 100).values

    def _label(d):
        base = d.strftime("%b %d") if hasattr(d, "strftime") else str(d)
        if sizes is not None and d in sizes:
            return f"{base} · n={int(sizes[d])}"
        return base

    y = [_label(d) for d in matrix_df.index]
    fig.add_trace(go.Heatmap(
        z=z, x=[f"D{c}" for c in matrix_df.columns], y=y,
        colorscale=_RETENTION_SCALE, zmin=0, zmax=100,
        hoverongaps=False,
        hovertemplate="%{y} · %{x}: %{z:.0f}%<extra></extra>",
        colorbar=dict(title="%"),
    ))
    fig.update_yaxes(autorange="reversed")
    fig = style(fig, "Retention by cohort",
                subtitle="Cohorts n≥3 only · censored=slate, 0%=pale, 100%=deep · "
                         + _CAVEAT)
    # Paint the no-data background so NaN cells are an explicit slate, not
    # the page's INK (which reads like a high-retention deep-blue cell).
    fig.update_layout(plot_bgcolor=_CENSORED_BG)
    return fig


def new_vs_returning(nvr_df: pd.DataFrame, days: int = 30) -> go.Figure:
    """Stacked daily new vs returning active players. Healthy growth is a
    rising returning base, not just churn-and-replace acquisition."""
    fig = go.Figure()
    if nvr_df.empty:
        return style(fig, f"New vs returning players ({days}d)")
    fig.add_bar(
        x=nvr_df["date"], y=nvr_df["returning"], name="Returning",
        marker_color=SKY, hovertemplate="%{y} returning<extra></extra>",
    )
    fig.add_bar(
        x=nvr_df["date"], y=nvr_df["new"], name="New",
        marker_color=GOLD, hovertemplate="%{y} new<extra></extra>",
    )
    fig.update_layout(
        barmode="stack",
        # Park the legend in the plot's top-right corner instead of the
        # band above it, so it never collides with the left-anchored title.
        legend=dict(orientation="h", yanchor="top", y=0.99,
                    xanchor="right", x=1.0, font=dict(size=11),
                    bgcolor="rgba(0,0,0,0)"),
        yaxis_title="Active players",
    )
    return style(fig, f"New vs returning players ({days}d)",
                 subtitle="Returning = device seen before today; new = first seen")


def sessions_histogram(sessions: pd.Series, days: int = 30) -> go.Figure:
    """Distribution of plays-per-active-day. A wall at 1 = single-run
    sessions; a long tail = bingeing."""
    fig = go.Figure()
    if sessions.empty:
        return style(fig, f"Session depth ({days}d)")
    fig.add_histogram(
        x=sessions, marker_color=SKY,
        # Bins centred on each integer (edges at .5) so a bar sits squarely
        # over "1", "2", … and never straddles two counts.
        xbins=dict(start=0.5, size=1),
        hovertemplate="%{x} plays/day: %{y} sessions<extra></extra>",
    )
    median = float(sessions.median())
    fig.add_vline(
        x=median, line_dash="dash", line_color=GOLD,
        annotation_text=f"median {median:.0f}",
        # Anchor the label to the line itself (its x), not the panel top-
        # right, so the reader's eye ties the number to the dashes.
        annotation_position="top", annotation_xanchor="left",
        annotation_font=dict(color=GOLD, size=11),
    )
    # Integer ticks so "2 plays" is unambiguous.
    fig.update_layout(
        xaxis=dict(title="Plays in a single day", dtick=1, tick0=1),
        yaxis_title="Device-days",
    )
    return style(fig, f"Session depth ({days}d)",
                 subtitle="Plays per device per active day")


def engagement_segments(seg_df: pd.DataFrame, days: int) -> go.Figure:
    """Horizontal bar of player counts per play-count bucket. The 1-play
    bar is drawn in gold so the bounce segment pops."""
    fig = go.Figure()
    if seg_df.empty:
        return style(fig, f"Players by engagement ({days}d)")
    colors = [GOLD if seg == "1 play" else SKY for seg in seg_df["segment"]]
    fig.add_bar(
        x=seg_df["players"], y=seg_df["segment"], orientation="h",
        marker_color=colors, text=seg_df["players"], textposition="outside",
        hovertemplate="%{y}: %{x} players<extra></extra>",
    )
    total = int(seg_df["players"].sum())
    one_shot = int(seg_df.loc[seg_df["segment"] == "1 play", "players"].sum())
    subtitle = (
        f"{one_shot}/{total} players ({one_shot / total * 100:.0f}%) played only once"
        if total else "no players in window"
    )
    span = float(seg_df["players"].max() or 1)
    fig.update_layout(xaxis_title="Players", yaxis=dict(autorange="reversed"),
                      xaxis_range=[0, span * 1.18])
    fig.update_traces(cliponaxis=False)
    return style(fig, f"Players by engagement ({days}d)", subtitle=subtitle)
