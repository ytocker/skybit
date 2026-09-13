"""Round 6 — five simple king crowns.

Round 5 (historical, jewel-encrusted) rejected as too sophisticated.
User wants the iconic flat-icon style — just a band, a few peaks,
maybe a gem or two. The shape kids draw when they draw a king's
crown. The shape Brawl Stars and FontAwesome use.

Designs:

  crown_s1.png — Three-point Crown   (3 sharp peaks, gem on each)
  crown_s2.png — Five-point Crown    (5 sharp peaks, gem on each)
  crown_s3.png — King's Cross Crown  (3 peaks, middle is a small cross)
  crown_s4.png — Spiked Diadem       (5 sharp spikes, no peak gems)
  crown_s5.png — Three-bump Crown    (3 rounded semicircle peaks)

Same bolder pipeline as round 5: 2× oversample, NEAR_BLACK outlines,
single-stop gold + highlight, one optional centre band gem.
"""

import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import sys
import pygame

pygame.init()
pygame.font.init()

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.config import W, H
from tools.preview_crown_variants import (
    draw_leaderboard_variant, draw_bg, SCORES,
)
from tools.preview_crown_grandiose import (
    GOLD_HI, GOLD, GOLD_LO,
    RUBY, RUBY_HI, SAPPHIRE, SAPPHIRE_HI, EMERALD, EMERALD_HI,
    PEARL, _with_shadow,
)
from tools.preview_crown_kings import (
    NEAR_BLACK, OS,
    _oversampled2, _band_outlined,
    _outlined_polygon, _outlined_gem,
)


# ── S1: Three-point Crown ───────────────────────────────────────────────────

def _draw_s1(big, s):
    """3 sharp pointed peaks of equal height, gem ball on each tip,
    one small ruby in the band centre. 44 × 32 px."""
    bw, bh = big.get_width(), big.get_height()
    cx = bw // 2
    band_top = 18 * s
    band_bot = 26 * s
    band_l = 2 * s
    band_r = bw - 2 * s
    _band_outlined(big, s, band_l, band_top, band_r, band_bot)

    # Centre ruby on band
    _outlined_gem(big, cx, (band_top + band_bot) // 2,
                  int(1.6 * s), RUBY, RUBY_HI)

    # 3 peaks at evenly spaced positions
    peak_xs = [cx - 14 * s, cx, cx + 14 * s]
    pw = 4 * s  # half-width at base
    ph = 12 * s  # height above band
    for px in peak_xs:
        tip = (px, band_top - ph)
        l   = (px - pw, band_top)
        r   = (px + pw, band_top)
        _outlined_polygon(big, [tip, l, r], GOLD, GOLD_HI)

    # Gem ball on each peak tip — alternating colours
    gem_colours = [(SAPPHIRE, SAPPHIRE_HI), (RUBY, RUBY_HI),
                   (SAPPHIRE, SAPPHIRE_HI)]
    for px, (gc, gh) in zip(peak_xs, gem_colours):
        tip_y = band_top - ph
        _outlined_gem(big, px, tip_y - 2 * s, int(1.8 * s), gc, gh)


