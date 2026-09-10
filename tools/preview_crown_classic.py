"""Round 4 crown previews — five classic, royal designs.

Rounds 2 (R1-R5) and 3 (G1-G5) both rejected — too cartoony, then
too maximalist. User asked for "more classic and royal". This round
pulls back on the ornament budget and leans into heraldic vocabulary:
fleur-de-lis, strawberry leaves, crosses pattée, single jeweled bands
with 2 simple arches. Less halo, less spikes, no fur trim — just the
sort of crown you'd see in a coat of arms.

Renders:
  crown_c1.png — Closed Imperial   (band + 2 arches + cross orb)
  crown_c2.png — Royal Diadem      (band + fleur-de-lis alternating with pearl spikes)
  crown_c3.png — Tudor Crown       (band + alternating crosses + leaves + 2 arches)
  crown_c4.png — Heraldic Lily     (band + 5 fleur-de-lis, no top)
  crown_c5.png — Princess Coronet  (band + 5 strawberry leaves + pearls between)

Run from repo root:
  python3 tools/preview_crown_classic.py
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
    GOLD_HI, GOLD, GOLD_LO, GOLD_DEEP, VELVET, VELVET_DK,
    PEARL, PEARL_SH, RUBY, RUBY_HI, SAPPHIRE, SAPPHIRE_HI,
    EMERALD, EMERALD_HI, DARK_GOLD, WHITE_HI,
    _oversampled, _with_shadow, _gold_grad_rect, _quad_bezier,
    _gem, _maltese_cross,
)


# ── Heraldic ornament helpers ──────────────────────────────────────────────

def _fleur_de_lis(surf, cx, base_y, w, h):
    """Stylized fleur-de-lis: tall centre petal + two side petals curving
    outward + horizontal binding bar. Rises from base_y (the band top),
    symmetric about cx. `w` is total width, `h` is height above base."""
    half = w // 2
    body_w = max(2, w // 5)

    # Centre petal: tall pointed triangle
    c_tip = (cx, base_y - h)
    c_l   = (cx - body_w, base_y)
    c_r   = (cx + body_w, base_y)
    pygame.draw.polygon(surf, GOLD_DEEP,
                        [(c_tip[0], c_tip[1] + 1),
                         (c_l[0] - 1, c_l[1] + 1),
                         (c_r[0] + 1, c_r[1] + 1)])
    pygame.draw.polygon(surf, GOLD_LO, [c_tip, c_l, c_r])
    pygame.draw.polygon(surf, GOLD, [c_tip, c_l, (cx, base_y)])
    pygame.draw.line(surf, GOLD_HI, c_tip, (cx - 1, base_y - h // 2),
                     max(1, w // 12 + 1))

    # Left side petal: pointed outward + downward
    l_tip   = (cx - half, base_y - h * 2 // 3)
    l_inner = (cx - body_w, base_y - h // 3)
    l_base  = (cx - body_w, base_y)
    pygame.draw.polygon(surf, GOLD_DEEP,
                        [(l_tip[0] - 1, l_tip[1] + 1),
                         (l_inner[0], l_inner[1] + 1),
                         (l_base[0] - 1, l_base[1] + 1)])
    pygame.draw.polygon(surf, GOLD_LO, [l_tip, l_inner, l_base])

    # Right side petal: mirror
    r_tip   = (cx + half, base_y - h * 2 // 3)
    r_inner = (cx + body_w, base_y - h // 3)
    r_base  = (cx + body_w, base_y)
    pygame.draw.polygon(surf, GOLD_DEEP,
                        [(r_tip[0] + 1, r_tip[1] + 1),
                         (r_inner[0], r_inner[1] + 1),
                         (r_base[0] + 1, r_base[1] + 1)])
    pygame.draw.polygon(surf, GOLD_LO, [r_tip, r_inner, r_base])

    # Horizontal binding bar around the lower third
    bar_y = base_y - h * 2 // 5
    bar_h = max(2, h // 8)
    pygame.draw.rect(surf, GOLD_DEEP,
                     (cx - half + 1, bar_y + 1, w - 2, bar_h),
                     border_radius=bar_h // 2)
    pygame.draw.rect(surf, GOLD,
                     (cx - half, bar_y, w, bar_h),
                     border_radius=bar_h // 2)


def _strawberry_leaf(surf, cx, base_y, w, h):
    """3-lobed strawberry leaf — heraldic coronet ornament. Centre lobe
    tallest, two side lobes shorter and angled outward."""
    half = w // 2
    body_w = max(1, w // 5)

    # Centre lobe — tall narrow triangle
    c_tip = (cx, base_y - h)
    c_l = (cx - body_w, base_y - h // 3)
    c_r = (cx + body_w, base_y - h // 3)
    pygame.draw.polygon(surf, GOLD_DEEP,
                        [(c_tip[0], c_tip[1] + 1),
                         (c_l[0] - 1, c_l[1] + 1),
                         (c_r[0] + 1, c_r[1] + 1)])
    pygame.draw.polygon(surf, GOLD_LO, [c_tip, c_l, c_r])
    pygame.draw.polygon(surf, GOLD, [c_tip, c_l, (cx, base_y - h // 3)])

    # Left lobe — short, angled outward
    side_h = int(h * 0.55)
    l_tip = (cx - half, base_y - side_h)
    l_in  = (cx - body_w, base_y - h // 4)
    l_out = (cx - half, base_y)
    pygame.draw.polygon(surf, GOLD_DEEP,
                        [(l_tip[0] - 1, l_tip[1] + 1),
                         (l_in[0], l_in[1] + 1),
                         (l_out[0] - 1, l_out[1])])
    pygame.draw.polygon(surf, GOLD_LO, [l_tip, l_in, l_out])

    # Right lobe — mirror
    r_tip = (cx + half, base_y - side_h)
    r_in  = (cx + body_w, base_y - h // 4)
    r_out = (cx + half, base_y)
    pygame.draw.polygon(surf, GOLD_DEEP,
                        [(r_tip[0] + 1, r_tip[1] + 1),
                         (r_in[0], r_in[1] + 1),
                         (r_out[0] + 1, r_out[1])])
    pygame.draw.polygon(surf, GOLD_LO, [r_tip, r_in, r_out])


def _cross_pattee(surf, cx, base_y, size, s):
    """Cross with flared arms (heraldic "cross pattée"), rising from
    base_y. Size is total height of the cross."""
    h = size
    arm_thick = max(2, s)
    flare = arm_thick + max(1, s // 2)
    bar_y = base_y - h * 5 // 8

    # Vertical bar — shadow
    pygame.draw.rect(surf, GOLD_DEEP,
                     (cx - arm_thick // 2 + 1, base_y - h + 1,
                      arm_thick, h))
    # Vertical bar — body
    pygame.draw.rect(surf, GOLD,
                     (cx - arm_thick // 2, base_y - h, arm_thick, h))
    # Horizontal bar — shadow
    pygame.draw.rect(surf, GOLD_DEEP,
                     (cx - h // 2 + 1, bar_y + 1, h, arm_thick))
    pygame.draw.rect(surf, GOLD,
                     (cx - h // 2, bar_y, h, arm_thick))
    # Flared tips on all four arms
    pygame.draw.rect(surf, GOLD,
                     (cx - flare // 2, base_y - h, flare,
                      max(1, arm_thick // 2)))
    pygame.draw.rect(surf, GOLD,
                     (cx - flare // 2, base_y - max(1, arm_thick // 2),
                      flare, max(1, arm_thick // 2)))
    pygame.draw.rect(surf, GOLD,
                     (cx - h // 2, bar_y + arm_thick // 2 - flare // 2,
                      max(1, arm_thick // 2), flare))
    pygame.draw.rect(surf, GOLD,
                     (cx + h // 2 - max(1, arm_thick // 2),
                      bar_y + arm_thick // 2 - flare // 2,
                      max(1, arm_thick // 2), flare))


def _band(big, s, band_l, band_top, band_r, band_bot):
    """Reusable jeweled gold band: drop shadow + gradient fill + dark border."""
    pygame.draw.rect(big, GOLD_DEEP,
                     (band_l - 1, band_top + s,
                      band_r - band_l + 2, band_bot - band_top),
                     border_radius=s)
    _gold_grad_rect(big, (band_l, band_top, band_r - band_l, band_bot - band_top))
    pygame.draw.rect(big, DARK_GOLD,
                     (band_l, band_top, band_r - band_l, band_bot - band_top),
                     border_radius=s, width=max(1, s // 2))


def _two_arches(big, s, band_l, band_r, band_top, apex):
    """Pair of bezier-curve arches converging from band corners to apex.
    Multi-tone gold to give them depth."""
    arch_thick = max(s, 2)
    arches = [
        _quad_bezier((band_l + 3 * s, band_top),
                     (band_l + 4 * s, apex[1] + 3 * s), apex),
        _quad_bezier((band_r - 3 * s, band_top),
                     (band_r - 4 * s, apex[1] + 3 * s), apex),
    ]
    for arch in arches:
        pygame.draw.lines(big, GOLD_DEEP, False,
                          [(x, y + s) for x, y in arch], arch_thick + s)
        pygame.draw.lines(big, GOLD_LO, False, arch, arch_thick + 1)
        pygame.draw.lines(big, GOLD, False, arch, arch_thick)
    pygame.draw.lines(big, GOLD_HI, False,
                      [(x, y - 1) for x, y in
                       arches[0][: len(arches[0]) // 2 + 1]],
                      max(1, s // 2))


def _velvet_dome(big, dome_rect):
    """Velvet (deep red) ellipse with a darker right-shade for volume."""
    pygame.draw.ellipse(big, VELVET, dome_rect)
    pygame.draw.ellipse(big, VELVET_DK,
                        (dome_rect.x + dome_rect.w * 3 // 5,
                         dome_rect.y + dome_rect.h // 8,
                         dome_rect.w * 2 // 5,
                         dome_rect.h * 6 // 8))


# ── C1: Closed Imperial Crown ──────────────────────────────────────────────

def _draw_c1(big, s):
    """Classic British-imperial silhouette: jeweled band + velvet dome +
    two crossing arches + gold orb + cross at apex. ≈ 36 × 32 px."""
    bw, bh = big.get_width(), big.get_height()
    cx = bw // 2

    band_top, band_bot = 22 * s, 29 * s
    band_l = 2 * s
    band_r = bw - 2 * s
    _band(big, s, band_l, band_top, band_r, band_bot)
    # Three gems on the band: ruby — large sapphire — ruby (classical)
    band_cy = (band_top + band_bot) // 2
    _gem(big, band_l + 7 * s, band_cy, int(1.5 * s), RUBY, RUBY_HI)
    _gem(big, cx,              band_cy, int(2.0 * s), SAPPHIRE, SAPPHIRE_HI)
    _gem(big, band_r - 7 * s,  band_cy, int(1.5 * s), RUBY, RUBY_HI)

    # Velvet dome inside the arches
    dome_rect = pygame.Rect(cx - 12 * s, 8 * s, 24 * s, 15 * s)
    _velvet_dome(big, dome_rect)

    # Two arches converging at apex, gold orb + cross above
    apex = (cx, 7 * s)
    _two_arches(big, s, band_l, band_r, band_top, apex)
    _gem(big, apex[0], apex[1], int(1.8 * s), GOLD, GOLD_HI)
    _maltese_cross(big, apex[0], top_y=apex[1] - 6 * s, h=4 * s,
                   thick=s, col=GOLD)


def draw_crown_c1(surf, cx, cy):
    bw, bh = 36, 32
    img = _with_shadow(_oversampled(_draw_c1, bw, bh, 3))
    surf.blit(img, (cx - bw // 2, cy - bh // 2 + 2))


# ── C2: Royal Diadem (open, alternating fleur-de-lis + pearl spikes) ───────

def _draw_c2(big, s):
    """Open coronet: gold band + 3 fleur-de-lis alternating with 2
    pearl-tipped spikes along the top. ≈ 40 × 24 px."""
    bw, bh = big.get_width(), big.get_height()
    cx = bw // 2

    band_top, band_bot = 15 * s, 22 * s
    band_l = 2 * s
    band_r = bw - 2 * s
    _band(big, s, band_l, band_top, band_r, band_bot)
    # Three small gems on the band
    band_cy = (band_top + band_bot) // 2
    _gem(big, band_l + 6 * s, band_cy, int(1.2 * s), EMERALD, EMERALD_HI)
    _gem(big, cx,              band_cy, int(1.6 * s), RUBY, RUBY_HI)
    _gem(big, band_r - 6 * s,  band_cy, int(1.2 * s), EMERALD, EMERALD_HI)

    # 5 ornaments along the top: fleur, spike, fleur, spike, fleur
    ornament_xs = [cx - 13 * s, cx - 6 * s, cx, cx + 6 * s, cx + 13 * s]
    for i, ox in enumerate(ornament_xs):
        if i % 2 == 0:
            # Fleur-de-lis ornament
            _fleur_de_lis(big, ox, band_top + 1, 4 * s, 9 * s)
        else:
            # Pearl-tipped spike
            tip = (ox, band_top - 7 * s)
            l   = (ox - max(1, int(0.8 * s)), band_top)
            r   = (ox + max(1, int(0.8 * s)), band_top)
            pygame.draw.polygon(big, GOLD_DEEP,
                                [(tip[0], tip[1] + 1),
                                 (l[0] - 1, l[1] + 1),
                                 (r[0] + 1, r[1] + 1)])
            pygame.draw.polygon(big, GOLD_LO, [tip, l, r])
            pygame.draw.polygon(big, GOLD,
                                [tip, l, (ox, band_top)])
            pygame.draw.circle(big, PEARL_SH, (tip[0], tip[1] - s + 1), s + 1)
            pygame.draw.circle(big, PEARL, (tip[0], tip[1] - s), s)
            pygame.draw.circle(big, WHITE_HI, (tip[0] - 1, tip[1] - s - 1),
                               max(1, s // 2))


def draw_crown_c2(surf, cx, cy):
    bw, bh = 40, 24
    img = _with_shadow(_oversampled(_draw_c2, bw, bh, 3))
    surf.blit(img, (cx - bw // 2, cy - bh // 2 + 2))


# ── C3: Tudor Crown ────────────────────────────────────────────────────────

def _draw_c3(big, s):
    """Tudor-style closed crown: band + alternating crosses pattée and
    strawberry leaves + 2 arches + apex cross. ≈ 40 × 32 px."""
    bw, bh = big.get_width(), big.get_height()
    cx = bw // 2

    band_top, band_bot = 22 * s, 29 * s
    band_l = 2 * s
    band_r = bw - 2 * s
    _band(big, s, band_l, band_top, band_r, band_bot)
    # 4 evenly spaced gems on the band
    band_cy = (band_top + band_bot) // 2
    gems = [(RUBY, RUBY_HI), (SAPPHIRE, SAPPHIRE_HI),
            (RUBY, RUBY_HI), (EMERALD, EMERALD_HI)]
    for i, (gc, gh) in enumerate(gems):
        gx = band_l + (i + 1) * (band_r - band_l) // 5
        _gem(big, gx, band_cy, int(1.2 * s), gc, gh)

    # 5 ornaments along band top: cross, leaf, cross, leaf, cross
    ornament_xs = [band_l + 4 * s, band_l + 10 * s, cx,
                   band_r - 10 * s, band_r - 4 * s]
    for i, ox in enumerate(ornament_xs):
        if i % 2 == 0:
            _cross_pattee(big, ox, band_top, 5 * s, s)
        else:
            _strawberry_leaf(big, ox, band_top, 4 * s, 5 * s)

    # Velvet dome
    dome_rect = pygame.Rect(cx - 12 * s, 10 * s, 24 * s, 13 * s)
    _velvet_dome(big, dome_rect)

    # Two arches + apex cross
    apex = (cx, 7 * s)
    _two_arches(big, s, band_l + 3 * s, band_r - 3 * s, band_top - 1 * s, apex)
    _gem(big, apex[0], apex[1], int(1.5 * s), GOLD, GOLD_HI)
    _maltese_cross(big, apex[0], top_y=apex[1] - 5 * s, h=4 * s,
                   thick=s, col=GOLD)


def draw_crown_c3(surf, cx, cy):
    bw, bh = 40, 32
    img = _with_shadow(_oversampled(_draw_c3, bw, bh, 3))
    surf.blit(img, (cx - bw // 2, cy - bh // 2 + 2))


# ── C4: Heraldic Lily Crown ────────────────────────────────────────────────

def _draw_c4(big, s):
    """5 fleur-de-lis along a plain jeweled band — straight out of a
    coat of arms. No arches, no top, just heraldic simplicity. ≈ 40 × 24 px."""
    bw, bh = big.get_width(), big.get_height()
    cx = bw // 2

    band_top, band_bot = 16 * s, 22 * s
    band_l = 2 * s
    band_r = bw - 2 * s
    _band(big, s, band_l, band_top, band_r, band_bot)
    # Single central ruby
    band_cy = (band_top + band_bot) // 2
    _gem(big, cx, band_cy, int(2.0 * s), RUBY, RUBY_HI)
    # Two side sapphires
    _gem(big, band_l + 5 * s, band_cy, int(1.0 * s), SAPPHIRE, SAPPHIRE_HI)
    _gem(big, band_r - 5 * s, band_cy, int(1.0 * s), SAPPHIRE, SAPPHIRE_HI)

    # 5 evenly spaced fleur-de-lis along the band top
    fleur_xs = [cx - 13 * s, cx - 6 * s, cx, cx + 6 * s, cx + 13 * s]
    # Centre tallest, sides slightly shorter — gives subtle hierarchy
    heights  = [7 * s,       9 * s,      11 * s, 9 * s,      7 * s]
    for ox, fh in zip(fleur_xs, heights):
        _fleur_de_lis(big, ox, band_top + 1, 4 * s, fh)


def draw_crown_c4(surf, cx, cy):
    bw, bh = 40, 24
    img = _with_shadow(_oversampled(_draw_c4, bw, bh, 3))
    surf.blit(img, (cx - bw // 2, cy - bh // 2 + 2))


# ── C5: Princess Coronet ───────────────────────────────────────────────────

def _draw_c5(big, s):
    """Low, wide coronet: 5 strawberry leaves with pearls between them
    over a jeweled band. Open at the top — duke/duchess heraldic style.
    ≈ 40 × 22 px."""
    bw, bh = big.get_width(), big.get_height()
    cx = bw // 2

    band_top, band_bot = 13 * s, 19 * s
    band_l = 2 * s
    band_r = bw - 2 * s
    _band(big, s, band_l, band_top, band_r, band_bot)
    # 3 small gems on band
    band_cy = (band_top + band_bot) // 2
    _gem(big, band_l + 5 * s, band_cy, int(1.0 * s), EMERALD, EMERALD_HI)
    _gem(big, cx,              band_cy, int(1.4 * s), RUBY, RUBY_HI)
    _gem(big, band_r - 5 * s,  band_cy, int(1.0 * s), EMERALD, EMERALD_HI)

    # 5 strawberry leaves along the band top
    leaf_xs = [cx - 13 * s, cx - 6 * s, cx, cx + 6 * s, cx + 13 * s]
    for ox in leaf_xs:
        _strawberry_leaf(big, ox, band_top + 1, 4 * s, 6 * s)

    # 4 pearls between leaves
    pearl_xs = [(leaf_xs[i] + leaf_xs[i + 1]) // 2 for i in range(4)]
    for px in pearl_xs:
        pygame.draw.circle(big, PEARL_SH, (px, band_top - s), s + 1)
        pygame.draw.circle(big, PEARL, (px, band_top - s - 1), s)
        pygame.draw.circle(big, WHITE_HI, (px - 1, band_top - s - 2),
                           max(1, s // 2))


def draw_crown_c5(surf, cx, cy):
    bw, bh = 40, 22
    img = _with_shadow(_oversampled(_draw_c5, bw, bh, 3))
    surf.blit(img, (cx - bw // 2, cy - bh // 2 + 2))


# ── Render ──────────────────────────────────────────────────────────────────

OUT_DIR = os.path.join(os.path.dirname(__file__), "screenshots")
os.makedirs(OUT_DIR, exist_ok=True)

CROWNS = [
    ("crown_c1.png", draw_crown_c1, "Closed Imperial"),
    ("crown_c2.png", draw_crown_c2, "Royal Diadem"),
    ("crown_c3.png", draw_crown_c3, "Tudor Crown"),
    ("crown_c4.png", draw_crown_c4, "Heraldic Lily"),
    ("crown_c5.png", draw_crown_c5, "Princess Coronet"),
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
