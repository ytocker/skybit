"""Round 7 — five elegant 3-peak king crowns + positioning fix.

User reaction to round 6 (simple): *"Garbage and don't even sit well
on the icon. Make something elegant, using 3 peaks suitable for
number 1!"*

Two complaints to address:

1. **Positioning** — the crown's bbox extended *below* its band, so a
   chunk of empty SRCALPHA territory landed inside the gold badge,
   visually pulling the crown DOWN into the badge instead of letting
   it sit ON it. Fix here: every `_draw_e*` places the band at the
   *bottom* of the bbox (band_bottom = bh) and every `draw_crown_e*`
   blits at `cy - bh + 4` so the band lands ~2 px into the badge top
   (firm seat, not hovering, not occluding the "1").

2. **Elegance** — 3 peaks, slim proportions, refined gem work, no
   maximalism. Variants vary the top ornament style:

   crown_e1.png — Slender Pearls   (3 narrow peaks, pearl on each tip,
                                    oval ruby on band)
   crown_e2.png — Royal Cross      (3 peaks, centre tallest topped with
                                    a Maltese cross, side gems)
   crown_e3.png — Diamond Trio     (3 peaks each with a kite-cut jewel —
                                    sapphire / ruby / sapphire)
   crown_e4.png — Triple Arch      (3 rounded arched peaks, centre tall,
                                    pearls in the cusps)
   crown_e5.png — Triple Trefoil   (3 peaks topped with delicate trefoils,
                                    central ruby)

Same bolder pipeline as round 5: 2× oversample, NEAR_BLACK outlines,
two-stop GOLD_HI → GOLD_LO gradient, single dominant central gem.
"""

import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import math
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
    PEARL, PEARL_SH, WHITE_HI, _with_shadow, _aura,
)
from tools.preview_crown_kings import (
    NEAR_BLACK,
    _oversampled2, _band_outlined,
    _outlined_polygon, _outlined_gem,
    _outlined_maltese,
)


# Anchor shift: place band BOTTOM 4 px below the legacy cy so it
# overlaps the badge top by ~2 px (badge top = cy + 2 in the
# leaderboard's coordinate system).
_BAND_ANCHOR_DY = 4


