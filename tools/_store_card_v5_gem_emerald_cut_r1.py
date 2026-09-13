"""Round-1 render sheet for the emerald-cut gem badge concept (iteration 2).

Monkey-patches store_cards.facet_gem with a rectangular step-cut stone —
a stretched octagon (taller than wide) rendered as concentric stepped bands
of eight trapezoid facets around a flat table. Value is stepped by a hard
per-ring brightness lift so the steps read as a stair even at badge scale,
with a left/right directional bias and a wide horizontal hall-of-mirrors
flash standing in for the classic point specular. Renders it in-context on
two full v5 cards plus an 8x zoomed 4-tier gem strip. Review-only tooling —
never imported by the game.
"""
import os
import sys
import math

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, "/home/user/skybit")

import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

import game.store_cards as sc
from game.draw import lerp_color, NEAR_BLACK, WHITE
from game.hud import _font as hud_font


RARITY_TIERS = [
    ("common",    (214, 206, 230), (78,  74, 112)),
    ("rare",      (108, 188, 252), (24,  78, 142)),
    ("epic",      (194, 122, 248), (80,  34, 126)),
    ("legendary", (255, 202, 104), (150, 92,  22)),
]
SID_PRIMARY   = "skin_mummy"    # EPIC
SID_SECONDARY = "skin_kitsune"  # LEGENDARY
CARD_W = sc.CARD_W * sc.SS     # 324
GEM_R  = sc.m(sc.GEM_R + 3)    # 22


def _tier_gf(base):
    # Brighter tiers earn a hotter reflected-fill + flash so legendary reads as
    # the richest stone; muted low tiers stay restrained.
    if base == (214, 206, 230): return 0.55
    if base == (108, 188, 252): return 0.70
    if base == (194, 122, 248): return 0.85
    if base == (255, 202, 104): return 1.00
    return 0.85


def make_oct(cx, cy, hw, hh, c, scale=1.0):
    """Stretched octagon: hw=half-width, hh=half-height, c=chamfer.
    Returns 8-vertex polygon (CW). Scale shrinks about (cx,cy)."""
    hw, hh, c = hw * scale, hh * scale, c * scale
    return [
        (cx - (hw - c), cy - hh), (cx + (hw - c), cy - hh),  # top edge
        (cx + hw, cy - (hh - c)), (cx + hw, cy + (hh - c)),   # right edge
        (cx + (hw - c), cy + hh), (cx - (hw - c), cy + hh),   # bottom edge
        (cx - hw, cy + (hh - c)), (cx - hw, cy - (hh - c)),   # left edge
    ]


def my_facet_gem(surf, cx, cy, r, base, deep, mystery=False):
    """Emerald-cut: a stretched step-cut octagon (taller than wide). Two
    concentric bands of eight trapezoid facets stair down to a flat table.
    Each facet is shaded by its outer-edge normal off ONE top-left key light,
    then the inner band gets a hard brightness lift so the steps read as a
    stair at badge scale — an emerald cut is all about that stacked-mirror
    stair, not sparkle. A left/right directional bias and a wide horizontal
    flash finish it; mystery owns red so it claims NO tier."""
    if mystery:
        base = (244, 96, 96)          # mystery owns red so it claims NO tier
        deep = (120, 22, 26)

    gf = _tier_gf(base)

    # Value stops — hue-preserving floor so a facet never crushes to black.
    t_dk    = lerp_color(deep, base, 0.18)      # shadow floor
    t_mid   = base
    t_hi    = lerp_color(base, WHITE, 0.55)
    t_table = lerp_color(base, WHITE, 0.50)
    warm    = lerp_color(base, (255, 238, 206), 0.5)
    t_key   = lerp_color(deep, NEAR_BLACK, 0.5)

    def shade(nx, ny):
        d = nx * (-0.7071) + ny * (-0.7071)     # primary top-left light
        f = (d + 1) / 2
        if f < 0.5:
            col = lerp_color(t_dk, t_mid, f * 2)
        else:
            col = lerp_color(t_mid, t_hi, (f - 0.5) * 2)
        # reflected warm secondary from lower-right so shadowed steps keep life
        d2 = nx * 0.5 + ny * 0.5
        col = lerp_color(col, warm, 0.12 * max(0.0, (d2 + 1) / 2) * gf)
        return col

    # ── seat: a dark well + faint tier ring so the stone reads on any ground ──
    seat_r = r + sc.m(4)
    seat_sz = r * 2 + sc.m(10)
    seat = pygame.Surface((seat_sz, seat_sz), pygame.SRCALPHA)
    sc_off = r + sc.m(5)
    pygame.draw.circle(seat, (0, 0, 0, 175), (sc_off, sc_off), seat_r)
    pygame.draw.circle(seat, (*base, 100), (sc_off, sc_off), seat_r, max(1, sc.m(0.8)))
    surf.blit(seat, (cx - sc_off, cy - sc_off))

    # ── inner glow: restrained so the bloom never blows out the step stair ──
    sc.soft_glow(surf, cx, cy, int(r * 0.5), base, int(60 * gf))

    # ── stretched-octagon step cut: outer girdle → ring → table ──
    hw = int(r * 0.70)
    hh = r
    c  = int(r * 0.32)
    oct0 = make_oct(cx, cy, hw, hh, c, 1.00)  # outer girdle
    oct1 = make_oct(cx, cy, hw, hh, c, 0.72)  # inner ring 1
    oct2 = make_oct(cx, cy, hw, hh, c, 0.46)  # inner ring 2 / table

    def band(oct_outer, oct_inner, lift):
        for i in range(8):
            a  = oct_outer[i]
            b  = oct_outer[(i + 1) % 8]
            ib = oct_inner[(i + 1) % 8]
            ia = oct_inner[i]
            # outward normal = center → mid of the outer edge
            mx = (a[0] + b[0]) / 2 - cx
            my = (a[1] + b[1]) / 2 - cy
            ml = math.hypot(mx, my) or 1
            col = shade(mx / ml, my / ml)
            if lift:
                col = lerp_color(col, t_hi, lift)   # hard stair-step read
            # left steps face the light warmer, right steps sink into shadow
            if i in (6, 7):
                bias = 20
            elif i in (2, 3):
                bias = -20
            else:
                bias = 0
            if bias:
                col = tuple(max(0, min(255, v + bias)) for v in col)
            pygame.draw.polygon(surf, col, [a, b, ib, ia])

    band(oct0, oct1, 0.0)     # outer band — full value range
    band(oct1, oct2, 0.42)    # inner band — hard lift makes the stair legible

    # ── table: the flat top, brightest ──
    pygame.draw.polygon(surf, t_table, oct2)

    # ── keylines: crisp the steps + rim, composited so alpha reads over facets ──
    over = pygame.Surface((seat_sz, seat_sz), pygame.SRCALPHA)
    ox, oy = sc_off, sc_off
    def shift(poly):
        return [(x - cx + ox, y - cy + oy) for (x, y) in poly]
    for ring in (oct0, oct1, oct2):
        pygame.draw.polygon(over, (*t_key, 200), shift(ring), 1)
    rim_col = lerp_color(base, WHITE, 0.4)
    pygame.draw.polygon(over, (*rim_col, 255), shift(oct0), 1)
    surf.blit(over, (cx - ox, cy - oy))

    # ── horizontal flash: the emerald-cut hall-of-mirrors, restrained additive ──
    fx, fy = cx, cy - int(r * 0.35)
    frx, fry = max(1, int(r * 0.35)), max(1, int(r * 0.08))
    flash = pygame.Surface((frx * 2 + 2, fry * 2 + 2), pygame.SRCALPHA)
    pygame.draw.ellipse(flash, (255, 255, 255, int(170 * gf)),
                        (1, 1, frx * 2, fry * 2))
    surf.blit(flash, (fx - frx - 1, fy - fry - 1), special_flags=pygame.BLEND_ADD)

    pr = max(1, int(r * 0.06))
    pip = pygame.Surface((pr * 2 + 2, pr * 2 + 2), pygame.SRCALPHA)
    pygame.draw.circle(pip, (255, 255, 255, 255), (pr + 1, pr + 1), pr)
    surf.blit(pip, (fx - pr - 1, fy - pr - 1), special_flags=pygame.BLEND_ADD)