def draw_crown_s1(surf, cx, cy):
    bw, bh = 44, 32
    img = _with_shadow(_oversampled2(_draw_s1, bw, bh))
    surf.blit(img, (cx - bw // 2, cy - bh // 2 + 2))


# ── S2: Five-point Crown ────────────────────────────────────────────────────

def _draw_s2(big, s):
    """5 peaks, centre tallest, each topped with a gem ball.
    52 × 34 px."""
    bw, bh = big.get_width(), big.get_height()
    cx = bw // 2
    band_top = 20 * s
    band_bot = 28 * s
    band_l = 2 * s
    band_r = bw - 2 * s
    _band_outlined(big, s, band_l, band_top, band_r, band_bot)
    _outlined_gem(big, cx, (band_top + band_bot) // 2,
                  int(1.6 * s), RUBY, RUBY_HI)

    peak_xs = [cx - 19 * s, cx - 10 * s, cx, cx + 10 * s, cx + 19 * s]
    peak_hs = [9 * s, 12 * s, 16 * s, 12 * s, 9 * s]
    peak_pw = [3 * s, 3 * s, 4 * s, 3 * s, 3 * s]
    for px, ph, pw in zip(peak_xs, peak_hs, peak_pw):
        tip = (px, band_top - ph)
        l   = (px - pw, band_top)
        r   = (px + pw, band_top)
        _outlined_polygon(big, [tip, l, r], GOLD, GOLD_HI)

    # Gem on each peak: ruby in centre, sapphires + emeralds outside
    gem_colours = [
        (EMERALD, EMERALD_HI),
        (SAPPHIRE, SAPPHIRE_HI),
        (RUBY, RUBY_HI),
        (SAPPHIRE, SAPPHIRE_HI),
        (EMERALD, EMERALD_HI),
    ]
    for px, ph, (gc, gh) in zip(peak_xs, peak_hs, gem_colours):
        _outlined_gem(big, px, band_top - ph - 2 * s,
                      int(1.6 * s), gc, gh)


def draw_crown_s2(surf, cx, cy):
    bw, bh = 52, 36
    img = _with_shadow(_oversampled2(_draw_s2, bw, bh))
    surf.blit(img, (cx - bw // 2, cy - bh // 2 + 2))


# ── S3: King's Cross Crown ──────────────────────────────────────────────────

def _draw_s3(big, s):
    """3 peaks where the centre is a small Christian cross instead of
    a gem ball. Side peaks have gems. 48 × 38 px."""
    bw, bh = big.get_width(), big.get_height()
    cx = bw // 2
    band_top = 24 * s
    band_bot = 32 * s
    band_l = 2 * s
    band_r = bw - 2 * s
    _band_outlined(big, s, band_l, band_top, band_r, band_bot)
    _outlined_gem(big, cx, (band_top + band_bot) // 2,
                  int(1.6 * s), RUBY, RUBY_HI)

    # Side peaks (shorter than the centre, leave room for cross above)
    side_xs = [cx - 15 * s, cx + 15 * s]
    side_pw = 4 * s
    side_ph = 11 * s
    for sx in side_xs:
        tip = (sx, band_top - side_ph)
        l   = (sx - side_pw, band_top)
        r   = (sx + side_pw, band_top)
        _outlined_polygon(big, [tip, l, r], GOLD, GOLD_HI)
        _outlined_gem(big, sx, band_top - side_ph - 2 * s,
                      int(1.6 * s), SAPPHIRE, SAPPHIRE_HI)

    # Centre peak — slightly shorter triangle with a Christian cross above
    centre_ph = 8 * s
    centre_pw = 4 * s
    c_tip = (cx, band_top - centre_ph)
    c_l   = (cx - centre_pw, band_top)
    c_r   = (cx + centre_pw, band_top)
    _outlined_polygon(big, [c_tip, c_l, c_r], GOLD, GOLD_HI)

    # Small Christian cross above the centre peak
    cross_top = c_tip[1] - 9 * s
    cross_bot = c_tip[1]
    cross_thick = max(2, s + 1)
    pygame.draw.rect(big, NEAR_BLACK,
                     (cx - cross_thick // 2 - 1, cross_top - 1,
                      cross_thick + 2, cross_bot - cross_top + 2))
    pygame.draw.rect(big, GOLD,
                     (cx - cross_thick // 2, cross_top,
                      cross_thick, cross_bot - cross_top))
    bar_y = cross_top + 3 * s
    pygame.draw.rect(big, NEAR_BLACK,
                     (cx - 4 * s - 1, bar_y - 1,
                      8 * s + 2, cross_thick + 2))
    pygame.draw.rect(big, GOLD,
                     (cx - 4 * s, bar_y, 8 * s, cross_thick))


def draw_crown_s3(surf, cx, cy):
    bw, bh = 48, 38
    img = _with_shadow(_oversampled2(_draw_s3, bw, bh))
    surf.blit(img, (cx - bw // 2, cy - bh // 2 + 2))


# ── S4: Spiked Diadem ───────────────────────────────────────────────────────

def _draw_s4(big, s):
    """5 narrow sharp spikes of equal height, no peak gems. Just a
    band with spiky points — minimalist. 50 × 30 px."""
    bw, bh = big.get_width(), big.get_height()
    cx = bw // 2
    band_top = 18 * s
    band_bot = 26 * s
    band_l = 2 * s
    band_r = bw - 2 * s
    _band_outlined(big, s, band_l, band_top, band_r, band_bot)
    _outlined_gem(big, cx, (band_top + band_bot) // 2,
                  int(2 * s), RUBY, RUBY_HI)

    spike_xs = [cx - 19 * s, cx - 10 * s, cx, cx + 10 * s, cx + 19 * s]
    spike_pw = 2 * s
    spike_h = 14 * s
    for sx in spike_xs:
        tip = (sx, band_top - spike_h)
        l   = (sx - spike_pw, band_top)
        r   = (sx + spike_pw, band_top)
        _outlined_polygon(big, [tip, l, r], GOLD, GOLD_HI)


def draw_crown_s4(surf, cx, cy):
    bw, bh = 50, 30
    img = _with_shadow(_oversampled2(_draw_s4, bw, bh))
    surf.blit(img, (cx - bw // 2, cy - bh // 2 + 2))


# ── S5: Three-bump Crown (rounded) ──────────────────────────────────────────

def _draw_s5(big, s):
    """3 rounded semicircle peaks (cartoon style) with gems set in
    the cusps between them. 44 × 30 px."""
    bw, bh = big.get_width(), big.get_height()
    cx = bw // 2
    band_top = 18 * s
    band_bot = 26 * s
    band_l = 2 * s
    band_r = bw - 2 * s

    # Draw the rounded peaks FIRST — they extend up above the band.
    # Each peak is a filled circle drawn so the bottom half overlaps
    # the band area (which is drawn on top, hiding the bottom half).
    peak_xs = [cx - 13 * s, cx, cx + 13 * s]
    peak_r = 7 * s
    for px in peak_xs:
        # Outline (slightly larger circle behind)
        pygame.draw.circle(big, NEAR_BLACK, (px, band_top), peak_r + 1)
        # Body
        pygame.draw.circle(big, GOLD, (px, band_top), peak_r)
        # Highlight crescent
        pygame.draw.circle(big, GOLD_HI,
                           (px - 2 * s, band_top - 1 * s),
                           max(2, peak_r // 2))

    # Now draw the band over the bottom halves of the bumps
    _band_outlined(big, s, band_l, band_top, band_r, band_bot)
    _outlined_gem(big, cx, (band_top + band_bot) // 2,
                  int(1.6 * s), RUBY, RUBY_HI)

    # Gem at the top of each rounded peak
    gem_colours = [(SAPPHIRE, SAPPHIRE_HI), (EMERALD, EMERALD_HI),
                   (SAPPHIRE, SAPPHIRE_HI)]
    for px, (gc, gh) in zip(peak_xs, gem_colours):
        _outlined_gem(big, px, band_top - peak_r + 2 * s,
                      int(1.5 * s), gc, gh)

    # Small pearls in the cusps between bumps
    cusp_xs = [(peak_xs[i] + peak_xs[i + 1]) // 2 for i in range(2)]
    for px in cusp_xs:
        pygame.draw.circle(big, NEAR_BLACK, (px, band_top - 1 * s),
                           int(1.4 * s))
        pygame.draw.circle(big, PEARL, (px, band_top - 1 * s),
                           max(1, int(s)))


def draw_crown_s5(surf, cx, cy):
    bw, bh = 44, 30
    img = _with_shadow(_oversampled2(_draw_s5, bw, bh))
    surf.blit(img, (cx - bw // 2, cy - bh // 2 + 2))


# ── Render ──────────────────────────────────────────────────────────────────

OUT_DIR = os.path.join(os.path.dirname(__file__), "screenshots")
os.makedirs(OUT_DIR, exist_ok=True)

CROWNS = [
    ("crown_s1.png", draw_crown_s1, "Three-point Crown"),
    ("crown_s2.png", draw_crown_s2, "Five-point Crown"),
    ("crown_s3.png", draw_crown_s3, "King's Cross Crown"),
    ("crown_s4.png", draw_crown_s4, "Spiked Diadem"),
    ("crown_s5.png", draw_crown_s5, "Three-bump Crown"),
]


def main():
    screen = pygame.Surface((W, H))
    for fname, drawer, label in CROWNS:
        draw_bg(screen)
        draw_leaderboard_variant(
            screen, title_t=1.4, scores=SCORES,
            player_rank=6, variant=6, crown_drawer=drawer)
        out = os.path.join(OUT_DIR, fname)
        pygame.image.save(screen, out)
        print(f"saved {out}  ({label})")


if __name__ == "__main__":
    main()
