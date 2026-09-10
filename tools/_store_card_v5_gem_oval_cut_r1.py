"""Round-1 render sheet for the oval-cut gem badge concept.

Monkey-patches store_cards.facet_gem with a vertical navette (pointed-ellipse /
marquise) stone: two opposing apexes with chevron French-tip caps, an oval
belly (no sharp corners) that is narrower than the diamond-cut rhombus, and a
diamond table lens. Value-stepped off one top-left light with a warm reflected
bounce so the shade facets glow rather than go dead. Renders it in-context on
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
    # Brighter tiers earn a hotter reflected-fill + specular so legendary reads
    # as the richest stone; muted low tiers stay restrained.
    if base == (214, 206, 230): return 0.55
    if base == (108, 188, 252): return 0.70
    if base == (194, 122, 248): return 0.85
    if base == (255, 202, 104): return 1.00
    return 0.85


def my_facet_gem(surf, cx, cy, r, base, deep, mystery=False):
    """Oval-cut: a vertical navette (marquise) — an oval belly rising to two
    opposing pointed apexes with chevron French-tip caps. Narrower than the
    diamond rhombus (belly at r*0.50) so the tall stone reads as its own cut.
    Six facets (four belly quads + two chevron apex triangles) tile around a
    diamond table, each shaded by its quadrant normal off one top-left key
    light, with a warmer lower-right reflected bounce keeping shade facets
    alive."""
    if mystery:
        base = (244, 96, 96)          # mystery owns red so it claims NO tier
        deep = (120, 22, 26)

    gf = _tier_gf(base)

    # Value stops — hue-preserving floor so a facet never crushes to black.
    t_dk  = lerp_color(deep, base, 0.18)      # shadow floor
    t_mid = base
    t_hi  = lerp_color(base, WHITE, 0.55)
    warm  = lerp_color(base, (255, 200, 120), 0.4)
    t_key = lerp_color(deep, NEAR_BLACK, 0.5)

    def shade(nx, ny):
        d = nx * (-0.7071) + ny * (-0.7071)     # primary top-left light
        f = (d + 1) / 2
        if f < 0.5:
            col = lerp_color(t_dk, t_mid, f * 2)
        else:
            col = lerp_color(t_mid, t_hi, (f - 0.5) * 2)
        # reflected secondary from lower-right — warm low-sun bounce so the
        # SE/S-facing shade facets glow instead of reading dead purple
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

    # ── navette silhouette: blunted apexes (2px flats) so the tips don't
    # alias to a jagged pixel at 22px, oval belly at r*0.50 ──
    TOP_L = (cx - 2, cy - r + 1)
    TOP_R = (cx + 2, cy - r + 1)
    BOT_L = (cx - 2, cy + r - 1)
    BOT_R = (cx + 2, cy + r - 1)
    L = (cx - int(r * 0.50), cy)
    R = (cx + int(r * 0.50), cy)

    # ── table: a diamond lens, taller than wide to echo the navette ──
    tT = (cx,                  cy - int(r * 0.42))
    tR = (cx + int(r * 0.22),  cy)
    tB = (cx,                  cy + int(r * 0.42))
    tL = (cx - int(r * 0.22),  cy)

    inv = 1.0 / math.sqrt(2)
    # Six facets: four belly quads keyed to their quadrant diagonal, plus two
    # chevron apex triangles capping the points.
    facets = [
        ([TOP_L, tT, tL, L], (-inv, -inv), False),   # UL — most lit
        ([TOP_R, R, tR, tT], ( inv, -inv), False),   # UR
        ([BOT_R, tB, tR, R], ( inv,  inv), False),   # LR
        ([BOT_L, L, tL, tB], (-inv,  inv), True),    # LL — darkest
        ([TOP_L, TOP_R, tT], (0.0, -1.0), False),    # top chevron cap (UL-lit)
        ([BOT_L, tB, BOT_R], (0.0,  1.0), True),     # bottom chevron (dark base)
    ]
    for poly, (nx, ny), extra_dark in facets:
        col = shade(nx, ny)
        if extra_dark:
            # Pull LL + base an extra step toward the key so the value ramp
            # reads UL > UR > LR > LL/BOT as distinct stops.
            col = lerp_color(col, t_dk, 0.15)
        pygame.draw.polygon(surf, col, poly)

    # ── chevron seams: nested French-tip lines from each apex into the table ──
    seam_w = max(1, sc.m(0.4))
    for a, b in ((TOP_L, tT), (TOP_R, tT), (BOT_L, tB), (BOT_R, tB)):
        pygame.draw.line(surf, (*t_key, 190), a, b, seam_w)

    # ── table: the flat top, lifted to be the single brightest zone so the eye
    # lands there before any belly facet ──
    table_col = lerp_color(base, WHITE, 0.55 + 0.05 * gf)
    pygame.draw.polygon(surf, table_col, [tT, tR, tB, tL])

    # ── rim: hue-tinted silhouette keyline so the navette edge stays defined ──
    rim_col = lerp_color(base, WHITE, 0.40)
    pygame.draw.polygon(surf, rim_col, [TOP_L, TOP_R, R, BOT_R, BOT_L, L],
                        max(1, sc.m(0.6)))

    # ── lens specular: a horizontal catch-light (rx > ry) across the tall
    # stone, plus a distinct hot pip above it — both additive so they read as
    # glass. No centred/circular highlight. ──
    lx, ly = cx - int(r * 0.16), cy - int(r * 0.24)
    lrx = max(1, int(r * (0.14 + 0.06 * gf)))
    lry = max(1, int(r * (0.09 + 0.03 * gf)))
    lens = pygame.Surface((lrx * 2 + 2, lry * 2 + 2), pygame.SRCALPHA)
    pygame.draw.ellipse(lens, (255, 255, 255, int(185 * gf)),
                        (1, 1, lrx * 2, lry * 2))
    surf.blit(lens, (lx - lrx - 1, ly - lry - 1), special_flags=pygame.BLEND_ADD)

    px, py = cx - int(r * 0.22), cy - int(r * 0.30)
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
    out_dir = "/home/user/skybit/docs/store_card_v5_gem_badge_r3/oval-cut"
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

    header = hf.render("gem badge — oval-cut r1", True, (236, 232, 250))
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
