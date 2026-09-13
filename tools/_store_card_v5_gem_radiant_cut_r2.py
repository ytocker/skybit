"""Round-2 render sheet for the radiant-cut gem badge concept.

Monkey-patches store_cards.facet_gem with a LANDSCAPE clipped-corner stone —
the only wider-than-tall gem in the set, so its orientation alone reads at
22px. Eight triangular crown facets tile the ring between an octagonal girdle
and a scaled octagonal table, value-stepped off one top-left key light with a
warm reflected pass so the shadow flank glows instead of going dead. Renders
it in-context on two full v5 cards plus an 8x zoomed 4-tier gem strip.
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
    """Radiant-cut: a landscape clipped-corner octagon — the only wider-than-
    tall stone in the set, so its format alone distinguishes it at badge size.
    Eight triangular crown facets tile the ring between an octagonal girdle and
    a 0.50-scaled table; each is shaded by its edge-midpoint normal off one
    top-left key light, with a warm reflected secondary keeping the shadow
    flank alive. A razor-thin horizontal specular streak echoes the wide form."""
    if mystery:
        base = (244, 96, 96)          # mystery owns red so it claims NO tier
        deep = (120, 22, 26)

    gf = _tier_gf(base)

    # Value stops — hue-preserving floor so a facet never crushes to black.
    # Crown ceiling stays well under the table so the flat top wins the eye.
    t_dk  = lerp_color(deep, base, 0.18)      # shadow floor
    t_mid = base
    t_hi  = lerp_color(base, WHITE, 0.45)
    t_key = lerp_color(deep, NEAR_BLACK, 0.5)
    # Warmer reflected tint: a low-sun bounce, not just a pale wash, so cool
    # shadow facets pick up a believable amber return.
    warm  = lerp_color(base, (255, 200, 120), 0.4)

    def shade(nx, ny):
        d = nx * (-0.7071) + ny * (-0.7071)     # primary top-left light
        f = (d + 1) / 2
        if f < 0.5:
            col = lerp_color(t_dk, t_mid, f * 2)
        else:
            col = lerp_color(t_mid, t_hi, (f - 0.5) * 2)
        # reflected secondary from lower-right so the SE/S-facing shadow facets
        # glow amber instead of reading dead flat purple
        d2 = nx * 0.5 + ny * 0.5
        f2 = max(0.0, (d2 + 1) / 2)
        col = lerp_color(col, warm, 0.18 * f2 * gf)
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

    # ── girdle: a landscape clipped-corner octagon (emphatically wider than
    # tall) so orientation alone separates it from the octagon stone ──
    hw = r
    hh = int(r * 0.70)
    c = int(r * 0.32)
    girdle = [
        (cx - hw + c, cy - hh),      # TL
        (cx + hw - c, cy - hh),      # TR
        (cx + hw,     cy - hh + c),  # R_top
        (cx + hw,     cy + hh - c),  # R_bot
        (cx + hw - c, cy + hh),      # BR
        (cx - hw + c, cy + hh),      # BL
        (cx - hw,     cy + hh - c),  # L_bot
        (cx - hw,     cy - hh + c),  # L_top
    ]
    # Table: same octagon scaled 0.50 about centre — the flat crown top.
    table_pts = [(cx + int((x - cx) * 0.50), cy + int((y - cy) * 0.50))
                 for x, y in girdle]

    def unit_mid(a, b):
        mx = (a[0] + b[0]) / 2 - cx
        my = (a[1] + b[1]) / 2 - cy
        ml = math.hypot(mx, my) or 1
        return mx / ml, my / ml

    # ── eight triangular crown facets fully tiling the crown ring: one per
    # outer edge, each a quad from the outer edge to the matching table edge ──
    n = len(girdle)
    for i in range(n):
        a = girdle[i]
        b = girdle[(i + 1) % n]
        ta = table_pts[i]
        tb = table_pts[(i + 1) % n]
        nx, ny = unit_mid(a, b)
        pygame.draw.polygon(surf, shade(nx, ny), [a, b, tb, ta])

    # ── seams: outer vertex -> table vertex radials ──
    seam_w = max(1, sc.m(0.5))
    for i in range(n):
        pygame.draw.line(surf, (*t_key, 190), girdle[i], table_pts[i], seam_w)

    # ── table: the flat top, lifted well clear of the crown ceiling so the eye
    # lands there first (≥25 lum over the brightest crown facet at all tiers) ──
    table_col = lerp_color(base, WHITE, 0.62 + 0.05 * gf)
    pygame.draw.polygon(surf, table_col, table_pts)

    # ── rim: hue-tinted silhouette keyline so the edge stays defined ──
    rim_col = lerp_color(base, WHITE, 0.40)
    pygame.draw.polygon(surf, rim_col, girdle, max(1, sc.m(0.6)))

    # ── specular: a razor-thin horizontal streak (rx >> ry) so it reads as a
    # single elongated flash echoing the landscape form, plus an inline hot pip
    # on the same axis — both additive so together they read as glass ──
    lx, ly = cx - int(r * 0.30), cy - int(r * 0.24)
    lrx = max(2, int(r * (0.18 + 0.04 * gf)))
    lrx = min(lrx, int(r * 0.18) + 1)
    lry = 1
    lens = pygame.Surface((lrx * 2 + 2, lry * 2 + 2), pygame.SRCALPHA)
    pygame.draw.ellipse(lens, (255, 255, 255, int(190 * gf)),
                        (1, 1, lrx * 2, lry * 2))
    surf.blit(lens, (lx - lrx - 1, ly - lry - 1), special_flags=pygame.BLEND_ADD)

    px, py = cx - int(r * 0.40), cy - int(r * 0.24)
    prx = max(1, int(r * 0.06))
    pry = 1
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
    out_dir = "/home/user/skybit/docs/store_card_v5_gem_badge_r3/radiant-cut"
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

    header = hf.render("gem badge — radiant-cut r2", True, (236, 232, 250))
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
