"""Round-2 render sheet for the kite-cut gem badge concept.

Monkey-patches store_cards.facet_gem with an ASYMMETRIC kite stone — the belly
is lifted into the UPPER HALF (a short crown over a long lower spike), so it
reads as a top-heavy falling shard rather than the symmetric rhombus of
diamond-cut. Four kite crown facets tile the ring around a proportionally-biased
table, each carrying an explicit per-facet value bias so the four planes read as
four distinct planes; shaded off one top-left key with a hot lower-right
reflected return so even cool tiers stay amber-alive. Renders it in-context on
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
    """Kite-cut: an asymmetric kite whose wide belly is lifted into the upper
    half and whose lower point drops into a long spike. The short crown over the
    long lower sliver is the whole differentiator from diamond-cut's symmetric
    rhombus. Four kite crown facets tile the ring to a proportional table; each
    is shaded by its outer-edge normal off one top-left key AND carries an
    explicit stepped value bias (UL brightest → LR darkest) so the planes never
    collapse into one another, with a hot lower-right reflected secondary keeping
    the SE-facing facets amber-alive rather than dead purple."""
    if mystery:
        base = (244, 96, 96)          # mystery owns red so it claims NO tier
        deep = (120, 22, 26)

    gf = _tier_gf(base)

    # Value stops — hue-preserving floor so a facet never crushes to black.
    t_dk  = lerp_color(deep, base, 0.18)      # shadow floor
    t_mid = base
    t_hi  = lerp_color(base, WHITE, 0.55)
    # Hotter low-sun bounce so cool shadow facets pick up a believable amber
    # return instead of collapsing to a dead cool hue.
    warm  = lerp_color(base, (255, 200, 120), 0.55)
    t_key = lerp_color(deep, NEAR_BLACK, 0.5)

    def shade(nx, ny):
        d = nx * (-0.7071) + ny * (-0.7071)     # primary top-left light
        f = (d + 1) / 2
        if f < 0.5:
            col = lerp_color(t_dk, t_mid, f * 2)
        else:
            col = lerp_color(t_mid, t_hi, (f - 0.5) * 2)
        # reflected secondary from lower-right so the SE/S-facing shadow facets
        # glow instead of reading dead purple
        d2 = nx * 0.5 + ny * 0.5
        f2 = max(0.0, (d2 + 1) / 2)
        col = lerp_color(col, warm, 0.25 * f2 * gf)
        return col

    # ── seat: a dark well + faint tier ring so the stone reads on any ground.
    # Kept circular; the lifted belly drops a long spike that intentionally
    # protrudes past the seat well, reinforcing the top-heavy read. ──
    seat_r = r + sc.m(4)
    seat_sz = r * 2 + sc.m(10)
    seat = pygame.Surface((seat_sz, seat_sz), pygame.SRCALPHA)
    sc_off = r + sc.m(5)
    pygame.draw.circle(seat, (0, 0, 0, 175), (sc_off, sc_off), seat_r)
    pygame.draw.circle(seat, (*base, 100), (sc_off, sc_off), seat_r, max(1, sc.m(0.8)))
    surf.blit(seat, (cx - sc_off, cy - sc_off))

    # ── inner glow: a tighter tier bloom so it doesn't wash out the long spike ──
    sc.soft_glow(surf, cx, cy, int(r * 0.40), base, int(65 * gf))

    # ── girdle + table corners (asymmetric kite, belly lifted HIGH into the
    # upper half: short N→belly crown, long belly→S spike) ──
    N = (cx,                  cy - int(r * 0.90))   # top apex (shorter reach)
    E = (cx + int(r * 0.82),  cy - int(r * 0.55))   # right belly, upper half
    W = (cx - int(r * 0.82),  cy - int(r * 0.55))   # left belly, upper half
    S = (cx,                  cy + int(r * 1.10))   # long lower spike

    tN = (cx,                  cy - int(r * 0.50))
    tE = (cx + int(r * 0.24),  cy - int(r * 0.22))
    tW = (cx - int(r * 0.24),  cy - int(r * 0.22))
    tS = (cx,                  cy + int(r * 0.45))

    def unit_mid(a, b):
        mx = (a[0] + b[0]) / 2 - cx
        my = (a[1] + b[1]) / 2 - cy
        ml = math.hypot(mx, my) or 1
        return mx / ml, my / ml

    # Four kite crown facets fully tiling the crown ring. An explicit stepped
    # value bias (added AFTER the dot-product shade) forces ~25 lum between
    # neighbouring planes so the four facets never collapse into one flat mass:
    # UL brightest → UR → LL → LR darkest.
    kites = [
        ([W, N, tN, tW], unit_mid(W, N), 0.00),   # upper-left, most lit
        ([N, E, tE, tN], unit_mid(N, E), 0.12),   # upper-right
        ([S, W, tW, tS], unit_mid(S, W), 0.20),   # lower-left sliver
        ([E, S, tS, tE], unit_mid(E, S), 0.30),   # lower-right sliver, darkest
    ]
    for quad, (nx, ny), dk_bias in kites:
        col = shade(nx, ny)
        if dk_bias:
            col = lerp_color(col, t_dk, dk_bias)
        pygame.draw.polygon(surf, col, quad)

    # ── seams: outer corner -> table corner ──
    seam_w = max(1, sc.m(0.5))
    for outer, inner in ((W, tW), (N, tN), (E, tE), (S, tS)):
        pygame.draw.line(surf, (*t_key, 190), outer, inner, seam_w)

    # ── table: the flat top, lifted to be the unambiguously brightest zone so
    # the eye lands there before any crown facet ──
    table_col = lerp_color(base, WHITE, 0.62 + 0.05 * gf)
    pygame.draw.polygon(surf, table_col, [tN, tE, tS, tW])

    # ── rim: silhouette keyline so the edge stays defined ──
    rim_col = lerp_color(base, WHITE, 0.4)
    pygame.draw.polygon(surf, rim_col, [N, E, S, W], max(1, sc.m(0.6)))

    # ── split specular seated in the SHORT upper-left facet: a soft lens (wider
    # than tall) plus a distinct hot pip above it — both additive so they read as
    # glass. Re-anchored high after the belly lift so it sits inside the short UL
    # segment, keeping the asymmetry legible. ──
    lx, ly = cx - int(r * 0.24), cy - int(r * 0.55)
    lrx = max(1, int(r * (0.15 + 0.05 * gf)))
    lry = max(1, int(r * (0.09 + 0.03 * gf)))
    lens = pygame.Surface((lrx * 2 + 2, lry * 2 + 2), pygame.SRCALPHA)
    pygame.draw.ellipse(lens, (255, 255, 255, int(190 * gf)),
                        (1, 1, lrx * 2, lry * 2))
    surf.blit(lens, (lx - lrx - 1, ly - lry - 1), special_flags=pygame.BLEND_ADD)

    px, py = cx - int(r * 0.32), cy - int(r * 0.62)
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
    out_dir = "/home/user/skybit/docs/store_card_v5_gem_badge_r3/kite-cut"
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

    header = hf.render("gem badge — kite-cut r2", True, (236, 232, 250))
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
