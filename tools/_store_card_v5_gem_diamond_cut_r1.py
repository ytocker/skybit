"""Round-1 render sheet for the diamond-cut gem badge concept (iteration 2).

Monkey-patches store_cards.facet_gem with a point-up rhombus/lozenge stone —
four kite crown facets tiling a ring around a diamond table — value-stepped
off one top-left light with a warm reflected fill, a dark seat, a rim keyline,
and a dual specular (soft lens + hot pip). Renders it in-context on two full
v5 cards plus an 8x zoomed 4-tier gem strip. Review-only tooling — never
imported by the game.
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
    # Brighter tiers earn a hotter reflected-fill + specular so legendary reads
    # as the richest stone; muted low tiers stay restrained.
    if base == (214, 206, 230): return 0.55
    if base == (108, 188, 252): return 0.70
    if base == (194, 122, 248): return 0.85
    if base == (255, 202, 104): return 1.00
    return 0.85


def my_facet_gem(surf, cx, cy, r, base, deep, mystery=False):
    """Diamond-cut: a point-up rhombus (taller than wide) cut into four kite
    crown facets that tile the ring between an outer girdle and a diamond
    table. Each kite is shaded by its edge-midpoint normal off one top-left
    key light, with a warm reflected secondary from the lower-right so the
    stone never goes flat."""
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
        # reflected secondary from lower-right so shadowed facets keep life
        d2 = nx * 0.5 + ny * 0.5
        f2 = max(0.0, (d2 + 1) / 2)
        col = lerp_color(col, warm, 0.12 * f2 * gf)
        return col

    # ── seat: a dark well + faint tier ring so the stone reads on any ground ──
    seat_r = r + sc.m(4)
    seat_sz = r * 2 + sc.m(10)
    seat = pygame.Surface((seat_sz, seat_sz), pygame.SRCALPHA)
    sc_off = r + sc.m(5)
    pygame.draw.circle(seat, (0, 0, 0, 175), (sc_off, sc_off), seat_r)
    pygame.draw.circle(seat, (*base, 100), (sc_off, sc_off), seat_r, max(1, sc.m(0.8)))
    surf.blit(seat, (cx - sc_off, cy - sc_off))

    # ── inner glow: a soft tier bloom under the facets ──
    sc.soft_glow(surf, cx, cy, int(r * 0.5), base, int(80 * gf))

    # ── girdle + table corners (point-up rhombus, taller than wide) ──
    N = (cx,                 cy - r)
    E = (cx + int(r * 0.66), cy)
    S = (cx,                 cy + r)
    W = (cx - int(r * 0.66), cy)

    tN = (cx,                  cy - int(r * 0.30))
    tE = (cx + int(r * 0.198), cy)
    tS = (cx,                  cy + int(r * 0.30))
    tW = (cx - int(r * 0.198), cy)

    def unit_mid(a, b):
        mx = (a[0] + b[0]) / 2 - cx
        my = (a[1] + b[1]) / 2 - cy
        ml = math.hypot(mx, my) or 1
        return mx / ml, my / ml

    # Four kite crown facets fully tiling the crown ring.
    kites = [
        ([W, N, tN, tW], unit_mid(W, N)),   # top-left, most lit
        ([N, E, tE, tN], unit_mid(N, E)),   # top-right
        ([E, S, tS, tE], unit_mid(E, S)),   # bottom-right, darkest
        ([S, W, tW, tS], unit_mid(S, W)),   # bottom-left
    ]
    for quad, (nx, ny) in kites:
        pygame.draw.polygon(surf, shade(nx, ny), quad)

    # ── seams: outer corner -> table corner ──
    seam_w = max(1, sc.m(0.4))
    for outer, inner in ((W, tW), (N, tN), (E, tE), (S, tS)):
        pygame.draw.line(surf, (*t_key, 190), outer, inner, seam_w)

    # ── table: the flat top, brightest ──
    pygame.draw.polygon(surf, t_table, [tN, tE, tS, tW])

    # ── rim: silhouette keyline so the edge stays defined ──
    rim_col = lerp_color(base, WHITE, 0.4)
    pygame.draw.polygon(surf, rim_col, [N, E, S, W], max(1, sc.m(0.6)))

    # ── dual specular: soft lens + hot pip, both additive ──
    lx, ly = cx - int(r * 0.26), cy - int(r * 0.26)
    lrx, lry = max(1, int(r * 0.14)), max(1, int(r * 0.10))
    lens = pygame.Surface((lrx * 2 + 2, lry * 2 + 2), pygame.SRCALPHA)
    pygame.draw.ellipse(lens, (255, 255, 255, int(200 * gf)),
                        (1, 1, lrx * 2, lry * 2))
    surf.blit(lens, (lx - lrx - 1, ly - lry - 1), special_flags=pygame.BLEND_ADD)

    pr = max(1, int(r * 0.08))
    px, py = cx - int(r * 0.34), cy - int(r * 0.34)
    pip = pygame.Surface((pr * 2 + 2, pr * 2 + 2), pygame.SRCALPHA)
    pygame.draw.circle(pip, (255, 255, 255, 255), (pr + 1, pr + 1), pr)
    surf.blit(pip, (px - pr - 1, py - pr - 1), special_flags=pygame.BLEND_ADD)


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
    out_dir = "/home/user/skybit/docs/store_card_v5_gem_badge_r2/diamond-cut"
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

    header = hf.render("gem badge — diamond-cut r1", True, (236, 232, 250))
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

    # ── sanity: gem centre column must never be pure black (reflected floor) ──
    probe = render_gem((194, 122, 248), (80, 34, 126))
    ccx = probe.get_width() // 2
    px = probe.get_at((ccx, 19))
    print("probe pixel at (cx,19):", tuple(px))
    assert (px[0], px[1], px[2]) != (0, 0, 0), "gem crushed to pure black"
    print("sanity OK — reflected-light floor holds")


if __name__ == "__main__":
    main()
