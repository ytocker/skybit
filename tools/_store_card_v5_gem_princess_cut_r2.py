"""Round-2 render sheet for the princess-cut gem badge concept.

Monkey-patches store_cards.facet_gem with a square brilliant — an
axis-aligned square standing on its edges, cut over a diamond table into
four cardinal triangle facets on an explicit 4-step value ladder plus four
corner triangles that radiate a mirror-symmetric princess "X" out to the
stone corners. Value-stepped off one top-left light with a warm lower-right
bounce so the shadow facets glow rather than going dead. Clean right-angle
engineering aesthetic. Renders it in-context on two full v5 cards plus an
8x zoomed 4-tier gem strip. Review-only tooling — never imported by game.
"""
import os
import sys

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
    """Princess-cut: an axis-aligned square standing on its edges, cut over a
    diamond table into four cardinal triangle facets driven by an explicit
    4-step luminance ladder (top brightest -> bottom darkest, left brighter
    than right), plus four corner triangle facets that fill toward the stone
    corners on a mirror-symmetric value scheme (left == right at each height,
    only top vs bottom differ) so the princess "X" reads as a clean cross, not
    a pinwheel. A warm lower-right bounce keeps the shadow facets alive."""
    if mystery:
        base = (244, 96, 96)          # mystery owns red so it claims NO tier
        deep = (120, 22, 26)

    gf = _tier_gf(base)

    # Value stops — hue-preserving floor so a facet never crushes to black.
    t_dk  = lerp_color(deep, base, 0.18)      # shadow floor
    t_mid = base
    # Crown highlight sits deliberately BELOW the table so the flat top stays
    # the single unambiguously brightest zone at every tier (see table below).
    t_hi  = lerp_color(base, WHITE, 0.35)
    # Warmer reflected tint: a low-sun bounce, not just a pale wash, so cool
    # shadow facets pick up a believable amber return instead of dead purple.
    warm  = lerp_color(base, (255, 200, 120), 0.45)
    t_key = lerp_color(deep, NEAR_BLACK, 0.5)

    def apply_warm(col, f2):
        # Lower-right-facing facets pick up the amber bounce; strength scales
        # with tier so richer stones glow warmer in shadow.
        return lerp_color(col, warm, 0.22 * f2 * gf)

    # ── explicit 4-step cardinal ladder (no shared dot-product collisions) ──
    top_col   = t_hi                                  # brightest crown
    left_col  = lerp_color(t_mid, t_hi, 0.45)         # mid-bright
    right_col = lerp_color(t_dk, t_mid, 0.75)         # mid-dark
    bot_col   = t_dk                                  # darkest
    # warm bounce weighted by each facet's outward normal (top/left cool,
    # right/bottom warm) — cardinals may differ left/right by design.
    top_col   = apply_warm(top_col,   0.25)
    left_col  = apply_warm(left_col,  0.25)
    right_col = apply_warm(right_col, 0.75)
    bot_col   = apply_warm(bot_col,   0.75)

    # Corner triangles: slightly darker than the adjacent cardinal, and mirror
    # symmetric across the vertical axis so the X never skews to a pinwheel.
    # Warm bounce is keyed to vertical position ONLY (upper vs lower) so the
    # left and right corner at a given height stay identical.
    up_corner_col = apply_warm(lerp_color(top_col, t_dk, 0.30), 0.25)
    lo_corner_col = apply_warm(lerp_color(bot_col, t_dk, 0.30), 0.75)

    # ── seat: a dark well + faint tier ring so the stone reads on any ground ──
    seat_r = r + sc.m(4)
    seat_sz = r * 2 + sc.m(10)
    seat = pygame.Surface((seat_sz, seat_sz), pygame.SRCALPHA)
    sc_off = r + sc.m(5)
    pygame.draw.circle(seat, (0, 0, 0, 175), (sc_off, sc_off), seat_r)
    pygame.draw.circle(seat, (*base, 100), (sc_off, sc_off), seat_r, max(1, sc.m(0.8)))
    surf.blit(seat, (cx - sc_off, cy - sc_off))

    # ── inner glow: a tighter, dimmer tier bloom so the square corners stay
    # crisp — the right-angle silhouette is the whole identity. ──
    sc.soft_glow(surf, cx, cy, int(r * 0.42), base, int(60 * gf))

    # ── square silhouette (axis-aligned, standing on its edges) ──
    s = r * 0.72
    TL = (cx - s, cy - s)
    TR = (cx + s, cy - s)
    BR = (cx + s, cy + s)
    BL = (cx - s, cy + s)

    # ── diamond table (45°-rotated inner square): its corners face the
    # cardinals; the X radiates from its edge midpoints to the stone corners. ──
    st = r * 0.40
    tN = (cx, cy - st)
    tE = (cx + st, cy)
    tS = (cx, cy + st)
    tW = (cx - st, cy)
    # diamond edge midpoints — the inner anchor of each corner X seam.
    tTL = ((tW[0] + tN[0]) / 2, (tW[1] + tN[1]) / 2)
    tTR = ((tN[0] + tE[0]) / 2, (tN[1] + tE[1]) / 2)
    tBR = ((tE[0] + tS[0]) / 2, (tE[1] + tS[1]) / 2)
    tBL = ((tS[0] + tW[0]) / 2, (tS[1] + tW[1]) / 2)

    # ── four cardinal triangle facets (explicit ladder) ──
    pygame.draw.polygon(surf, top_col,   [TL, TR, tN])   # top, brightest
    pygame.draw.polygon(surf, right_col, [TR, BR, tE])   # right, mid-dark
    pygame.draw.polygon(surf, bot_col,   [BR, BL, tS])   # bottom, darkest
    pygame.draw.polygon(surf, left_col,  [BL, TL, tW])   # left, mid-bright

    # ── four corner triangle facets — the mirror-symmetric princess "X" ──
    pygame.draw.polygon(surf, up_corner_col, [TL, tW, tN])   # UL
    pygame.draw.polygon(surf, up_corner_col, [TR, tN, tE])   # UR
    pygame.draw.polygon(surf, lo_corner_col, [BR, tE, tS])   # LR
    pygame.draw.polygon(surf, lo_corner_col, [BL, tS, tW])   # LL

    # ── table: the flat top, lifted to be the single brightest zone so the eye
    # lands there before any crown facet (kept > every cardinal at all tiers) ──
    table_col = lerp_color(base, WHITE, 0.60 + 0.05 * gf)
    pygame.draw.polygon(surf, table_col, [tN, tE, tS, tW])

    # ── seams: only the four corner diagonals (the princess "X"). No cardinal
    # chevrons — they turned to noise at badge scale. ──
    seam_w = max(1, sc.m(0.5))
    for outer, inner in ((TL, tTL), (TR, tTR), (BR, tBR), (BL, tBL)):
        pygame.draw.line(surf, (*t_key, 230), outer, inner, seam_w)

    # ── rim: silhouette keyline at full width so the square edge survives at
    # 22px (a thinner stroke vanishes on the web downscale). ──
    rim_col = lerp_color(base, WHITE, 0.45)
    pygame.draw.polygon(surf, rim_col, [TL, TR, BR, BL], max(1, sc.m(1.0)))

    # ── split specular: a small soft lens seated on the table's upper-left,
    # plus a distinct hot pip just above it — both additive so they read as
    # glass. Sub-white lens so the pip stays the hottest point. ──
    lx, ly = cx - int(r * 0.12), cy - int(r * 0.16)
    lrx = max(1, int(r * (0.11 + 0.04 * gf)))
    lry = max(1, int(r * (0.055 + 0.02 * gf)))
    lens = pygame.Surface((lrx * 2 + 2, lry * 2 + 2), pygame.SRCALPHA)
    pygame.draw.ellipse(lens, (255, 255, 255, int(150 * gf)),
                        (1, 1, lrx * 2, lry * 2))
    surf.blit(lens, (lx - lrx - 1, ly - lry - 1), special_flags=pygame.BLEND_ADD)

    px, py = cx - int(r * 0.20), cy - int(r * 0.24)
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


def _lum(px):
    return 0.299 * px[0] + 0.587 * px[1] + 0.114 * px[2]


def main():
    out_dir = "/home/user/skybit/docs/store_card_v5_gem_badge_r3/princess-cut"
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

    header = hf.render("gem badge — princess-cut r2", True, (236, 232, 250))
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

    # ── sanity: the table must be the brightest zone at every tier (note 4) ──
    for name, base, deep in RARITY_TIERS:
        g = render_gem(base, deep)
        c = g.get_width() // 2
        table_lum = _lum(g.get_at((c, c)))          # dead centre = table
        # top cardinal sits just below the table apex, above the diamond top.
        top_lum = _lum(g.get_at((c, int(c - GEM_R * 0.62))))
        print(f"  {name:>9}: table_lum={table_lum:.0f} top_cardinal_lum={top_lum:.0f}")
        assert table_lum > top_lum, f"{name}: table not brightest"
    print("sanity OK — reflected floor holds; table dominates every tier")


if __name__ == "__main__":
    main()