sc.facet_gem = my_facet_gem   # monkey-patch BEFORE any draw_card call


def render_card(sid):
    ch = sc.CARD_H * sc.SS
    surf = pygame.Surface((CARD_W, ch + 16), pygame.SRCALPHA)
    rect = pygame.Rect(sc.m(sc._INSET), sc.m(sc._INSET),
                       CARD_W - 2 * sc.m(sc._INSET),
                       ch - 2 * sc.m(sc._INSET))
    sc.draw_card(surf, sid, rect, equipped=False, secret=False,
                 variant=sc.PRICE_VARIANT)
    return surf


def render_gem(base, deep):
    sz = (GEM_R + 4) * 2
    g = pygame.Surface((sz, sz), pygame.SRCALPHA)
    my_facet_gem(g, sz // 2, sz // 2, GEM_R, base, deep)
    return g


def main():
    out_dir = "/home/user/skybit/docs/store_card_v5_gem_badge_r2/emerald-cut"
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "round_1.png")

    pad = 28
    gap = 24
    header_h = 40

    cards = [render_card(SID_PRIMARY), render_card(SID_SECONDARY)]
    cw, chh = cards[0].get_size()
    row1_w = cw * 2 + gap
    row1_y = header_h + pad

    zoom = 8
    gsz = render_gem((0, 0, 0), (0, 0, 0)).get_size()[0]
    gz = gsz * zoom
    label_h = 24
    row2_y = row1_y + chh + gap * 2
    row2_w = gz * 4 + gap * 3

    canvas_w = pad * 2 + max(row1_w, row2_w)
    canvas_h = row2_y + gz + label_h + pad

    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill((8, 8, 20))

    hf = hud_font(26)
    lf = hud_font(18)

    header = hf.render("gem badge — emerald-cut r1", True, (236, 232, 250))
    canvas.blit(header, (pad, pad // 2 + 4))

    # Row 1 — full cards, centred
    x = pad + (max(row1_w, row2_w) - row1_w) // 2
    for card in cards:
        canvas.blit(card, (x, row1_y))
        x += cw + gap

    # Row 2 — 8x gem strip with tier labels
    x = pad + (max(row1_w, row2_w) - row2_w) // 2
    for name, base, deep in RARITY_TIERS:
        gem = render_gem(base, deep)
        big = pygame.transform.scale(gem, (gz, gz))
        canvas.blit(big, (x, row2_y))
        lbl = lf.render(name, True, (210, 206, 226))
        canvas.blit(lbl, (x + (gz - lbl.get_width()) // 2, row2_y + gz + 4))
        x += gz + gap

    pygame.image.save(canvas, out)
    print("saved", out, canvas.get_size())

    # ── sanity: gem centre column must never crush to pure black ──
    probe = render_gem((194, 122, 248), (80, 34, 126))
    ccx = probe.get_width() // 2
    px = probe.get_at((ccx, 19))
    print("probe pixel at (cx,19):", tuple(px))
    assert (px[0], px[1], px[2]) != (0, 0, 0), "gem crushed to pure black"
    print("sanity OK — reflected-light floor holds")


if __name__ == "__main__":
    main()
