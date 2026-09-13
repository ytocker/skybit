"""Round-2 render sheet for the improved-octagon gem badge concept.

Monkey-patches store_cards.facet_gem with an 8-gon stone that keeps the
original facet_gem's octagonal silhouette but eliminates its water-drop
defect: a portrait-biased girdle (hw<hh) cut into eight crown kite facets
that tile the ring around an octagonal table. Value-stepped off one
top-left light plus a warm lower-right reflected fill, with an explicit
anti-disc push and hard radial seams so the crown reads as eight distinct
stepped panels rather than a smooth gradient disc. Renders it in-context on
two full v5 cards plus an 8x zoomed 4-tier gem strip.
Review-only tooling — never imported by the game.
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
    """Improved-octagon: the original 8-gon silhouette with a portrait bias
    (hw<hh) so it reads taller-than-wide instead of a flat disc. Eight crown
    kite facets tile the ring between an octagonal girdle and an octagonal
    table. Each kite is shaded by its outer-edge-midpoint normal off one
    top-left key light, then an alternating push toward the shadow floor plus
    hard radial seams force the crown to read as eight stepped panels rather
    than a smooth gradient disc."""
    if mystery:
        base = (244, 96, 96)          # mystery owns red so it claims NO tier
        deep = (120, 22, 26)

    gf = _tier_gf(base)

    # Value stops — hue-preserving floor so a facet never crushes to black. The
    # floor is lifted well off the deep so the darkest facet glows with tier hue
    # rather than crushing to near-black mud.
    t_dk  = lerp_color(deep, base, 0.28)      # shadow floor
    t_mid = base
    # Crown high stop kept clearly below the table so no crown facet can rival
    # the table brightness — the table stays the single unambiguous bright zone.
    t_hi  = lerp_color(base, WHITE, 0.42)
    # Warm reflected tint: a hotter low-sun amber bounce so cool shadow facets
    # lean amber (R>=B) instead of settling into dead purple.
    warm  = lerp_color(base, (255, 200, 120), 0.5)
    t_key = lerp_color(deep, NEAR_BLACK, 0.5)

    def shade(nx, ny):
        d = nx * (-0.7071) + ny * (-0.7071)     # primary top-left light
        f = (d + 1) / 2
        if f < 0.5:
            col = lerp_color(t_dk, t_mid, f * 2)
        else:
            col = lerp_color(t_mid, t_hi, (f - 0.5) * 2)
        # reflected secondary from lower-right, warm so the SE/S-facing shadow
        # facets glow instead of reading dead purple
        d2 = nx * 0.5 + ny * 0.5
        f2 = max(0.0, (d2 + 1) / 2)
        col = lerp_color(col, warm, 0.24 * f2 * gf)
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
    sc.soft_glow(surf, cx, cy, int(r * 0.5), base, int(70 * gf))

    # ── girdle + table octagons (portrait bias: hw<hh reads taller-than-wide) ──
    hw = r * 0.92
    hh = r * 1.0
    thw = hw * 0.46
    thh = hh * 0.46

    g = []
    t = []
    for k in range(8):
        th = math.radians(22.5 + 45 * k)
        c, s = math.cos(th), math.sin(th)
        g.append((cx + hw * c, cy + hh * s))
        t.append((cx + thw * c, cy + thh * s))

    def unit_mid(a, b):
        mx = (a[0] + b[0]) / 2 - cx
        my = (a[1] + b[1]) / 2 - cy
        ml = math.hypot(mx, my) or 1
        return mx / ml, my / ml

    # ── eight crown kite facets fully tiling the crown ring ──
    for k in range(8):
        g0, g1 = g[k], g[(k + 1) % 8]
        t0, t1 = t[k], t[(k + 1) % 8]
        nx, ny = unit_mid(g0, g1)
        col = shade(nx, ny)
        # anti-disc: alternate a small extra push toward the shadow floor so no
        # two adjacent facets settle on the same value — the crown steps, not fades
        col = lerp_color(col, t_dk, 0.12 * (k % 2))
        pygame.draw.polygon(surf, col, [g0, g1, t1, t0])

    # ── hard radial seams: outer vertex -> table vertex on all 8 spokes so the
    # eight panels stay crisply divided ──
    seam_w = max(1, sc.m(0.5))
    for k in range(8):
        pygame.draw.line(surf, t_key, g[k], t[k], seam_w)

    # ── table: the flat top octagon, lifted to be the single brightest zone so
    # the eye lands there before any crown facet ──
    table_col = lerp_color(base, WHITE, 0.55 + 0.05 * gf)
    pygame.draw.polygon(surf, table_col, t)

    # ── rim: 1px hue-tinted silhouette keyline, drawn LAST before specular ──
    rim_col = lerp_color(base, WHITE, 0.4)
    pygame.draw.polygon(surf, rim_col, g, max(1, sc.m(0.6)))

    # ── lens specular: a soft off-centre highlight on the upper-left flank —
    # no centred/circular pip — held sub-white so the pip above stays the single
    # hottest point and the two read as distinct glints, not one merged blob ──
    lx, ly = cx - int(r * 0.28), cy - int(r * 0.30)
    lrx = max(1, int(r * (0.16 + 0.06 * gf)))
    lry = max(1, int(r * (0.10 + 0.04 * gf)))
    lens = pygame.Surface((lrx * 2 + 2, lry * 2 + 2), pygame.SRCALPHA)
    pygame.draw.ellipse(lens, (255, 255, 255, int(150 * gf)),
                        (1, 1, lrx * 2, lry * 2))
    surf.blit(lens, (lx - lrx - 1, ly - lry - 1), special_flags=pygame.BLEND_ADD)

    px, py = cx - int(r * 0.36), cy - int(r * 0.38)
    prx = max(1, int(r * 0.05))
    pry = max(1, int(r * 0.035))
    pip = pygame.Surface((prx * 2 + 2, pry * 2 + 2), pygame.SRCALPHA)
    pygame.draw.ellipse(pip, (255, 255, 255, 220), (1, 1, prx * 2, pry * 2))
    surf.blit(pip, (px - prx - 1, py - pry - 1), special_flags=pygame.BLEND_ADD)


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
    out_dir = "/home/user/skybit/docs/store_card_v5_gem_badge_r3/improved-octagon"
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "round_2.png")

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

    hf = hud_font(30, True)
    lf = hud_font(18)

    header = hf.render("gem badge — improved-octagon r2", True, (236, 232, 250))
    canvas.blit(header, (pad, pad // 2 + 2))

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
