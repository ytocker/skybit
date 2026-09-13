"""Review render: trillion-cut gem badge (iteration 2) for the v5 store card.

A point-up brilliant trillion cut for the tier gem badge in place of the locked
8-facet octagon. The triangular crown reads as a distinct silhouette at badge
scale. r2 moves the specular onto the LEFT crown facet (where the top-left key
light actually lands), caps the table so it stays a hue-tinted focal bright
instead of a white flash, and gives each crown facet ONE flat value off a clean
3-stop ramp so the cut reads as three planes, not a gradient smear. The
apex-glow clamp still nudges the bloom below centre so the sharp top point wins.
"""
import os, sys, math

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, "/home/user/skybit")

import pygame
pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

import game.store_cards as sc
from game.draw import lerp_color, NEAR_BLACK, WHITE
from game.hud import _font as hud_font


def _tier_gf(base):
    if base == (214, 206, 230): return 0.55
    if base == (108, 188, 252): return 0.70
    if base == (194, 122, 248): return 0.85
    if base == (255, 202, 104): return 1.00
    return 0.85


def my_facet_gem(surf, cx, cy, r, base, deep, mystery=False):
    """Point-up trillion cut: an equilateral triangle girdle with three crown
    trapezoids tiling to a small central table triangle. Each facet is a single
    flat value taken off a 3-stop ramp keyed to its outward normal vs ONE
    top-left light, so the crown reads as three clean planes. The seat + inner
    bloom sit BELOW centre so nothing softens the sharp apex T, which is held by
    a bright rim trace drawn last."""
    gf = _tier_gf(base)

    # 3-stop crown ramp; gf scales the hot endpoint so legendary out-glitters
    # common instead of every tier topping out at the same brightness.
    t_dk  = lerp_color(deep, base, 0.18)
    t_mid = base
    t_hi  = lerp_color(base, WHITE, 0.40 + 0.30 * gf)
    # table is the focal bright but capped — hue-tinted, never a white flash.
    table_col = lerp_color(base, WHITE, 0.45 + 0.10 * gf)
    t_key = lerp_color(deep, NEAR_BLACK, 0.5)

    def facet_col(nx, ny):
        d = nx * (-0.7071) + ny * (-0.7071)
        f = (d + 1) / 2
        if f < 0.5:
            return lerp_color(t_dk, t_mid, f * 2)
        return lerp_color(t_mid, t_hi, (f - 0.5) * 2)

    # apex clamp: seat + inner bloom sit below centre so nothing softens apex T
    gcy = cy + int(r * 0.08)

    # dark seat well so the gem reads on any ground
    seat_sz = r * 2 + sc.m(10)
    seat = pygame.Surface((seat_sz, seat_sz), pygame.SRCALPHA)
    sc_off = r + sc.m(5)
    pygame.draw.circle(seat, (0, 0, 0, 175), (sc_off, sc_off), r + sc.m(4))
    pygame.draw.circle(seat, (*base, 100), (sc_off, sc_off), r + sc.m(4),
                       max(1, sc.m(0.8)))
    surf.blit(seat, (cx - sc_off, gcy - sc_off))

    sc.soft_glow(surf, cx, gcy, int(r * 0.5), base, int(80 * gf))

    # outer girdle — point-up equilateral triangle (apex at TOP)
    T  = (cx,                  cy - r)
    BR = (cx + int(r * 0.92),  cy + int(r * 0.62))
    BL = (cx - int(r * 0.92),  cy + int(r * 0.62))
    # inner table triangle, same orientation, scale 0.40
    tr = 0.40
    tT  = (cx,                        cy - int(r * tr))
    tBR = (cx + int(r * 0.92 * tr),   cy + int(r * 0.62 * tr))
    tBL = (cx - int(r * 0.92 * tr),   cy + int(r * 0.62 * tr))

    def edge_normal(p, q):
        mx = (p[0] + q[0]) / 2 - cx
        my = (p[1] + q[1]) / 2 - cy
        ml = math.hypot(mx, my) or 1
        return mx / ml, my / ml

    # three crown trapezoids fully tiling the crown ring — one flat value each:
    #   left  (BL→T, faces UL light) brightest
    #   right (T→BR, faces part-right) mid
    #   bottom(BR→BL, faces down-away) darkest
    for edge, tri in ((((T, BR), (tBR, tT))),   # right edge
                      (((BR, BL), (tBL, tBR))),  # bottom edge (darkest)
                      (((BL, T), (tT, tBL)))):   # left edge (most lit)
        (a, b), (ib, ia) = edge, tri
        nx, ny = edge_normal(a, b)
        pygame.draw.polygon(surf, facet_col(nx, ny), [a, b, ib, ia])

    # flat table on top — capped focal bright
    pygame.draw.polygon(surf, table_col, [tT, tBR, tBL])

    # seams from each girdle corner to its table corner
    for a, ta in ((T, tT), (BR, tBR), (BL, tBL)):
        pygame.draw.line(surf, (*t_key, 190), a, ta, max(1, sc.m(0.4)))

    # rim trace LAST at the top layer so the sharp apex wins over the bloom
    pygame.draw.polygon(surf, lerp_color(base, WHITE, 0.4), [T, BR, BL],
                        width=max(1, sc.m(0.5)))

    # dual specular on the LEFT crown facet — the plane the UL key light hits.
    # Deliberately offset well left of the apex so T is NOT the hottest point.
    lrx = int(r * (0.10 + 0.07 * gf))
    lry = int(r * (0.07 + 0.05 * gf))
    lens = pygame.Surface((lrx * 2 + 2, lry * 2 + 2), pygame.SRCALPHA)
    pygame.draw.ellipse(lens, (255, 255, 255, int(190 * gf)),
                        (1, 1, lrx * 2, lry * 2))
    lcx, lcy = cx - int(r * 0.22), cy - int(r * 0.14)
    surf.blit(lens, (lcx - lrx - 1, lcy - lry - 1), special_flags=pygame.BLEND_ADD)

    prx, pry = int(r * 0.05), int(r * 0.04)
    pip = pygame.Surface((prx * 2 + 2, pry * 2 + 2), pygame.SRCALPHA)
    pygame.draw.ellipse(pip, (255, 255, 255, 220), (1, 1, prx * 2, pry * 2))
    pcx, pcy = cx - int(r * 0.28), cy - int(r * 0.18)
    surf.blit(pip, (pcx - prx - 1, pcy - pry - 1), special_flags=pygame.BLEND_ADD)


