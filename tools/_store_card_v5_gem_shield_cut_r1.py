"""Round-1 render sheet for the shield-cut gem badge concept.

Monkey-patches store_cards.facet_gem with a D-shaped 7-facet "shield-cut"
stone (flat top edge, domed bottom) and renders it both in-context on two
full v5 cards and as an 8x zoomed 4-tier gem strip. Review-only tooling —
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
CARD_W = sc.CARD_W * sc.SS   # 324
GEM_R  = sc.m(sc.GEM_R + 3)  # 22 device px


def _lum(c):
    # Rec. 601 luma — a cheap tier-brightness heuristic driving glow strength.
    return (0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]) / 255.0


def my_facet_gem(surf, cx, cy, r, base, deep, mystery=False):
    """Shield-cut: a D-shaped stone — flat top edge, domed bottom — cut into
    7 facets. The flat top (three trapezoids under a bright table) is the
    distinctive read; four alternating triangles fan down into the dome. The
    flat top anchors cleanly into the card corner with no fragile apex."""
    if mystery:
        base = (206, 60, 60)          # mystery owns red so it claims NO tier
        deep = (96, 18, 24)

    hi = lerp_color(base, WHITE, 0.5)
    mid = base
    lo = lerp_color(base, deep, 0.6)
    dark = lerp_color(deep, NEAR_BLACK, 0.4)
    # Legendary/bright hues carry a slightly hotter aura than muddy low tiers.
    gf = 0.55 + 0.45 * _lum(base)

    top_y = cy - int(0.7 * r)
    mid_y = cy - int(0.2 * r)
    hub = (cx, cy + int(0.15 * r))
    bottom_y = cy + int(0.3 * r)
    left_x = cx - r
    right_x = cx + r

    # --- Layer 0: additive glow bloom ---
    gr = int(r * 1.1)
    glow = pygame.Surface((gr * 2 + 2, gr * 2 + 2), pygame.SRCALPHA)
    gc = gr + 1
    for i in range(gr, 0, -1):
        a = int(58 * gf * (1 - i / gr))
        if a > 0:
            pygame.draw.circle(glow, (*base, a), (gc, gc), i)
    surf.blit(glow, (cx - gc, cy - gc), special_flags=pygame.BLEND_ADD)

    # --- Layer 1: D-silhouette body (flat top, domed bottom) ---
    body = [(left_x, top_y), (right_x, top_y)]
    steps = 16
    # Semicircle-ish dome: sweep the lower arc from top-right, through the
    # bottom, back to top-left. Parametrised on an ellipse whose top sits at
    # top_y and whose bottom reaches bottom_y.
    arc_cy = top_y
    arc_ry = bottom_y - top_y
    for k in range(steps + 1):
        ang = math.pi * (k / steps)          # 0 -> pi, right side to left side
        bx = cx + r * math.cos(ang)
        by = arc_cy + arc_ry * math.sin(ang)
        body.append((bx, by))
    pygame.draw.polygon(surf, lo, body)

    # --- Layer 2: three upper trapezoids across the flat-top band ---
    third = (right_x - left_x) / 3.0
    tl = lerp_color(mid, hi, 0.35)
    tc = lerp_color(mid, hi, 0.5)
    tr = lerp_color(mid, hi, 0.35)
    for i, col in enumerate((tl, tc, tr)):
        x0 = left_x + third * i
        x1 = left_x + third * (i + 1)
        pygame.draw.polygon(surf, col, [
            (x0, top_y), (x1, top_y), (x1, mid_y), (x0, mid_y)])

    # --- Layer 3: four lower radiating triangles converging on the hub ---
    seam_pts = [(left_x + (right_x - left_x) * (j / 4.0), mid_y) for j in range(5)]
    t_lite = lerp_color(mid, dark, 0.4)
    t_dark = lerp_color(mid, dark, 0.7)
    for j in range(4):
        col = t_lite if j % 2 == 0 else t_dark
        pygame.draw.polygon(surf, col, [seam_pts[j], seam_pts[j + 1], hub])

    # --- Layer 4: bright table rounded rect at top-centre ---
    tw = max(int(0.4 * r), 6)
    th = max(int(0.3 * r), 4)
    trect = pygame.Rect(0, 0, tw, th)
    trect.center = (cx, cy - int(0.5 * r))
    pygame.draw.rect(surf, hi, trect, border_radius=max(1, sc.m(1)))

    # --- Layer 5: seam strokes + silhouette outline ---
    sw = max(1, sc.m(0.8))
    for j in range(1, 4):                     # trapezoid vertical seams
        x = left_x + third * j
        pygame.draw.line(surf, dark, (x, top_y), (x, mid_y), sw)
    pygame.draw.line(surf, dark, (left_x, mid_y), (right_x, mid_y), sw)
    for j in range(1, 4):                     # triangle seams to the hub
        pygame.draw.line(surf, dark, seam_pts[j], hub, sw)
    pygame.draw.polygon(surf, dark, body, max(1, sc.m(1)))

    # --- Layer 6: flat-top white highlight edge ---
    hlt = pygame.Surface((surf.get_width(), surf.get_height()), pygame.SRCALPHA)
    hrect = pygame.Rect(left_x, top_y, right_x - left_x, max(1, sc.m(1)))
    pygame.draw.rect(hlt, (*WHITE, int(120 * gf)), hrect)
    surf.blit(hlt, (0, 0))

    # T4 legendary: a hot additive glint on the table
    if _lum(base) > 0.7:
        gsz = max(2, int(0.16 * r))
        glint = pygame.Surface((gsz * 2, gsz * 2), pygame.SRCALPHA)
        pygame.draw.circle(glint, (255, 255, 255, 230), (gsz, gsz), gsz)
        surf.blit(glint, (cx - gsz - int(0.12 * r), cy - int(0.5 * r) - gsz),
                  special_flags=pygame.BLEND_ADD)


sc.facet_gem = my_facet_gem   # monkey-patch before any draw_card call


def render_card(sid):
    ch = sc.CARD_H * sc.SS
    surf = pygame.Surface((CARD_W, ch + 16), pygame.SRCALPHA)
    rect = pygame.Rect(sc.m(sc._INSET), sc.m(sc._INSET),
                       CARD_W - 2 * sc.m(sc._INSET), ch - 2 * sc.m(sc._INSET))
    sc.draw_card(surf, sid, rect, False, False, sc.PRICE_VARIANT)
    return surf


def render_gem(base, deep):
    m = GEM_R + 4
    surf = pygame.Surface((m * 2, m * 2), pygame.SRCALPHA)
    my_facet_gem(surf, m, m, GEM_R, base, deep)
    return surf


def main():
    out_dir = "/home/user/skybit/docs/store_card_v5_gem_badge/shield-cut"
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "round_1.png")

    pad = 24
    gap = 24
    header_h = 40

    cards = [render_card(SID_PRIMARY), render_card(SID_SECONDARY)]
    cw, chh = cards[0].get_size()
    row1_w = cw * 2 + gap
    row1_y = header_h + pad

    zoom = 8
    gem_src = render_gem((0, 0, 0), (0, 0, 0)).get_size()[0]  # size probe
    gz = gem_src * zoom
    label_h = 24
    row2_y = row1_y + chh + gap * 2
    row2_w = gz * 4 + gap * 3

    canvas_w = pad * 2 + max(row1_w, row2_w)
    canvas_h = row2_y + gz + label_h + pad

    canvas = pygame.Surface((canvas_w, canvas_h))
    canvas.fill((8, 8, 20))

    hf = hud_font(26)
    lf = hud_font(18)

    header = hf.render("gem badge — shield-cut r1", True, (236, 232, 250))
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
