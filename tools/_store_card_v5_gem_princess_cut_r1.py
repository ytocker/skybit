"""Round-1 render sheet for the princess-cut gem badge concept.

Monkey-patches store_cards.facet_gem with a square brilliant — an
axis-aligned square standing on its edges, cut into four cardinal
trapezoid facets plus four corner triangles that radiate a princess "X"
out of a square table. Value-stepped off one top-left light with a warm
lower-right bounce so the shadow facets glow rather than going dead.
Clean right-angle engineering aesthetic. Renders it in-context on two
full v5 cards plus an 8x zoomed 4-tier gem strip. Review-only tooling —
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
    # Brighter tiers earn a hotter reflected-fill + specular so legendary reads
    # as the richest stone; muted low tiers stay restrained.
    if base == (214, 206, 230): return 0.55
    if base == (108, 188, 252): return 0.70
    if base == (194, 122, 248): return 0.85
    if base == (255, 202, 104): return 1.00
    return 0.85


def my_facet_gem(surf, cx, cy, r, base, deep, mystery=False):
    """Princess-cut: an axis-aligned square standing on its edges, cut into
    four cardinal trapezoid facets tiling the ring between the outer square
    and a square table, plus four corner triangles that radiate the princess
    "X" out of the table corners. Each facet is shaded by its face normal off
    one top-left key light, with a warmer lower-right bounce keeping the
    shadow facets alive rather than dead purple."""
    if mystery:
        base = (244, 96, 96)          # mystery owns red so it claims NO tier
        deep = (120, 22, 26)

    gf = _tier_gf(base)

    # Value stops — hue-preserving floor so a facet never crushes to black.
    t_dk  = lerp_color(deep, base, 0.18)      # shadow floor
    t_mid = base
    t_hi  = lerp_color(base, WHITE, 0.55)
    # Warmer reflected tint: a low-sun bounce, not just a pale wash, so cool
    # shadow facets pick up a believable amber return.
    warm  = lerp_color(base, (255, 200, 120), 0.4)
    t_key = lerp_color(deep, NEAR_BLACK, 0.5)

    def shade(nx, ny):
        d = nx * (-0.7071) + ny * (-0.7071)     # primary top-left light
        f = (d + 1) / 2
        if f < 0.5:
            col = lerp_color(t_dk, t_mid, f * 2)
        else:
            col = lerp_color(t_mid, t_hi, (f - 0.5) * 2)
        # reflected secondary from lower-right, warmer so the SE/S-facing
        # shadow facets glow instead of reading dead purple
        d2 = nx * 0.5 + ny * 0.5
        f2 = max(0.0, (d2 + 1) / 2)
        col = lerp_color(col, warm, 0.15 * f2 * gf)
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

    # ── square silhouette (axis-aligned, standing on its edges) ──
    s = r * 0.72
    TL = (cx - s, cy - s)
    TR = (cx + s, cy - s)
    BR = (cx + s, cy + s)
    BL = (cx - s, cy + s)

    # ── square table (inner square) ──
    st = r * 0.34
    tTL = (cx - st, cy - st)
    tTR = (cx + st, cy - st)
    tBR = (cx + st, cy + st)
    tBL = (cx - st, cy + st)

    # ── four cardinal trapezoid facets tiling the crown ring ──
    traps = [
        ([TL, TR, tTR, tTL], (0.0, -1.0)),   # top, most lit
        ([TR, BR, tBR, tTR], (1.0,  0.0)),   # right
        ([BR, BL, tBL, tBR], (0.0,  1.0)),   # bottom, darkest
        ([BL, TL, tTL, tBL], (-1.0, 0.0)),   # left, mid-lit
    ]
    for quad, (nx, ny) in traps:
        pygame.draw.polygon(surf, shade(nx, ny), quad)

    # ── corner triangles: shaded darker than the adjacent traps so the
    # princess "X" radiates from the table corners out to the square corners ──
    corners = [
        ([TL, tTL, tTR], (-0.7071, -0.7071), TL, tTL),   # UL corner region
        ([TR, tTR, tBR], (0.7071, -0.7071), TR, tTR),    # UR
        ([BR, tBR, tBL], (0.7071, 0.7071), BR, tBR),     # LR
        ([BL, tBL, tTL], (-0.7071, 0.7071), BL, tBL),    # LL
    ]
    for tri, (nx, ny), outer, inner in corners:
        col = shade(nx, ny)
        col = lerp_color(col, t_key, 0.28)   # darker than neighbouring traps
        pygame.draw.polygon(surf, col, tri)

    # ── seams: hard corner diagonals (the princess "X") ──
    seam_w = max(1, sc.m(0.5))
    for outer, inner in ((TL, tTL), (TR, tTR), (BR, tBR), (BL, tBL)):
        pygame.draw.line(surf, (*t_key, 210), outer, inner, seam_w)

    # ── lighter chevron seams: outer edge midpoint -> table edge midpoint so
    # each cardinal trapezoid reads as an arrow facet ──
    chev_w = max(1, sc.m(0.4))
    chev_col = lerp_color(t_key, base, 0.35)
    edges = [
        (((TL[0] + TR[0]) / 2, (TL[1] + TR[1]) / 2), ((tTL[0] + tTR[0]) / 2, (tTL[1] + tTR[1]) / 2)),  # top
        (((TR[0] + BR[0]) / 2, (TR[1] + BR[1]) / 2), ((tTR[0] + tBR[0]) / 2, (tTR[1] + tBR[1]) / 2)),  # right
        (((BR[0] + BL[0]) / 2, (BR[1] + BL[1]) / 2), ((tBR[0] + tBL[0]) / 2, (tBR[1] + tBL[1]) / 2)),  # bottom
        (((BL[0] + TL[0]) / 2, (BL[1] + TL[1]) / 2), ((tBL[0] + tTL[0]) / 2, (tBL[1] + tTL[1]) / 2)),  # left
    ]
    for outer_mid, inner_mid in edges:
        pygame.draw.line(surf, (*chev_col, 150), outer_mid, inner_mid, chev_w)

    # ── table: the flat top, lifted to be the single brightest zone so the eye
    # lands there before any crown facet ──
    table_col = lerp_color(base, WHITE, 0.55 + 0.05 * gf)
    pygame.draw.polygon(surf, table_col, [tTL, tTR, tBR, tBL])

    # ── rim: silhouette keyline so the square edge stays defined ──
    rim_col = lerp_color(base, WHITE, 0.40)
    pygame.draw.polygon(surf, rim_col, [TL, TR, BR, BL], max(1, sc.m(0.6)))

    # ── split specular: a soft lens seated on the table's upper flank, plus a
    # distinct hot pip just above it — both additive so they read as glass.
    # NO centred/circular specular. ──
    lx, ly = cx - int(r * 0.26), cy - int(r * 0.26)
    lrx = max(1, int(r * (0.15 + 0.05 * gf)))
    lry = max(1, int(r * (0.09 + 0.03 * gf)))
    lens = pygame.Surface((lrx * 2 + 2, lry * 2 + 2), pygame.SRCALPHA)
    pygame.draw.ellipse(lens, (255, 255, 255, int(190 * gf)),
                        (1, 1, lrx * 2, lry * 2))
    surf.blit(lens, (lx - lrx - 1, ly - lry - 1), special_flags=pygame.BLEND_ADD)

    px, py = cx - int(r * 0.34), cy - int(r * 0.34)
    prx = max(1, int(r * 0.05))
    pry = max(1, int(r * 0.04))
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
    out_dir = "/home/user/skybit/docs/store_card_v5_gem_badge_r3/princess-cut"
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

    hf = hud_font(30, True)
    lf = hud_font(18)

    header = hf.render("gem badge — princess-cut r1", True, (236, 232, 250))
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