# ── render sheet ──────────────────────────────────────────────────────────────
RARITY_TIERS = [
    ("common",    (214, 206, 230), (78,  74, 112)),
    ("rare",      (108, 188, 252), (24,  78, 142)),
    ("epic",      (194, 122, 248), (80,  34, 126)),
    ("legendary", (255, 202, 104), (150, 92,  22)),
]
SID_PRIMARY   = "skin_mummy"
SID_SECONDARY = "skin_kitsune"
CARD_W = sc.CARD_W * sc.SS
GEM_R  = sc.m(sc.GEM_R + 3)

sc.facet_gem = my_facet_gem   # rebind BEFORE draw_card so cards use the new cut


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
    BG = (8, 8, 20)
    PAD, GAP = 28, 24

    cards = [render_card(SID_PRIMARY), render_card(SID_SECONDARY)]
    ZOOM = 8
    gems = []
    for name, base, deep in RARITY_TIERS:
        g = render_gem(base, deep)
        gz = pygame.transform.smoothscale(
            g, (g.get_width() * ZOOM // 2, g.get_height() * ZOOM // 2))
        gems.append((name, gz))

    hf = hud_font(30, True)
    lf = hud_font(16, True)

    card_row_w = len(cards) * cards[0].get_width() + (len(cards) - 1) * GAP
    gem_w = gems[0][1].get_width()
    strip_w = len(gems) * gem_w + (len(gems) - 1) * GAP
    content_w = max(card_row_w, strip_w)
    W = content_w + 2 * PAD

    header = hf.render("gem badge — trillion-cut r2", True, (238, 236, 250))
    card_h = cards[0].get_height()
    gem_h = gems[0][1].get_height()
    label_h = lf.get_height() + 8

    y = PAD
    header_h = header.get_height()
    cards_y = y + header_h + GAP
    strip_y = cards_y + card_h + GAP + 30
    H = strip_y + gem_h + label_h + PAD

    canvas = pygame.Surface((W, H))
    canvas.fill(BG)

    canvas.blit(header, (PAD, y))

    # row 1 — two full cards, centred
    x = (W - card_row_w) // 2
    for c in cards:
        canvas.blit(c, (x, cards_y))
        x += c.get_width() + GAP

    # row 2 — zoomed gem strip, one per tier, labelled below
    sub = lf.render("zoomed gem badge — all four tiers", True, (170, 170, 200))
    canvas.blit(sub, (PAD, strip_y - 26))
    x = (W - strip_w) // 2
    for name, gz in gems:
        canvas.blit(gz, (x, strip_y))
        lbl = lf.render(name, True, (222, 220, 238))
        canvas.blit(lbl, (x + (gem_w - lbl.get_width()) // 2,
                          strip_y + gem_h + 4))
        x += gem_w + GAP

    out = "/home/user/skybit/docs/store_card_v5_gem_badge_r2/trillion-cut/round_2.png"
    os.makedirs(os.path.dirname(out), exist_ok=True)
    pygame.image.save(canvas, out)
    print("saved", out, canvas.get_size())


if __name__ == "__main__":
    main()
