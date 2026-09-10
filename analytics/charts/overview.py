"""
Overview / live-ops Plotly builders. Each takes pre-aggregated data and
returns a styled go.Figure (theme.style centralises the look).
"""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from theme import CORAL, GOLD, GRID, MUTED, SKY, SKY_SOFT, style


def daily_activity(band_df: pd.DataFrame, by_day_df: pd.DataFrame,
                   days: int = 30) -> go.Figure:
    """The single daily-activity panel: plays-per-day volume, whether that
    volume is normal, and unique players — all in one chart so the tab
    isn't showing the same series twice.

      • Plays = SKY bars (primary axis).
      • Expected range = a *trailing* Poisson band (λ ± 2√λ), drawn only
        past the 14-day warm-up so no fabricated "normal range" shows on
        thin history; λ as a dotted line.
      • Anomalous days (Poisson z beyond ±2, spike or drop) = haloed coral
        markers on the bar tops — unmistakable.
      • Unique players = GOLD line on a secondary axis.

    Takes both pre-aggregated frames (band_df from daily_plays_with_band,
    by_day_df from by_day) and aligns them on date — both are built over
    the same continuous day index."""
    fig = go.Figure()
    if band_df.empty:
        return style(fig, f"Daily activity ({days}d)")

    # Volume bars first so the band/markers/line read on top of them.
    fig.add_bar(
        x=band_df["date"], y=band_df["plays"], name="Plays",
        marker_color=SKY_SOFT, hovertemplate="%{y} plays<extra></extra>",
    )

    # Poisson expected-range ribbon over the warmed-up tail (NaN on warm-up
    # days leaves a gap rather than a fake band collapsing to the point).
    fig.add_scatter(
        x=band_df["date"], y=band_df["hi"], mode="lines",
        line=dict(width=0), showlegend=False, hoverinfo="skip", connectgaps=False,
    )
    fig.add_scatter(
        x=band_df["date"], y=band_df["lo"], mode="lines", fill="tonexty",
        fillcolor="rgba(77,163,255,0.16)", line=dict(width=0),
        name="Expected range (λ ± 2√λ)", hoverinfo="skip", connectgaps=False,
    )
    fig.add_scatter(
        x=band_df["date"], y=band_df["mean"], mode="lines",
        line=dict(color=SKY, width=1, dash="dot"), name="14d baseline λ",
        hovertemplate="%{y:.1f} expected (λ)<extra></extra>", connectgaps=False,
    )

    # "warm-up (no band yet)" cue over the warm-up region.
    warm_dates = band_df.loc[band_df["warmup"], "date"]
    if not warm_dates.empty:
        mid = warm_dates.iloc[len(warm_dates) // 2]
        ymax = float(band_df["plays"].max() or 1)
        fig.add_annotation(
            x=mid, y=ymax, yanchor="top", showarrow=False,
            text="warm-up<br>(no band yet)",
            font=dict(size=10, color=MUTED), align="center", opacity=0.9,
        )

    # Anomalous days: haloed coral markers on the bar tops.
    outlier = band_df["outlier"].to_numpy()
    fig.add_scatter(
        x=band_df.loc[outlier, "date"], y=band_df.loc[outlier, "plays"],
        mode="markers", name="Anomalous day",
        marker=dict(color=CORAL, size=13, symbol="circle",
                    line=dict(color="#FFE2D2", width=3)),
        hovertemplate="%{y} plays (anomalous)<extra></extra>",
    )

    # Unique players on the secondary axis (GOLD). Aligned on date so a
    # mismatched index can't silently misplot.
    uniq = band_df[["date"]].merge(by_day_df[["date", "uniques"]],
                                   on="date", how="left")
    fig.add_scatter(
        x=uniq["date"], y=uniq["uniques"], name="Unique players",
        mode="lines+markers", line=dict(color=GOLD, width=2), yaxis="y2",
        hovertemplate="%{y} unique<extra></extra>",
    )

    n_out = int(outlier.sum())
    sub = (f"{n_out} day(s) outside the expected Poisson range (λ ± 2√λ)"
           if n_out else "Volume within the expected Poisson range (λ ± 2√λ)")
    # Tint each axis title to its series so line→axis mapping needs no legend.
    fig.update_layout(
        yaxis=dict(title=dict(text="Plays", font=dict(color=SKY))),
        yaxis2=dict(title=dict(text="Unique players", font=dict(color=GOLD)),
                    overlaying="y", side="right", showgrid=False,
                    tickfont=dict(color=GOLD), rangemode="tozero"),
        legend=dict(orientation="h", yanchor="top", y=-0.18, x=0),
    )
    return style(fig, f"Daily activity ({days}d)", subtitle=sub)


def rejection_reasons(reasons_df: pd.DataFrame, days: int = 7) -> go.Figure:
    """Horizontal bar of rejected-submit reasons. Empty (no rejections) is
    a good state — render a clean empty frame, not an error."""
    fig = go.Figure()
    if reasons_df.empty:
        fig.add_annotation(text="No rejected submits in window 🎉",
                           xref="paper", yref="paper", x=0.5, y=0.5,
                           showarrow=False, font=dict(color=GRID))
        return style(fig, f"Rejected submits by reason ({days}d)")
    ordered = reasons_df.sort_values("count", ascending=True)
    fig.add_bar(
        x=ordered["count"], y=ordered["reason"], orientation="h",
        marker_color=CORAL, text=ordered["count"], textposition="outside",
        cliponaxis=False, hovertemplate="%{y}: %{x}<extra></extra>",
    )
    # Counts are integers — force integer ticks so a 1-vs-1 read doesn't
    # show fractional 0.2/0.4 gridlines, and pad the axis for the labels.
    top = int(ordered["count"].max())
    fig.update_layout(
        xaxis=dict(title="Rejected runs", dtick=1, range=[0, top + 1]),
    )
    return style(fig, f"Rejected submits by reason ({days}d)",
                 subtitle="The plausibility gate that dropped each run")


def avg_duration(by_day_df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    if by_day_df.empty:
        return style(fig, "Avg session duration (s)")
    fig.add_scatter(
        x=by_day_df["date"], y=by_day_df["avg_duration_s"],
        mode="lines+markers", line=dict(color=SKY, width=2),
        hovertemplate="%{y:.1f}s<extra></extra>",
    )
    return style(fig, "Avg session duration (s)")


def hourly_heatmap(grid: pd.DataFrame) -> go.Figure:
    """Weekday × hour-of-day heatmap. Rows Mon..Sun for reading order."""
    weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    fig = go.Figure(data=go.Heatmap(
        z=grid.values,
        x=[f"{h:02d}" for h in grid.columns],
        y=weekdays,
        colorscale="Blues",
        hovertemplate="%{y} %{x}:00 — %{z} plays<extra></extra>",
        colorbar=dict(title="Plays"),
    ))
    fig.update_yaxes(autorange="reversed")
    # Framed as the companion to the freshness / "alive" check: a quiet
    # dashboard right now is only worth an alert if *this* weekday-hour
    # cell is usually busy. Reads as health context, not a planning grid.
    return style(fig, "Quiet now? Compare to the usual weekly rhythm",
                 subtitle="Plays by UTC weekday × hour — is the current "
                          "silence expected for this slot?")
