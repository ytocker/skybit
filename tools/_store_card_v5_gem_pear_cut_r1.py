"""Round-1 (iteration 2) render sheet for the pear-cut gem badge concept.

Monkey-patches store_cards.facet_gem with a teardrop "pear-cut" stone — a
round head at top blending into a blunt-flat point at the bottom — cut into
six crown facets around a small pear-shaped table. All facet geometry, the
seat well, the inner glow and the twin speculars are computed around a
LIFTED centre (cg) so the round head gets breathing room inside the card
corner and the blunt bottom flat avoids a fragile 1-px apex. Renders the
stone both in-context on two full v5 cards and as an 8x zoomed 4-tier gem
strip. Review-only tooling — never imported by the game.
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
CARD_W = sc.CARD_W * sc.SS   # 324
GEM_R  = sc.m(sc.GEM_R + 3)  # 22 device px


def _tier_gf(base):
    # Brighter tiers carry a hotter aura/specular than muddy low tiers; keyed
    # off the tier's own hue so the four badges feel like one graded family.
    if base == (214, 206, 230):
        return 0.55
    if base == (108, 188, 252):
        return 0.70
    if base == (194, 122, 248):
        return 0.85
    if base == (255, 202, 104):
        return 1.00
    return 0.85


def my_facet_gem(surf, cx, cy, r, base, deep, mystery=False):
    """Pear-cut: a teardrop stone with a round head up top narrowing to a
    blunt-flat point below, cut into six crown facets around a small
    pear-shaped table. Value-stepped off ONE top-left light via edge-midpoint
    normals; the head reads brightest, the down-facing tip darkest."""
    if mystery:
        base = (206, 60, 60)          # mystery owns red so it claims NO tier
        deep = (96, 18, 24)

    gf = _tier_gf(base)
    t_dk    = lerp_color(deep, base, 0.18)
    t_mid   = base
    t_hi    = lerp_color(base, WHITE, 0.55)
    t_table = lerp_color(base, WHITE, 0.50)
    warm    = lerp_color(base, (255, 238, 206), 0.5)
    t_key   = lerp_color(deep, NEAR_BLACK, 0.5)

    def shade(nx, ny):
        d = nx * (-0.7071) + ny * (-0.7071)
        f = (d + 1) / 2
        col = (lerp_color(t_dk, t_mid, f * 2) if f < 0.5
               else lerp_color(t_mid, t_hi, (f - 0.5) * 2))
        d2 = nx * 0.5 + ny * 0.5
        col = lerp_color(col, warm, 0.12 * max(0.0, (d2 + 1) / 2) * gf)
        return col

    # LIFTED CENTRE — all geometry hangs off cg so the round head has room to
    # breathe above the blunt bottom point.
    cg = (cx, cy - int(r * 0.10))

    # dark seat well so the stone reads on any ground (centred on cg)
    seat_sz = r * 2 + sc.m(10)
    seat = pygame.Surface((seat_sz, seat_sz), pygame.SRCALPHA)
    off = r + sc.m(5)
    pygame.draw.circle(seat, (0, 0, 0, 175), (off, off), r + sc.m(4))
    pygame.draw.circle(seat, (*base, 100), (off, off), r + sc.m(4),
                       max(1, sc.m(0.8)))
    surf.blit(seat, (cx - off, cg[1] - off))

    # inner tier glow settling the stone into the seat
    sc.soft_glow(surf, cx, cg[1], int(r * 0.5), base, int(80 * gf))

    # teardrop outline anchors
    A = (cx, cg[1] - r)                                   # round head apex
    Lshoulder = (cx - int(r * 0.80), cg[1] - int(r * 0.15))
    Rshoulder = (cx + int(r * 0.80), cg[1] - int(r * 0.15))
    BL = (cx - 2, cg[1] + r - 1)                          # blunt bottom flat L
    BR = (cx + 2, cg[1] + r - 1)                          # blunt bottom flat R

    # small pear-shaped table
    pT = (cx, cg[1] - int(r * 0.42))
    pL = (cx - int(r * 0.30), cg[1] - int(r * 0.05))
    pR = (cx + int(r * 0.30), cg[1] - int(r * 0.05))
    pB = (cx, cg[1] + int(r * 0.45))

    def norm(mid):
        vx, vy = mid[0] - cg[0], mid[1] - cg[1]
        ln = math.hypot(vx, vy) or 1.0
        return vx / ln, vy / ln

    def emid(p, q):
        return ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2)

    # six crown facets, each valued by the unit normal of its OUTER edge
    head_l = [A, pT, pL, Lshoulder]
    head_r = [A, Rshoulder, pR, pT]
    belly_r = [Rshoulder, BR, pB, pR]
    belly_l = [Lshoulder, pL, pB, BL]
    tip = [BL, BR, pB]

    pygame.draw.polygon(surf, shade(*norm(emid(A, Lshoulder))), head_l)
    pygame.draw.polygon(surf, shade(*norm(emid(A, Rshoulder))), head_r)
    pygame.draw.polygon(surf, shade(*norm(emid(Rshoulder, BR))), belly_r)
    pygame.draw.polygon(surf, shade(*norm(emid(Lshoulder, BL))), belly_l)
    pygame.draw.polygon(surf, shade(0.0, 1.0), tip)      # faces straight down
    pygame.draw.polygon(surf, t_table, [pT, pR, pB, pL])

    # facet seams
    sw = max(1, sc.m(0.4))
    for a, b in ((A, pT), (Lshoulder, pL), (Rshoulder, pR),
                 (BL, pB), (BR, pB)):
        pygame.draw.line(surf, (*t_key, 190), a, b, sw)

    # crisp rim — the blunt bottom flat keeps the outline from a fragile 1-px
    # apex at the point.
    rim = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    pygame.draw.polygon(rim, (*lerp_color(base, WHITE, 0.4), 255),
                        [A, Rshoulder, BR, BL, Lshoulder], max(1, sc.m(0.5)))
    surf.blit(rim, (0, 0))

    # DUAL specular in the round-head zone (additive)
    lx = int(r * 0.14)
    ly = int(r * 0.10)
    lens = pygame.Surface((lx * 2 + 2, ly * 2 + 2), pygame.SRCALPHA)
    pygame.draw.ellipse(lens, (255, 255, 255, int(200 * gf)),
                        (1, 1, lx * 2, ly * 2))
    surf.blit(lens, (cx - int(r * 0.30) - lx - 1, cg[1] - int(r * 0.30) - ly - 1),
              special_flags=pygame.BLEND_ADD)
    pr = max(1, int(r * 0.08))
    pip = pygame.Surface((pr * 2 + 2, pr * 2 + 2), pygame.SRCALPHA)
    pygame.draw.circle(pip, (255, 255, 255, 255), (pr + 1, pr + 1), pr)
    surf.blit(pip, (cx - int(r * 0.40) - pr - 1, cg[1] - int(r * 0.40) - pr - 1),
              special_flags=pygame.BLEND_ADD)


sc.facet_gem = my_facet_gem   # monkey-patch before any draw_card call


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
    out_dir = "/home/user/skybit/docs/store_card_v5_gem_badge_r2/pear-cut"
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
    gz = render_gem((0, 0, 0), (0, 0, 0)).get_size()[0] * zoom
    label_h = 24
    row2_y = row1_y + chh + gap * 2
    row2_w = gz * 4 + gap * 3

    canvas_w = pad * 2 + max(row1_w, row2_w)
    canvas_h = row2_y + gz + label_h + pad

    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill((8, 8, 20))

    hf = hud_font(26)
    lf = hud_font(18)

    header = hf.render("gem badge — pear-cut r1", True, (236, 232, 250))
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


if __name__ == "__main__":
    main()