def _blit_anchored(surf, img, cx, cy, bw, bh):
    surf.blit(img, (cx - bw // 2, cy - bh + _BAND_ANCHOR_DY))


# Sparkle positions as (x_frac, y_frac) offsets from the crown centre,
# expressed as fractions of (bw / 2, bh / 2). Four sparkle accents
# surround the crown — two upper outer, two flanking the band.
_SPARKLE_POS = [(-1.05, -0.50), (1.05, -0.50),
                (-0.85,  0.30), (0.85,  0.30)]


def _aura_behind(big, s, cx, cy):
    """Soft 3-stop gold halo behind the crown. Subtle (max alpha 95)
    so the crown silhouette still dominates."""
    _aura(big, cx, cy,
          radii=[16 * s, 11 * s, 7 * s],
          alphas=[40, 65, 95])


def _sheen(big, s, band_top, band_bot, band_l, band_r):
    """Single thin GOLD_HI horizontal stripe at ~25 % down the band —
    sells the gold as metal rather than flat paint."""
    y = band_top + (band_bot - band_top) // 4
    pygame.draw.line(big, GOLD_HI,
                     (band_l + 2 * s, y), (band_r - 2 * s, y),
                     max(1, s // 2))


def _sparkle(big, s, cx, cy, size):
    """Tiny 4-armed sparkle: a small white plus-sign with a centre dot."""
    pygame.draw.line(big, WHITE_HI,
                     (cx - size, cy), (cx + size, cy),
                     max(1, s // 2))
    pygame.draw.line(big, WHITE_HI,
                     (cx, cy - size), (cx, cy + size),
                     max(1, s // 2))
    pygame.draw.circle(big, WHITE_HI, (cx, cy), max(1, s // 2))


def _scatter_sparkles(big, s, bw, bh):
    """Place 4 sparkles around the crown at fixed fractional offsets."""
    cx_pix = bw // 2
    cy_pix = bh // 2
    for x_frac, y_frac in _SPARKLE_POS:
        sx = int(cx_pix + x_frac * (bw // 2))
        sy = int(cy_pix + y_frac * (bh // 2))
        # Clamp so the sparkle sits inside the bbox
        sx = max(2 * s, min(bw - 2 * s, sx))
        sy = max(2 * s, min(bh - 2 * s, sy))
        _sparkle(big, s, sx, sy, 2 * s)


def _pearl(big, s, cx, cy, r):
    """Outlined pearl with white highlight, used on peak tips."""
    pygame.draw.circle(big, NEAR_BLACK, (cx, cy + 1), r + 1)
    pygame.draw.circle(big, PEARL_SH, (cx, cy + 1), r)
    pygame.draw.circle(big, PEARL, (cx, cy), r)
    pygame.draw.circle(big, WHITE_HI, (cx - max(1, r // 3),
                                       cy - max(1, r // 3)),
                       max(1, r // 2))


# ── E1: Slender Pearls ──────────────────────────────────────────────────────

def _draw_e1(big, s):
    """3 narrow tall peaks, pearl on each tip, oval ruby on band."""
    bw, bh = big.get_width(), big.get_height()
    cx = bw // 2

    # Aura behind the crown (drawn FIRST so everything lands on top)
    _aura_behind(big, s, cx, bh - 12 * s)

    # Band hugs the bottom of the bbox
    band_h = 8 * s
    band_top = bh - band_h
    band_bot = bh
    band_l = 3 * s
    band_r = bw - 3 * s
    _band_outlined(big, s, band_l, band_top, band_r, band_bot)
    _sheen(big, s, band_top, band_bot, band_l, band_r)

    # Single dominant oval ruby in the band centre
    band_cy = (band_top + band_bot) // 2
    pygame.draw.ellipse(big, NEAR_BLACK,
                        (cx - 4 * s, band_cy - 2 * s,
                         8 * s, 4 * s))
    pygame.draw.ellipse(big, RUBY,
                        (cx - int(3.5 * s), band_cy - int(1.7 * s),
                         7 * s, int(3.4 * s)))
    pygame.draw.ellipse(big, RUBY_HI,
                        (cx - int(2.5 * s), band_cy - 1 * s,
                         3 * s, int(1.5 * s)))

    # 3 slender peaks
    peak_xs = [cx - 14 * s, cx, cx + 14 * s]
    peak_pw = int(2.2 * s)
    peak_h = bh - band_h - 2 * s   # take all available height above the band
    for px in peak_xs:
        tip = (px, band_top - peak_h)
        l   = (px - peak_pw, band_top)
        r   = (px + peak_pw, band_top)
        _outlined_polygon(big, [tip, l, r], GOLD, GOLD_HI)

    # Pearl on each peak tip
    for px in peak_xs:
        tip_y = band_top - peak_h
        _pearl(big, s, px, tip_y + s, int(2 * s))

    _scatter_sparkles(big, s, bw, bh)


def draw_crown_e1(surf, cx, cy):
    bw, bh = 48, 36
    img = _with_shadow(_oversampled2(_draw_e1, bw, bh))
    _blit_anchored(surf, img, cx, cy, bw, bh)


# ── E2: Royal Cross ─────────────────────────────────────────────────────────

def _draw_e2(big, s):
    """3 peaks, centre tallest and topped with a Maltese cross. Side
    peaks have round sapphire gems."""
    bw, bh = big.get_width(), big.get_height()
    cx = bw // 2

    _aura_behind(big, s, cx, bh - 14 * s)

    band_h = 8 * s
    band_top = bh - band_h
    band_bot = bh
    band_l = 3 * s
    band_r = bw - 3 * s
    _band_outlined(big, s, band_l, band_top, band_r, band_bot)
    _sheen(big, s, band_top, band_bot, band_l, band_r)
    band_cy = (band_top + band_bot) // 2
    _outlined_gem(big, cx, band_cy, int(2 * s), RUBY, RUBY_HI)

    # Side peaks — shorter
    side_xs = [cx - 14 * s, cx + 14 * s]
    side_pw = 3 * s
    side_h = int(0.55 * (bh - band_h))
    for sx in side_xs:
        tip = (sx, band_top - side_h)
        l   = (sx - side_pw, band_top)
        r   = (sx + side_pw, band_top)
        _outlined_polygon(big, [tip, l, r], GOLD, GOLD_HI)
        _outlined_gem(big, sx, band_top - side_h - int(1.5 * s),
                      int(1.6 * s), SAPPHIRE, SAPPHIRE_HI)

    # Centre peak — taller, topped with a Maltese cross
    centre_pw = int(3.2 * s)
    centre_h = int(0.45 * (bh - band_h))
    c_tip = (cx, band_top - centre_h)
    c_l   = (cx - centre_pw, band_top)
    c_r   = (cx + centre_pw, band_top)
    _outlined_polygon(big, [c_tip, c_l, c_r], GOLD, GOLD_HI)
    # Small gold orb on the centre peak tip
    _outlined_gem(big, cx, c_tip[1] - int(1.3 * s),
                  int(1.4 * s), GOLD, GOLD_HI)
    # Maltese cross above the orb
    cross_top = c_tip[1] - int(2.6 * s) - int(0.55 * (bh - band_h) - centre_h)
    cross_top = max(s, cross_top)
    _outlined_maltese(big, s, cx,
                      top_y=cross_top,
                      h=bh - band_h - centre_h - 2 * s)

    _scatter_sparkles(big, s, bw, bh)


def draw_crown_e2(surf, cx, cy):
    bw, bh = 50, 40
    img = _with_shadow(_oversampled2(_draw_e2, bw, bh))
    _blit_anchored(surf, img, cx, cy, bw, bh)


# ── E3: Diamond Trio ────────────────────────────────────────────────────────

def _draw_e3(big, s):
    """3 peaks each topped with a kite-cut (diamond shape) gem.
    Sapphire / ruby / sapphire."""
    bw, bh = big.get_width(), big.get_height()
    cx = bw // 2

    _aura_behind(big, s, cx, bh - 12 * s)

    band_h = 8 * s
    band_top = bh - band_h
    band_bot = bh
    band_l = 3 * s
    band_r = bw - 3 * s
    _band_outlined(big, s, band_l, band_top, band_r, band_bot)
    _sheen(big, s, band_top, band_bot, band_l, band_r)
    band_cy = (band_top + band_bot) // 2
    _outlined_gem(big, cx, band_cy, int(1.8 * s), RUBY, RUBY_HI)

    peak_xs = [cx - 14 * s, cx, cx + 14 * s]
    peak_pw = int(2.6 * s)
    peak_h = bh - band_h - 6 * s  # leave room for the kite-cut gem above
    gem_cols = [(SAPPHIRE, SAPPHIRE_HI), (RUBY, RUBY_HI),
                (SAPPHIRE, SAPPHIRE_HI)]
    for px, (gc, gh) in zip(peak_xs, gem_cols):
        # Peak triangle
        tip = (px, band_top - peak_h)
        l   = (px - peak_pw, band_top)
        r   = (px + peak_pw, band_top)
        _outlined_polygon(big, [tip, l, r], GOLD, GOLD_HI)
        # Kite-cut gem above the peak tip
        gem_top   = (px, tip[1] - int(3.5 * s))
        gem_bot   = (px, tip[1] - int(0.5 * s))
        gem_left  = (px - int(1.8 * s), tip[1] - 2 * s)
        gem_right = (px + int(1.8 * s), tip[1] - 2 * s)
        _outlined_polygon(big,
                          [gem_top, gem_right, gem_bot, gem_left],
                          gc, gh)
        # Bright glint inside the gem
        pygame.draw.line(big, WHITE_HI,
                         (gem_top[0] - 1, gem_top[1] + 1),
                         (gem_top[0] - 1, gem_top[1] + int(2 * s)),
                         max(1, s // 2))

    _scatter_sparkles(big, s, bw, bh)


def draw_crown_e3(surf, cx, cy):
    bw, bh = 50, 36
    img = _with_shadow(_oversampled2(_draw_e3, bw, bh))
    _blit_anchored(surf, img, cx, cy, bw, bh)


# ── E4: Triple Arch ─────────────────────────────────────────────────────────

def _draw_e4(big, s):
    """3 rounded arched peaks (no sharp triangles). Central arch is
    tallest. Small pearls perch in the cusps between arches."""
    bw, bh = big.get_width(), big.get_height()
    cx = bw // 2

    _aura_behind(big, s, cx, bh - 12 * s)

    band_h = 8 * s
    band_top = bh - band_h
    band_bot = bh
    band_l = 3 * s
    band_r = bw - 3 * s

    # Draw arches FIRST (their bottom halves get covered by the band)
    # Side arches
    side_xs = [cx - 14 * s, cx + 14 * s]
    side_r = int(5.5 * s)
    for sx in side_xs:
        pygame.draw.circle(big, NEAR_BLACK, (sx, band_top), side_r + 1)
        pygame.draw.circle(big, GOLD_LO, (sx, band_top), side_r)
        pygame.draw.circle(big, GOLD, (sx, band_top), side_r - s)
        pygame.draw.circle(big, GOLD_HI,
                           (sx - 2 * s, band_top - 2 * s),
                           max(2, side_r // 3))
    # Central arch — taller, drawn as a vertical-stretch ellipse
    cen_w = 12 * s
    cen_h = int(7.5 * s)
    cen_top = band_top - cen_h
    pygame.draw.ellipse(big, NEAR_BLACK,
                        (cx - cen_w // 2 - 1, cen_top - 1,
                         cen_w + 2, cen_h * 2 + 2))
    pygame.draw.ellipse(big, GOLD_LO,
                        (cx - cen_w // 2, cen_top, cen_w, cen_h * 2))
    pygame.draw.ellipse(big, GOLD,
                        (cx - cen_w // 2 + s, cen_top + s,
                         cen_w - 2 * s, cen_h * 2 - 2 * s))
    pygame.draw.ellipse(big, GOLD_HI,
                        (cx - cen_w // 2 + int(1.5 * s),
                         cen_top + int(1.5 * s),
                         cen_w // 2, cen_h // 2))

    # Band over the bottom halves of the arches
    _band_outlined(big, s, band_l, band_top, band_r, band_bot)
    _sheen(big, s, band_top, band_bot, band_l, band_r)
    band_cy = (band_top + band_bot) // 2
    _outlined_gem(big, cx, band_cy, int(2 * s), RUBY, RUBY_HI)

    # Pearls in the cusps between arches
    cusp_xs = [(cx - 14 * s + cx) // 2, (cx + cx + 14 * s) // 2]
    for px in cusp_xs:
        _pearl(big, s, px, band_top - int(1.5 * s), int(1.6 * s))

    # Pearl on top of the central arch
    _pearl(big, s, cx, cen_top - int(0.5 * s), int(1.6 * s))
    # Tiny pearls on the side-arch tops
    for sx in side_xs:
        _pearl(big, s, sx, band_top - side_r - int(0.5 * s),
               int(1.3 * s))

    _scatter_sparkles(big, s, bw, bh)


def draw_crown_e4(surf, cx, cy):
    bw, bh = 50, 34
    img = _with_shadow(_oversampled2(_draw_e4, bw, bh))
    _blit_anchored(surf, img, cx, cy, bw, bh)


# ── E5: Triple Trefoil ──────────────────────────────────────────────────────

def _draw_e5(big, s):
    """3 peaks, each topped with a delicate trefoil (three-lobed
    ornament). Central peak tallest. Single ruby on band."""
    bw, bh = big.get_width(), big.get_height()
    cx = bw // 2

    _aura_behind(big, s, cx, bh - 12 * s)

    band_h = 8 * s
    band_top = bh - band_h
    band_bot = bh
    band_l = 3 * s
    band_r = bw - 3 * s
    _band_outlined(big, s, band_l, band_top, band_r, band_bot)
    _sheen(big, s, band_top, band_bot, band_l, band_r)
    band_cy = (band_top + band_bot) // 2
    _outlined_gem(big, cx, band_cy, int(2 * s), RUBY, RUBY_HI)

    side_xs = [cx - 15 * s, cx + 15 * s]
    side_h = int(0.6 * (bh - band_h))
    side_pw = int(2.4 * s)
    for sx in side_xs:
        tip = (sx, band_top - side_h)
        l   = (sx - side_pw, band_top)
        r   = (sx + side_pw, band_top)
        _outlined_polygon(big, [tip, l, r], GOLD, GOLD_HI)
        _draw_trefoil(big, s, sx, tip[1] - 1)

    centre_pw = int(2.6 * s)
    centre_h = int(0.95 * (bh - band_h))
    c_tip = (cx, band_top - centre_h)
    c_l   = (cx - centre_pw, band_top)
    c_r   = (cx + centre_pw, band_top)
    _outlined_polygon(big, [c_tip, c_l, c_r], GOLD, GOLD_HI)
    _draw_trefoil(big, s, cx, c_tip[1] - 1, big_=True)

    _scatter_sparkles(big, s, bw, bh)


def _draw_trefoil(big, s, cx, base_y, big_=False):
    """Three small gold lobes arranged in a trefoil cluster."""
    r = int(2 * s) if big_ else int(1.6 * s)
    # Top lobe
    pygame.draw.circle(big, NEAR_BLACK, (cx, base_y - 2 * r), r + 1)
    pygame.draw.circle(big, GOLD,       (cx, base_y - 2 * r), r)
    pygame.draw.circle(big, GOLD_HI,
                       (cx - max(1, r // 3), base_y - 2 * r - max(1, r // 3)),
                       max(1, r // 2))
    # Left + right lobes
    for dx in (-int(1.4 * r), int(1.4 * r)):
        pygame.draw.circle(big, NEAR_BLACK,
                           (cx + dx, base_y - r), r + 1)
        pygame.draw.circle(big, GOLD,
                           (cx + dx, base_y - r), r)
        pygame.draw.circle(big, GOLD_HI,
                           (cx + dx - max(1, r // 3),
                            base_y - r - max(1, r // 3)),
                           max(1, r // 2))


def draw_crown_e5(surf, cx, cy):
    bw, bh = 52, 36
    img = _with_shadow(_oversampled2(_draw_e5, bw, bh))
    _blit_anchored(surf, img, cx, cy, bw, bh)


# ── Render ──────────────────────────────────────────────────────────────────

OUT_DIR = os.path.join(os.path.dirname(__file__), "screenshots")
os.makedirs(OUT_DIR, exist_ok=True)

CROWNS = [
    ("crown_e1.png", draw_crown_e1, "Slender Pearls"),
    ("crown_e2.png", draw_crown_e2, "Royal Cross"),
    ("crown_e3.png", draw_crown_e3, "Diamond Trio"),
    ("crown_e4.png", draw_crown_e4, "Triple Arch"),
    ("crown_e5.png", draw_crown_e5, "Triple Trefoil"),
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
